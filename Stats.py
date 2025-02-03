"""Statistics calculation from the events DataFrame"""
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
import pandas as pd

# local imports
import Config



# Utility: returns the number of rows for an event in a DataFrame
def count(df, event_name):
    return df[df['event_name']==event_name].shape[0]


# Utility: returns the number of rows for an event in a DataFrame for a player
def countforplayer(df, player_name, event_name):
    return df[(df['team']==Config.TEAM)&(df['player']==player_name)&(df['event_name']==event_name)].shape[0]

# Utility: returns the number of rows for an event in a DataFrame for the Team
def countforteam(df, event_name):
    return df[(df['team']==Config.TEAM)&(df['event_name']==event_name)].shape[0]


###########################################################################################################################################################################
# Number of points scored by a player or by a team
###########################################################################################################################################################################
def points(events_df,          # Events DataFrame
           player_name=None,   # Name of the player (or None for team totals)
           team=Config.TEAM):  # TEAM or OPPO
    
    if events_df is None: return 0

    if player_name is None: df = events_df[(events_df['team']==team)]
    else:                   df = events_df[(events_df['team']==team)&(events_df['player']==player_name)]
    
    T1ok = count(df,'T1ok')
    T2ok = count(df,'T2ok')
    T3ok = count(df,'T3ok')
    return T1ok + T2ok*2 + T3ok*3
    

###########################################################################################################################################################################
# Number of fouls committed by a player
###########################################################################################################################################################################
def fouls(events_df,           # Events DataFrame
           player_name=None,   # Name of the player (or None for team totals)
           team=Config.TEAM):  # TEAM or OPPO
    
    if events_df is None: return 0

    if player_name is None: df = events_df[(events_df['team']==team)]
    else:                   df = events_df[(events_df['team']==team)&(events_df['player']==player_name)]
    
    return count(df,'FCom')
    
    
###########################################################################################################################################################################
# Evaluation of a player: (TL+) - (TL-) + [(T2+) x 2 - (T2-)] + [(T3+) x 3) - (T3-)] + PR - PP + RO + RD + AS - FF + FS + SD - SS
###########################################################################################################################################################################
def value(events_df,           # Events DataFrame
          player_name=None):   # Name of the Team player (or None for Team totals)
    
    if events_df is None: return 0

    if player_name is None: df = events_df[(events_df['team']==Config.TEAM)]
    else:                   df = events_df[(events_df['team']==Config.TEAM)&(events_df['player']==player_name)]
    
    return count(df,'T1ok') - count(df,'T1err') + 2*count(df,'T2ok') - count(df,'T2err') + 3*count(df,'T3ok') - count(df,'T3err') + \
           count(df,'PRec') - count(df,'PPer') + count(df,'ROff') + count(df,'RDif') + count(df,'Ass') - count(df,'FCom') + count(df,'FSub') + count(df,'SDat') - count(df,'SSub')

    
###########################################################################################################################################################################
# OER of a player: Offensive Efficency Rating  = Points scored / Possessions      with Possessions = T2 + T3 + (T1/2) + PP
###########################################################################################################################################################################
def oer(events_df,           # Events DataFrame
        player_name=None):   # Name of the Team player (or None for Team totals)
    
    if events_df is None: return 0.0

    if player_name is None: df = events_df[(events_df['team']==Config.TEAM)]
    else:                   df = events_df[(events_df['team']==Config.TEAM)&(events_df['player']==player_name)]
    
    T1ok  = count(df,'T1ok')
    T1err = count(df,'T1err')
    T2ok  = count(df,'T2ok')
    T2err = count(df,'T2err')
    T3ok  = count(df,'T3ok')
    T3err = count(df,'T3err')
    T1 = T1ok + T1err
    T2 = T2ok + T2err
    T3 = T3ok + T3err
    PP = count(df,'PPer')
    if T1+T2+T3+PP == 0: return 0.0
    return (count(df,'T1ok') + 2*count(df,'T2ok') + 3*count(df,'T3ok')) / (T2 + T3 + 0.5*T1 + PP)
    
    
