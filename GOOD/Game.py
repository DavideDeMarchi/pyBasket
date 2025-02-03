"""Game info, players and opponents selection"""
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
from ipywidgets import widgets, HTML, Layout
import ipyvuetify as v
from PIL import Image
import pandas as pd
import json

# vois imports
from vois import colors
from vois.vuetify import dialogGeneric

# local imports
import Config
import Stats


###########################################################################################################################################################################
# Game class
###########################################################################################################################################################################
class Game():
    
    def __init__(self,
                 board,        # Instance of ScoreBoard class
                 team_file,    # Path of the input Team file
                 game_file):   # Path of the input Game file
        
        self.board = board     # Reference to the overall board
        self.events_df = None  # Pandas DataFrame storing the events
        
        self.team_logo_img = None
        
        # Read team data
        with open(team_file) as f:
            self.team_data = json.load(f)
            self.players_info = self.team_data['players']

            if 'logo' in self.team_data:
                self.team_logo_img = Image.open('./images/%s'%self.team_data['logo'])
            
            # Add 'time_on_field' to all players (if not already present)
            for name,player in self.players_info.items():
                if 'time_on_field' not in player:
                    player['time_on_field'] = 0.0
            
            # Add 'plusminus' to all players (if not already present)
            for name,player in self.players_info.items():
                if 'plusminus' not in player:
                    player['plusminus'] = 0
                    
            # Players sorted alphabetically by name
            self.players_by_name = sorted(self.players_info.keys())

            # Players sorted by number
            self.players_by_number = [x[0] for x in sorted([[x[1]['name'],x[1]['number']] for x in self.players_info.items()], key=lambda x: int(x[1]))]
            self.players_numbers   = [x[1] for x in sorted([[x[1]['name'],x[1]['number']] for x in self.players_info.items()], key=lambda x: int(x[1]))]

   
        # Read game data
        self.game_file = game_file
        with open(self.game_file) as f:
            self.game_data = json.load(f)
            self.opponents_info = self.game_data['opponents_info']
            
            # Add players_info to game_data (if not already present)
            if 'players_info' in self.game_data:
                self.players_info = self.game_data['players_info']
            else:
                self.game_data['players_info'] = self.players_info
                
            
            # Add 'fouls' and 'points' to opponents players (if not already present)
            for name,player in self.opponents_info.items():
                if 'fouls' not in player:
                    player['fouls'] = 0
                if 'points' not in player:
                    player['points'] = 0

            # Opponents sorted alphabetically by name
            self.opponents_by_name = sorted(self.opponents_info.keys())

            # Opponents sorted by number
            self.opponents_by_number = [x[0] for x in sorted([[x[1]['name'],x[1]['number']] for x in self.opponents_info.items()], key=lambda x: int(x[1]))]
            
            # Read events from the game
            if 'events' in self.game_data:
                self.events_df = pd.DataFrame.from_records(self.game_data['events'])


        # Initialize other members of the overall board
        self.board.home_game = self.game_data['home']
        if self.board.home_game:
            self.board.team1_name = self.team_data['name']
            self.board.team1_abbr = self.team_data['abbreviation']
            self.board.team2_name = self.game_data['opponents']
            self.board.team2_abbr = self.game_data['abbreviation']
        else:
            self.board.team1_name = self.game_data['opponents']
            self.board.team1_abbr = self.game_data['abbreviation']
            self.board.team2_name = self.team_data['name']
            self.board.team2_abbr = self.team_data['abbreviation']
            
        if 'on_field' in self.game_data:
            self.on_field = self.game_data['on_field']
        else:
            self.on_field = ['']*5

            
    
    # Set the status of the overall board (quarter, seconds, points, fouls, timeouts, ...)
    def setBoardStatus(self):
        if 'status' in self.game_data:
            status = self.game_data['status']
            self.board.quarter    = status['quarter']
            self.board.tb.seconds = status['seconds']
            self.board.pb1.points = status['points1']
            self.board.pb2.points = status['points2']
            self.board.fb1.fouls  = status['fouls1']
            self.board.fb2.fouls  = status['fouls2']
            self.board.timeouts1  = status['timeouts1']
            self.board.timeouts2  = status['timeouts2']
        
        
    ###########################################################################################################################################################################
    # Display info on top of throwmap background: points per quarter. Returns an array of strings
    ###########################################################################################################################################################################
    def pointsPerQuarter(self):
        
        def qpoints(quarter):
            if quarter <= 4: name = 'Q%d'%quarter
            else:            name = 'S%d'%(quarter-4)
        
            df = self.events_df[self.events_df['quarter']==quarter]
            dfteam = df[df['team']==Config.TEAM]
            dfoppo = df[df['team']==Config.OPPO]
            
            T1ok = Stats.count(dfteam,'T1ok')
            T2ok = Stats.count(dfteam,'T2ok')
            T3ok = Stats.count(dfteam,'T3ok')
            pTeam = T1ok + T2ok*2 + T3ok*3
            
            T1ok = Stats.count(dfoppo,'T1ok')
            T2ok = Stats.count(dfoppo,'T2ok')
            T3ok = Stats.count(dfoppo,'T3ok')
            pOppo = T1ok + T2ok*2 + T3ok*3

            if self.board.home_game:
                return '%s: %d - %d'%(name,pTeam,pOppo)
            else:
                return '%s: %d - %d'%(name,pOppo,pTeam)
                    
        
        quarters = list(self.events_df['quarter'].unique())
        return [qpoints(x) for x in quarters]
        
        
    ###########################################################################################################################################################################
    # Display info on top of player image
    ###########################################################################################################################################################################

    # Returns a string displaying the field time of the player
    def playerFieldTime(self, player_name):
        if player_name in self.players_info:
            seconds = self.players_info[player_name]['time_on_field']
            return '  T: %d\'%02d"'%(seconds//60, int(seconds%60))
        else:
            return '  T: 0\'0"'
        
    # Returns a string displaying the points scored by a player
    def playerPointScored(self, player_name):
        return '  P: %d'%Stats.points(self.events_df, player_name)
        
    # Returns a string displaying the evaluation of a player
    def playerValue(self, player_name):
        return '  VAL: %d'%Stats.value(self.events_df, player_name)
    
    # Returns a string displaying the OER of a player
    def playerOER(self, player_name):
        return '  OER: %.2f'%Stats.oer(self.events_df, player_name)
    
    # Returns a string displaying the VIR of a player
    def playerVIR(self, player_name):
        return '  VIR: %.2f'%Stats.vir(self.events_df, player_name, self.players_info)
    
    # Returns a string displaying the plusminus of a player
    def playerPlusMinus(self, player_name):
        return '  +/-: %d'%Stats.plusminus(player_name, self.players_info)
    
    # Returns a string displaying the True Shooting Percentage of a player
    def playerTrueShooting(self, player_name):
        return '  TS: %.0f%%'%Stats.trueshooting(self.events_df, player_name)
    
    # Retrieve string for the current additional info on a player image
    def playerInfo(self, player_name):
        if self.board.showOverImage == 'T':
            return self.playerFieldTime(player_name)
        elif self.board.showOverImage == 'P':
            return self.playerPointScored(player_name)
        elif self.board.showOverImage == 'V':
            return self.playerValue(player_name)
        elif self.board.showOverImage == 'O':
            return self.playerOER(player_name)
        elif self.board.showOverImage == 'I':
            return self.playerVIR(player_name)
        elif self.board.showOverImage == 'M':
            return self.playerPlusMinus(player_name)
        elif self.board.showOverImage == 'S':
            return self.playerTrueShooting(player_name)
        else:
            return ''

        
    # Display current additional info over a player image
    def playerDisplayInfo(self, player_name):
        if player_name is not None and len(player_name) > 0 and player_name in self.on_field:
            position = self.on_field.index(player_name)
            c = self.board.players_card[position]
            c.children[2].children[0].children = ['#' + self.players_info[player_name]['number'] + self.playerInfo(player_name)]
            
    # Display current additional info over all the players on the field
    def playerDisplayInfoAll(self):
        for position,player_name in enumerate(self.on_field):
            if player_name is not None and len(player_name) > 0:
                c = self.board.players_card[position]
                c.children[2].children[0].children = ['#' + self.players_info[player_name]['number'] + self.playerInfo(player_name)]
            
            
    ###########################################################################################################################################################################
    # Save game to file
    ###########################################################################################################################################################################
    def saveGame(self, game_file=None):
        
        if isinstance(game_file, str):
            self.game_file = game_file
            
        with open(self.game_file, 'w') as file:
            
            # Save game status read from the overall board
            self.game_data['status'] = {
                'quarter':   self.board.quarter,
                'seconds':   self.board.tb.seconds,
                'points1':   self.board.pb1.points,
                'points2':   self.board.pb2.points,
                'fouls1':    self.board.fb1.fouls,
                'fouls2':    self.board.fb2.fouls,
                'timeouts1': self.board.timeouts1,
                'timeouts2': self.board.timeouts2
            }
            
            if self.events_df is not None:
                sss = self.events_df.to_json(orient='records', lines=True).split('\n')
                self.game_data['events'] = [json.loads(x) for x in sss if len(x) > 4]
            else:
                del self.game_data['events']
                
            file.write(json.dumps(self.game_data, indent=4, sort_keys=False))
            
            
    ###########################################################################################################################################################################
    # Management of players
    ###########################################################################################################################################################################

    # Return a list of widgets for the players
    def playersList(self, list_of_players, onclick=None, single_line=True):

        players_widgets = []
        players_card    = []

        w = 'calc(%fvw - 4px)'%(self.board.width/5)
        spacer = v.Html(tag='div',children=[' '], style_='width: 5px; height: %s; background-color: %s;'%(w, self.board.tb.color_back))
        style_text = 'color: white; text-shadow: 2px 2px black; background-color: #00000000; font-size: %fvh; line-height: %fvh; font-family: "%s", serif; vertical-align: baseline;'%(self.board.text_height*0.25, 
                                                                                                                                                                                       self.board.theight*0.25,
                                                                                                                                                                                       self.board.font_name)

        style_text_small = 'color: white; text-shadow: 2px 2px black; background-color: #00000000; font-size: %fvh; line-height: %fvh; font-family: "%s", serif; vertical-align: baseline;'%(self.board.text_height*0.2, 
                                                                                                                                                                                             self.board.theight*0.2,
                                                                                                                                                                                             self.board.font_name)
        
        for index,player_name in enumerate(list_of_players):
            if player_name is not None and len(player_name) > 0:
                title   = v.Html(tag='div',children=[player_name], style_='text-align: center; %s'%style_text)
                info = self.playerInfo(player_name)
                number  = v.Html(tag='div',children=['#' + self.players_info[player_name]['number'] + info], style_='text-align: center; %s'%style_text_small)
            else:
                title  = v.Html(tag='div',children=[''], style_='text-align: center; %s'%style_text)
                number = v.Html(tag='div',children=[''], style_='text-align: center; %s'%style_text_small)

            action = v.CardActions(children=[number], class_='justify-center')

            c = v.Card(tile=True, color='#222222', children=[title, v.Spacer(), action], outlined=False, elevation=0, width=w, height=w,
                       class_='noselect d-flex flex-column', style_='overflow: hidden; border-width:6px; border-color: yellow;')

            if player_name is not None and player_name != '':
                img = Image.open('./images/%s.jpg'%player_name)
                iw,ih = img.size
                img = img.crop((0, 0, iw, iw))
                c.img = colors.image2Base64(img)

            c.id = index
            if onclick is not None:
                c.on_event('click', onclick)

            players_card.append(c)
            players_widgets.append(c)
            if index < len(list_of_players)-1: players_widgets.append(spacer)

        if single_line or len(players_card) <= 5:
            return widgets.HBox(players_widgets), players_card
        else:
            n = len(players_card)*2 - 1
            if len(players_card)%2 == 0:
                nfirstline = n//2
                return widgets.VBox([widgets.HBox(players_widgets[:nfirstline]), widgets.HBox(players_widgets[nfirstline+1:])]), players_card
            else:
                nfirstline = n//2 + 1
                return widgets.VBox([widgets.HBox(players_widgets[:nfirstline]), widgets.HBox(players_widgets[nfirstline+1:])]), players_card

        
    # Players goes to the field
    def playerToField(self, player_name, position=0):
        if player_name not in self.on_field:
            if position >=0 and position < len(self.board.players_card):
                c = self.board.players_card[position]

                if player_name is None or player_name == '':
                    c.children[0].children = ['']
                    c.children[2].children[0].children = ['']
                    c.img = None
                    self.on_field[position] = ''
                else:
                    c.children[0].children = [player_name]
                    c.children[2].children[0].children = ['#' + self.players_info[player_name]['number'] + self.playerInfo(player_name)]
                    self.on_field[position] = player_name

                    img = Image.open('./images/%s.jpg'%player_name)
                    iw,ih = img.size
                    img = img.crop((0, 0, iw, iw))
                    c.img = colors.image2Base64(img)

                self.board.click_on_player(c, None, None)


    # Players goes to the bench
    def playerToBench(self, player_name):
        if player_name in self.on_field:
            position = self.on_field.index(player_name)
            c = self.board.players_card[position]
            c.children[0].children = ['']
            c.children[2].children[0].children = ['']
            c.img = None
            self.on_field[position] = ''
            c.outlined = False
            self.board.click_on_player(c, None, None)


    # Selection of one of the players on the bench
    def selectFromBench(self, onselect):

        dlg = None

        def doSelect(widget, event, data):
            player_name = bc[widget.id].children[0].children[0]
            dlg.close()
            onselect(player_name)

        bw, bc = self.playersList(self.board.bench, onclick=doSelect, single_line=False)

        if len(bc) >= 6:
            w = (len(bc)//2) * (self.board.width/5)
        else:
            w = len(bc) * (self.board.width/5)

        dlg = dialogGeneric.dialogGeneric(title='Select player', text='', titleheight=30,
                                          show=True, addclosebuttons=False, width='calc(%fvw - 4px)'%w,
                                          fullscreen=False, content=[bw], output=self.board.output)


    ###########################################################################################################################################################################
    # Management of opponents
    ###########################################################################################################################################################################

    # Return a list of widgets for the opponents
    def opponentsList(self, onclick=None, single_line=True, opponents_list=None):
        
        if opponents_list is None:
            opponents_list = self.opponents_by_number

        players_widgets = []
        players_card    = []

        w = 'calc(%fvw - 4px)'%(self.board.width/5)
        spacer = v.Html(tag='div',children=[' '], style_='width: 5px; height: %s; background-color: %s;'%(w,self.board.tb.color_back))
        style_text = 'text-shadow: 2px 2px black; background-color: #00000000; font-size: %fvh; line-height: %fvh; font-family: "%s", serif; vertical-align: baseline;'%(self.board.text_height*0.25,
                                                                                                                                                                         self.board.theight*0.25,
                                                                                                                                                                         self.board.font_name)
        style_text_white = 'color: white; %s'%style_text
        style_text_green = 'color: green; %s'%style_text
        style_text_red   = 'color: red; %s'%style_text

        # Sort the list by increasing shirt number
        opponents_list = [x[0] for x in sorted([(x,y) for x,y in zip(opponents_list,[self.opponents_info[x]['number'] for x in opponents_list])], key=lambda x: int(x[1]))]

        for index,player_name in enumerate(opponents_list):
            title  = v.Html(tag='div',children=[player_name], class_='mt-2', style_='text-align: center; %s'%style_text_white)
            number = v.Html(tag='div',children=['#' + self.opponents_info[player_name]['number'] + '  ' + str(self.opponents_info[player_name]['year'])], style_='text-align: center; %s'%style_text_white)

            if self.opponents_info[player_name]['points'] > 0: points = v.Html(tag='div',children=['%d P'%self.opponents_info[player_name]['points']], style_='text-align: center; color: green; %s'%style_text_green)
            else:                                              points = ''

            if self.opponents_info[player_name]['fouls'] > 0:  fouls  = v.Html(tag='div',children=['%d F'%self.opponents_info[player_name]['fouls']],  style_='text-align: center; color: red;   %s'%style_text_red)
            else:                                              fouls = ''

            action = v.CardActions(children=[number], class_='justify-center')

            c = v.Card(tile=True, color='#222222', children=[title, v.Spacer(), points, v.Spacer(), fouls, v.Spacer(), action],
                       outlined=False, elevation=0, width=w, height=w, class_='noselect d-flex flex-column', style_='overflow: hidden; border-width:6px; border-color: yellow;')

            c.id = index
            if onclick is not None:
                c.on_event('click', onclick)

            players_card.append(c)
            players_widgets.append(c)
            if index < len(opponents_list)-1: players_widgets.append(spacer)

        if single_line or len(players_card) <= 5:
            return widgets.HBox(players_widgets), players_card
        else:
            spacerV = v.Card(flat=True, tile=True, color=self.board.tb.color_back, width='%fvw'%self.board.width, height='5px')

            n = len(players_card)*2 - 1
            if len(players_card)%2 == 0:
                nfirstline = n//2
                return widgets.VBox([widgets.HBox(players_widgets[:nfirstline]), spacerV, widgets.HBox(players_widgets[nfirstline+1:])]), players_card
            else:
                nfirstline = n//2 + 1
                return widgets.VBox([widgets.HBox(players_widgets[:nfirstline]), spacerV, widgets.HBox(players_widgets[nfirstline+1:])]), players_card


    # Add points to an opponent player
    def opponentAddPoints(self, opponent_name, points):
        self.opponents_info[opponent_name]['points'] += points

    # Remove points to an opponent player
    def opponentRemovePoints(self, opponent_name, points):
        self.opponents_info[opponent_name]['points'] -= points


    # Add a foul to an opponent player
    def opponentAddFoul(self, opponent_name):
        self.opponents_info[opponent_name]['fouls'] += 1

    # Remove a foul to an opponent player
    def opponentRemoveFoul(self, opponent_name):
        self.opponents_info[opponent_name]['fouls'] -= 1


    # Selection of one of the opponents
    def selectOpponent(self, onselect, opponents_list=None):
        
        if opponents_list is None:
            opponents_list = self.opponents_by_number

        dlg = None

        def doSelect(widget, event, data):
            player_name = bc[widget.id].children[0].children[0]
            dlg.close()
            onselect(player_name)

        bw, bc = self.opponentsList(onclick=doSelect, single_line=False, opponents_list=opponents_list)

        if len(bc) >= 6:
            w = (len(bc)//2) * (self.board.width/5)
        else:
            w = len(bc) * (self.board.width/5)

        dlg = dialogGeneric.dialogGeneric(title='Select opponent', text='', titleheight=30,
                                          show=True, addclosebuttons=True, width='calc(%fvw - 4px)'%w,
                                          fullscreen=False, content=[bw], output=self.board.output)
    