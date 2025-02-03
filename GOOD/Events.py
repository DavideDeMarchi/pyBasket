"""Recording of player and opponents' events"""
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
import pandas as pd
import json

# vois imports
from vois.vuetify import settings, iconButton

# local imports
import Config
import ScoreBoard
import Game
import Stats


###########################################################################################################################################################################
# Events: display cards to insert player events
###########################################################################################################################################################################
class Events(widgets.HBox):
    
    def __init__(self, board):     # Instance of ScoreBoard
    
        super().__init__()
        
        # Store board
        self.board = board
        self.game  = self.board.game
        self.board.on_player_selected   = self.on_player_selected     # Be advised when the selected player changes
        self.board.on_opponents_points  = self.on_opponents_points    # Be advised when the opponents score 1,2,3 points
        self.board.on_team_timeout      = self.on_team_timeout        # When the team calls a timeout
        self.board.on_opponents_timeout = self.on_opponents_timeout   # When the opponents calls a timeout
        self.board.on_scaling           = self.on_scaling             # Called for scaling small/medium/large 
        
        # Cards for each of the event types
        self.event_card = { x: None for x in Config.EVENT_NAME.keys() }
        
        # CSS settings on the board.output
        with self.board.output:
            display(HTML('''
<style>
.noselect {
  -webkit-touch-callout: none; /* iOS Safari */
    -webkit-user-select: none; /* Safari */
     -khtml-user-select: none; /* Konqueror HTML */
       -moz-user-select: none; /* Old versions of Firefox */
        -ms-user-select: none; /* Internet Explorer/Edge */
            user-select: none; /* Non-prefixed version, currently
                                  supported by Chrome, Edge, Opera and Firefox */
}
</style>
'''))
            
        # List of player events
        if self.game.events_df is None:
            self.df = pd.DataFrame(columns=['team', 'player', 'event', 'event_name', 'event_description', 'quarter', 'seconds', 'x', 'y'])
             
            # Add reference to events dataframe to the players instance
            self.game.events_df = self.df
        else:
            self.df = self.game.events_df
        
        
        self.createControls()

        
    # Creation of the controls
    def createControls(self):

        # Two rows of cards to manage all types of events
        self.eventcards1 = []
        self.eventcards2 = []

        w = self.board.width/10.0   # Dimension to match the board width
        h = w*2.4

        text_height = w*1.6
        theight = w*2.3
        font_name = self.board.font_name
        style_text      = 'color: white;  background-color: #000000; font-size: %fvh; line-height: %fvh; font-family: "%s", serif; vertical-align: baseline;'%(text_height*0.25, theight*0.18, font_name)
        style_text_bold = 'color: yellow; background-color: #000000; font-size: %fvh; line-height: %fvh; font-family: "%s", serif; font-weight: bold;'%(text_height*0.45, theight*0.18, font_name)

        self.minus_buttons = {}
        for event in Config.EVENTS:
            title = v.Html(tag='div',children=[event['description']], style_='text-align: center; %s'%style_text)
            
            if Config.EVENT_COUNTABLE[event['id']]:
                value = v.Html(tag='div',children=[''], style_=style_text_bold)
                plus  = iconButton.iconButton(onclick=self.click_plus,  argument=event['id'], icon='mdi-plus',  color='green')
                minus = iconButton.iconButton(onclick=self.click_minus, argument=event['id'], icon='mdi-minus', color='red', disabled=True)
                self.minus_buttons[event['id']] = minus
                action = v.CardActions(children=[plus.draw(), value, minus.draw()], class_='mt-auto justify-center')
                c = v.Card(flat=True, tile=True, outlined=True, color=self.board.tb.color_back, ripple=False, children=[title, action], width='%fvw'%w, height='%fvh'%h, class_='pa-0 pt-2 noselect d-flex flex-column',
                           style_='border-width: 1px; border-color: #BBBBBB !important; overflow: hidden;')
            else:
                if event['id'] == 18: icon = 'mdi-arrow-left-bold'
                else:                 icon = 'mdi-arrow-right-bold'
                fire = iconButton.iconButton(onclick=self.click_fire,  argument=event['id'], icon=icon, x_large=True, width='%fvw'%(w*0.9), color='yellow')
                action = v.CardActions(children=[fire.draw()], class_='mt-auto justify-center')
                c = v.Card(flat=True, tile=True, outlined=True, color=self.board.tb.color_back, ripple=False, children=[title, action], width='%fvw'%w, height='%fvh'%h, class_='pa-0 pt-2 noselect d-flex flex-column',
                           style_='border-width: 1px; border-color: #BBBBBB !important; overflow: hidden;')
                
            c.id = event['id']
            self.event_card[event['id']] = c
            
            if Config.EVENT_TEAM[c.id]: c.disabled = False
            else:                       c.disabled = True

            if   event['row'] == 1: self.eventcards1.append(c)
            elif event['row'] == 2: self.eventcards2.append(c)

        # Card for buttons
        self.cbuttons = v.Card(flat=True, tile=True, color=self.board.tb.color_back, width='%fvw'%self.board.infow, height='%fvh'%(2*h), class_='pa-2')

        bw = 'calc(%fvw - 16px)'%self.board.infow
        iScore   = v.Icon(right=True, children=['mdi-table'])
        iPlay    = v.Icon(right=True, children=['mdi-format-list-bulleted'])
        iChart   = v.Icon(right=True, children=['mdi-chart-line'])
        iSummary = v.Icon(right=True, children=['mdi-sigma'])
        self.bScore   = v.Btn(children=['Score Table', iScore],   width=bw, color=settings.color_first, class_='mb-2')
        self.bPlay    = v.Btn(children=['Play By Play',iPlay],    width=bw, color=settings.color_first, class_='mb-2')
        self.bChart   = v.Btn(children=['Points Chart',iChart],   width=bw, color=settings.color_first, class_='mb-2')
        self.bSummary = v.Btn(children=['Game Summary',iSummary], width=bw, color=settings.color_first)
        
        self.cbuttons.children = [self.bScore, self.bPlay, self.bChart, self.bSummary]
        
        self.children = [ widgets.VBox([widgets.HBox(self.eventcards1), widgets.HBox(self.eventcards2)]), self.cbuttons ]
        
            

    # Add an event to the pandas dataframe of events
    def storeEvent(self, player_name, event_id, x=0, y=0, team=Config.TEAM):
        if self.df.shape[0] > 0:
            evid = max(self.df.index) + 1
        else:
            evid = 0

        if player_name is None:
            player_name = Config.TEAM

        self.df.loc[evid] = [team, player_name, event_id, Config.EVENT_NAME[event_id], Config.EVENT_DESCRIPTION[event_id], self.board.quarter, self.board.seconds, x, y]
        self.update(event_id)
        
        self.board.throwmap.updateThrows(self.df, self.board.player_selected, background=True)
        
        # Update all the text over the player images
        for player_name in self.game.on_field:
            if player_name is not None and len(player_name) > 0:
                self.game.playerDisplayInfo(player_name)

        
    # Remove last event for a team/player/event_id from the pandas dataframe of events
    def removeLastEvent(self, player_name, event_id, team=Config.TEAM):
        df = self.df[(self.df['team']==team)&(self.df['player']==player_name)&(self.df['event']==event_id)]
        if df.shape[0] > 0:
            evid = list(df.index)[-1]
            self.df.drop(evid, inplace=True)
            self.update(event_id)

            self.board.throwmap.updateThrows(self.df, self.board.player_selected, background=True)
            
            # Update all the text over the player images
            for player_name in self.game.on_field:
                if player_name is not None and len(player_name) > 0:
                    self.game.playerDisplayInfo(player_name)
            
    
    # Select the throw point
    def on_select_throw_point(self, x,y, argument):
        player_name, event_id, points = argument
        self.board.add_team_points(points)
        self.storeEvent(player_name, event_id, x=x, y=y)
        self.board.throwmap.updateThrows(self.df, player_name)
        
    
    # Add an event
    def click_plus(self, event_id):

        doStore = True
        
        # Score 1,2,3 points
        if event_id in [0, 2, 4]:
            points = Config.EVENT_VALUE[event_id]
            
            if event_id == 2:
                self.board.throwmap.select(mode=2, df=self.df, scale=2*self.board.scale, onclick=self.on_select_throw_point,
                                           argument=(self.board.player_selected, event_id, points), scored=True)
                return

            elif event_id == 4:
                self.board.throwmap.select(mode=3, df=self.df, scale=2*self.board.scale, onclick=self.on_select_throw_point,
                                           argument=(self.board.player_selected, event_id, points), scored=True)
                return
                
            self.board.add_team_points(points)

        # Miss 1,2,3 points
        elif event_id in [1, 3, 5]:
            points = 0
            
            if event_id == 3:
                self.board.throwmap.select(mode=2, df=self.df, scale=2*self.board.scale, onclick=self.on_select_throw_point,
                                           argument=(self.board.player_selected, event_id, points), scored=False)
                return
            
            elif event_id == 5:
                self.board.throwmap.select(mode=3, df=self.df, scale=2*self.board.scale, onclick=self.on_select_throw_point,
                                           argument=(self.board.player_selected, event_id, points), scored=False)
                return
            
        elif event_id == 13:            # Foul committed
            self.board.add_team_foul()
            
        elif event_id == 15:            # Foul received
            
            doStore = False
            
            def onselect(player_name):
                self.board.add_opponents_foul()
                self.game.opponentAddFoul(player_name)
                self.storeEvent(player_name, 13, team=Config.OPPO)  # Opponent committed foul
                self.storeEvent(self.board.player_selected, 15)     # Team player received the foul

            self.game.selectOpponent(onselect=onselect)
            
            
        if doStore:
            self.storeEvent(self.board.player_selected, event_id)

        
    # Remove the last event for the current player
    def click_minus(self, event_id):
        
        if event_id in [0, 2, 4]:       # Score 1,2,3 points
            points = Config.EVENT_VALUE[event_id]
            self.board.add_team_points(-points)
        elif event_id == 13:            # Foul committed
            self.board.remove_team_foul()
            
        player = self.board.player_selected
        if player is None: player = Config.TEAM
        
        doRemove = True
        
        if event_id in [0, 1, 2, 3, 4, 5]:
            self.board.throwmap.updateThrows(self.df, self.board.player_selected, background=True)

        elif event_id == 15:            # Foul received
            
            doRemove = False
            
            def onselect(player_name):
                self.board.remove_opponents_foul()
                self.game.opponentRemoveFoul(player_name)
                self.removeLastEvent(player_name, 13, team=Config.OPPO)    # Remove Opponent committed foul
                self.removeLastEvent(player, event_id)              # Remove Team player received foul
                
            self.game.selectOpponent(onselect=onselect, opponents_list=self.opponentsWithFouls())
            
        if doRemove:
            self.removeLastEvent(player, event_id)
            
            
    # Select a player from the bench to enter on the field
    def selectPlayerToEnter(self):
        def onselect(player_name):
            self.board.toField(player_name, position=self.board.player_index)
            self.storeEvent(player_name, 18)

        self.game.selectFromBench(onselect=onselect)
        
        
    # Fire an uncountable event ("go to field" or "go to bench")
    def click_fire(self, event_id):
        
        # Selection of a player to go on the field
        if event_id == 18:
            self.selectPlayerToEnter()
            
        # Uscita dal campo
        elif event_id == 19:
            player_name = self.board.player_selected
            self.storeEvent(player_name, event_id)
            self.board.toBench(player_name)

            self.selectPlayerToEnter()
        
        
    # Called when one of the player on the field is selected from the board
    def on_player_selected(self):
        if self.board.player_selected is None:               # No players selected --> Events go to the Team
            for c in self.eventcards1+self.eventcards2:
                if Config.EVENT_TEAM[c.id]: c.disabled = False
                else:                       c.disabled = True
                self.update(c.id)
        elif self.board.player_selected == '':               # Empty player selected: only "Entrata in campo" is enabled
            for c in self.eventcards1+self.eventcards2:
                if c.id == 18:  c.disabled = False
                else:           c.disabled = True
                self.update(c.id)
        else:
            for c in self.eventcards1+self.eventcards2:      # Normal player selected: only "Entrata in campo" is disabled
                if c.id == 18:  c.disabled = True
                else:           c.disabled = False
                self.update(c.id)
        
        self.board.throwmap.updateThrows(self.df, self.board.player_selected)
        
        
    # Store opponents score events
    def on_opponents_points(self, num_points):
        
        # Add opponent points
        if num_points > 0:
            if   num_points == 1: event_id = 0
            elif num_points == 2: event_id = 2
            else:                 event_id = 4

            def onselect(player_name):
                self.game.opponentAddPoints(player_name, num_points)
                self.storeEvent(player_name, event_id, team=Config.OPPO)
                self.board.doadd_opponent_points(num_points)
                self.board.throwmap.updateThrows(self.df, self.board.player_selected, background=True)

            self.game.selectOpponent(onselect=onselect)
            return True

        # Remove opponent points
        elif num_points < 0:
            if num_points == -1:
                opponents_list = self.opponentsWith1Point()
                if len(opponents_list) == 0:
                    return
                event_id = 0
            elif num_points == -2:
                opponents_list = self.opponentsWith2Point()
                if len(opponents_list) == 0:
                    return
                event_id = 2
            else:
                opponents_list = self.opponentsWith3Point()
                if len(opponents_list) == 0:
                    return
                event_id = 4

            def onselect(player_name):
                self.game.opponentRemovePoints(player_name, -num_points)
                self.removeLastEvent(player_name, event_id, team=Config.OPPO)
                self.board.doadd_opponent_points(num_points)
                self.board.throwmap.updateThrows(self.df, self.board.player_selected, background=True)

            self.game.selectOpponent(onselect=onselect, opponents_list=opponents_list)
        
    
    # Returns the list of the opponents player names that have at least one foul
    def opponentsWithFouls(self):
        return list(self.df[(self.df['team']==Config.OPPO)&(self.df['event']==13)]['player'].unique())
        
    # Returns the list of the opponents player names that have at least one free throw scored
    def opponentsWith1Point(self):
        return list(self.df[(self.df['team']==Config.OPPO)&(self.df['event']==0)]['player'].unique())
        
    # Returns the list of the opponents player names that have at least one 2 point throw scored
    def opponentsWith2Point(self):
        return list(self.df[(self.df['team']==Config.OPPO)&(self.df['event']==2)]['player'].unique())
    
    # Returns the list of the opponents player names that have at least one 3 point throw scored
    def opponentsWith3Point(self):
        return list(self.df[(self.df['team']==Config.OPPO)&(self.df['event']==4)]['player'].unique())
    
    
    # Add a time-out event for Team
    def on_team_timeout(self):
        self.storeEvent(Config.TEAM, 20, team=Config.TEAM)
    
    
    # Add a time-out event for Opponents
    def on_opponents_timeout(self):
        self.storeEvent(Config.OPPO, 20, team=Config.OPPO)
        
    
    
    # Update text for an event for the selected player
    def update(self, event_id):
        
        if Config.EVENT_COUNTABLE[event_id]:
            c = self.event_card[event_id]
            html  = c.children[1].children[1]
            minus = self.minus_buttons[event_id]

            player = self.board.player_selected
            if player is None: player = Config.TEAM

            df = self.df[(self.df['team']==Config.TEAM)&(self.df['player']==player)&(self.df['event']==event_id)]
            if df.shape[0] == 0:
                html.children = ['']
                minus.disabled = True
            else:
                html.children  = [str(df.shape[0])]
                minus.disabled = False
                        
        
    ###########################################################################################################################################################################
    # Properties
    ###########################################################################################################################################################################
        
    @property
    def scale(self):
        return self.board.scale

    @scale.setter
    def scale(self, s: float):
        self.board.scale = s
        self.createControls()
    
    # Scaling called from the ScoreBoard
    def on_scaling(self, scale):
        self.scale = scale