###########################################################################################################################################################################
# VIR of a player: Value Index Rating = [(Punti fatti + AS x 1,5 + PR + SD x 0,75 + RO x 1,25 + RD x 0,75 + T3+/2 + FS/2 - FF/2 - ((T3-) + (T2-)) x 0,75 - PP - (TL-)/2) / Minuti giocati]
###########################################################################################################################################################################
def vir(events_df,           # Events DataFrame
        player_name=None,    # Name of the Team player (or None for Team totals)
        players_info=None):  # game.player_info (to read the 'time_on_field' of each player)
    
    if events_df is None: return 0.0

    if player_name is None:
        minutes = 0.0
        for player_name in players_info.keys():
            minutes += players_info[player_name]['time_on_field'] / 60.0
        df = events_df[(events_df['team']==Config.TEAM)]
    else:
        minutes = players_info[player_name]['time_on_field'] / 60.0
        df = events_df[(events_df['team']==Config.TEAM)&(events_df['player']==player_name)]
        
    if minutes <= 0.0: return 0.0
    T1ok  = count(df,'T1ok')
    T1err = count(df,'T1err')
    T2ok  = count(df,'T2ok')
    T2err = count(df,'T2err')
    T3ok  = count(df,'T3ok')
    T3err = count(df,'T3err')
    T1 = T1ok + T1err
    T2 = T2ok + T2err
    T3 = T3ok + T3err
    P = T1ok + 2*T2ok + 3*T3ok
    return (P + 1.5*count(df,'Ass') + count(df,'PRec') + 0.75*count(df,'SDat') + 1.25*count(df,'ROff') + 0.75*count(df,'RDif') + 0.5*T3ok + 0.5*count(df,'FSub') + 0.5*count(df,'FCom') + \
            0.75*(T3err + T2err) - count(df,'PPer') - 0.5*T1err) / minutes
    
    
###########################################################################################################################################################################
# PlusMinus of a player: + Punti segnati dalla squadra - Punti segnati dagli avversari quando il giocatore e' in campo
###########################################################################################################################################################################
def plusminus(player_name=None,   # Name of the Team player (or None for Team totals)
              players_info=None): # game.player_info (to read the 'plusminus' of each player)
    
    if player_name is None:
        pm = 0
        for player_name in players_info.keys():
            pm += players_info[player_name]['plusminus']
        return pm
    else:
        if player_name not in players_info: return 0
        return players_info[player_name]['plusminus']
    
    
###########################################################################################################################################################################
# True Shooting Percentage of a player: (see: https://en.wikipedia.org/wiki/True_shooting_percentage): Points / 2*(T2 + T3 + 0.44*T1)
###########################################################################################################################################################################
def trueshooting(events_df,           # Events DataFrame
                 player_name=None):   # Name of the Team player (or None for Team totals)
    
    if events_df is None: return 0.0

    if player_name is None: df = events_df[(events_df['team']==Config.TEAM)]
    else:                   df = events_df[(events_df['team']==Config.TEAM)&(events_df['player']==player_name)]
    
    T1ok  = count(df,'T1ok')
    T1err = count(df,'T1err')
    T2ok  = count(df,'T2ok')
    T2err = count(df,'T2err')
    T3ok  = count(df,'T3ok')
    T3err = count(df,'T3err')
    T1 = T1ok + T1err
    T2 = T2ok + T2err
    T3 = T3ok + T3err
    if T1+T2+T3 == 0: return 0.0
    P = T1ok + 2*T2ok + 3*T3ok
    return 100.0 * (0.5*P / (T2 + T3 + 0.44*T1))
    
    
###########################################################################################################################################################################
# Utility functions for the BoxScore 
###########################################################################################################################################################################
    
###########################################################################################################################################################################
# Throw stats + percentage. Returns two strings, f.i., '1/3' '33%'
###########################################################################################################################################################################
def tperc(events_df,          # Events DataFrame
          player_name=None,   # Name of the Team player (or None for Team totals)
          throw=2):           # 0=2 or 3 points throw ,  1=free throws,  2=2 points throws,    3=3 points throws

    if events_df is None: return '', ''
    
    if player_name is None: df = events_df[(events_df['team']==Config.TEAM)]
    else:                   df = events_df[(events_df['team']==Config.TEAM)&(events_df['player']==player_name)]
    
    if throw == 0:
        ok  = count(df,'T2ok')
        err = count(df,'T2err')
        ok  += count(df,'T3ok')
        err += count(df,'T3err')
    else:
        ok  = count(df,'T%dok'%throw)
        err = count(df,'T%derr'%throw)
    
    tot = ok+err 
        
    if tot > 0:
        return '%d/%d'%(ok,tot), '%.0f%%'%(100.0*(ok/tot))
    else:
        return '', ''
    