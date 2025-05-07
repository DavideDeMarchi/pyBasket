"""
Data analytics
"""
# Author(s): Davide.De-Marchi@ec.europa.eu
# Copyright © European Union 2024-2025
# 
# Licensed under the EUPL, Version 1.2 or as soon they will be approved by 
# the European Commission subsequent versions of the EUPL (the "Licence");
# 
# You may not use this work except in compliance with the Licence.
# 
# You may obtain a copy of the Licence at:
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12

# Unless required by applicable law or agreed to in writing, software
# distributed under the Licence is distributed on an "AS IS"
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.
# 
# See the Licence for the specific language governing permissions and
# limitations under the Licence.
import Config
import Stats
import Game
import ScoreBoard
import BoxScore
import ThrowMap

import importlib
importlib.reload(Config)
importlib.reload(Stats)
importlib.reload(Game)
importlib.reload(ScoreBoard)
importlib.reload(BoxScore)
importlib.reload(ThrowMap)

from ipywidgets import widgets, HTML

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import glob
import os
import json


###########################################################################################################################################################################
# Returns the Pandas DataFrame containing all the events of the team players for the entire season and the players_info dictionary
###########################################################################################################################################################################
def seasonEvents(output, folder='./data'):

    # Conversion to int without errors
    def toint(x):
        try:
            return int(x)
        except:
            return 999999
    
    allfiles = glob.glob('%s/*.game'%folder)
    
    allevents = []
    
    # Try to read phases from the team file
    teamfiles = glob.glob('%s/*.team'%folder)
    phases = []
    if len(teamfiles) == 0:
        print('No .team file found in %s folder'%folder)
        return
              
    team_file = teamfiles[0]
    with open(team_file) as f:
        team_data = json.load(f)
        if 'phases' in team_data:
            phases = team_data['phases']

    if len(phases) == 0:
        phases = sorted(list(set([os.path.basename(x).split('-')[1] for x in allfiles if '-' in x and '.a-' in x])))
    
    sb = ScoreBoard.ScoreBoard(team_file, scale=0.4, output=output)

    players_info = {}
    
    # Cycle on all games
    progressive = 1
    for phase in phases:

        # File of the phase
        files = [x for x in allfiles if phase in x and os.path.basename(x).split('-')[1] == phase]

        # Sort on increasing phase + round
        rounds = [toint(os.path.basename(x).split('.')[0]) for x in files]
        files  = [file for r, file in sorted(zip(rounds, files))]

        for file in files:
            sb.game.loadGame(file)
            g = sb.game.game_data

            pi = g['players_info']
            for player_name in pi:
                if player_name in players_info:
                    players_info[player_name]['time_on_field'] += pi[player_name]['time_on_field']
                    players_info[player_name]['plusminus']     += pi[player_name]['plusminus']
                    if pi[player_name]['time_on_field'] > 0:
                        players_info[player_name]['games'] += 1
                else:
                    players_info[player_name] = pi[player_name]
                    if pi[player_name]['time_on_field'] > 0:
                        players_info[player_name]['games'] = 1
                    else:
                        players_info[player_name]['games'] = 0
                
            # Append all events
            df = sb.game.events_df
            if df.shape[0] > 0:
                name = file.replace('./data/','').replace('.game','')
                elems = name.split('-')
                ro = int(elems[0].replace('.a',''))
                ph = elems[1]
                op = elems[2]
                df['game_number'] = progressive
                df['round'] = ro
                df['phase'] = ph
                df['opponents'] = op
                df['home'] = g['home']
                if g['home']:
                    df['win'] = g['status']['points1'] > g['status']['points2']
                else:
                    df['win'] = g['status']['points2'] > g['status']['points1']
                allevents.append(df)
                
            progressive += 1

    df = pd.concat(allevents)
    df.reset_index(drop=True, inplace=True)
    
    df = df[df['team']==Config.TEAM]
    df = df[~df['player'].isin([Config.TEAM,''])]

    return df, players_info


###########################################################################################################################################################################
# Returns a plotly figure with a scatter chart
###########################################################################################################################################################################
def scatterChart(players, x, y, players_info, descrx, descry, size_on_time=True, show_bisector=False, do_average=True):

    # Media per partita
    if do_average:
        x = [v/players_info[player]['games'] for v,player in zip(x,players)]
        y = [v/players_info[player]['games'] for v,player in zip(y,players)]

    # Players size depends on time on the field
    if size_on_time:
        sizes = [players_info[x]['time_on_field'] for x in players]
        comment = '(la dimensione dei cerchi è proporzionale al totale dei minuti in campo)'
    # Players size depends on the number of games played
    else:
        sizes = [players_info[x]['games'] for x in players]
        comment = '(la dimensione dei cerchi è proporzionale al numero di partite effettivamente disputate)'
    
    customdata = ['Partite giocate: %d<br>Minuti medi in campo: %.1f'%(players_info[x]['games'], (players_info[x]['time_on_field'])/(60.0*players_info[x]['games'])) for x in players]
        
    sizes  = [100*x/max(sizes) for x in sizes]
    colors = [px.colors.qualitative.Light24[players.index(x)] for x in players]

    #players, x, y, sizes, colors
    fig = go.Figure()

    if show_bisector:
        m = max(x+y)
        fig.add_trace(go.Scatter(x=[0,m], y=[0,m], mode='lines', marker=dict(color='rgb(127, 127, 127)'), line=dict(dash='dash')))

    fig.add_trace(go.Scatter(x=x, y=y, text=players, mode='markers+text', marker=dict(size=sizes, color=colors),
                             customdata=customdata, name='',
                             hovertemplate='<b>%%{text}</b><br>%s: %%{x:.1f}<br>%s: %%{y:.1f}<br>%%{customdata}'%(descrx,descry)))

    fig.update_layout(height=800, template='plotly_white', font_family='Arial', xaxis_title=descrx, yaxis_title=descry, showlegend=False,
                      margin=dict(l=70, r=20, b=30, t=70),
                      title=dict(text='<b>' + descrx + ' vs. ' + descry + '</b><br><span style="font-size: 15px;">' + comment + '</span>', font=dict(size=20, weight=700)))
    return fig
