"""Overall ScoreBoard: displays time, points and fouls as digital numbers"""
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
from ipywidgets import widgets, HTML
import threading
import time
import ipyvuetify as v
from PIL import Image
from ipyevents import Event

# vois imports
from vois import colors
from vois.vuetify import settings, iconButton

# local imports
import Config
import DigitalBoards
import Game
import ThrowMap
import Stats


###########################################################################################################################################################################
# ScoreBoard
###########################################################################################################################################################################
class ScoreBoard(widgets.VBox):
    
    def __init__(self,
                 team_file,    # Path of the input Team file
                 game_file,    # Path of the input Game file
                 scale=1.0,    # Overall scaling
                 output=None): # Output widgets for the opening of dialog-boxes

        super().__init__()
        
        # Callbacks toward the Events instance
        self.on_player_selected   = None          # When a player on the field is selected
        self.on_opponents_points  = None          # When the opponents team scores
        self.on_team_timeout      = None          # When the team calls a timeout
        self.on_opponents_timeout = None          # When the opponents calls a timeout
        self.on_scaling           = None          # Called for scaling small/medium/large 
        
        # Read game info from the input files
        self.game = Game.Game(self, team_file, game_file)
        
        # Store input parameters
        self._scale = scale
        self.output = output
        
        self.createControls()

        
    # Creation of the controls
    def createControls(self):

        # Time board
        self.timer_last_second_elapsed = 0.0
        self.tb = DigitalBoards.TimeBoard(scale=self._scale*1.0313,                 # To make it the same width of the Score1 + Colon + Score2
                                          onupdate=self.on_timer_update,
                                          onstopped=self.on_timer_stopped,
                                          onterminated=self.on_timer_terminated)
        self.tb.seconds = 600

        twidth = (self.tb.width*0.55)/1.12
        self.theight = self.tb.height
        self.text_height = self.theight*0.98

        self.width = self.tb.width + 2*twidth
        
        space_height = self.theight*0.3
                
        self.font_name = 'Roboto Condensed'
        self.spacer2  = v.Html(tag='div',children=[' '], style_='width: %fvw; height: %fvh; background-color: %s;'%(twidth, space_height, self.tb.color_back))
        self.spacer1b = v.Html(tag='div',children=[' '], style_='width: %fvw; height: %fvh; background-color: %s;'%(self.tb.width, space_height*0.5, self.tb.color_back))
        self.spacer2b = v.Html(tag='div',children=[' '], style_='width: %fvw; height: %fvh; background-color: %s;'%(twidth, space_height*0.5, self.tb.color_back))

        # Card for number of current quarter
        self.quarter = 1
        self.qcard = v.Card(flat=True, color=self.tb.color_back, tile=True, width='%fvw'%self.tb.width, height='%fvh'%space_height, ripple=False, nuxt=False, class_='noselect',
                            style_='overflow: hidden; color: #ffff00 !important; font-size: %fvh; line-height: %fvh; font-family: "%s", serif; vertical-align: baseline; text-align: center;'%(self.text_height*0.85, self.theight*0.25, self.font_name))        
        self.qcard.children = ['- '*self.quarter]
        
        # Points
        if self.home_game:
            onclick1 = None
            onclick2 = self.internal_on_opponents_points
        else:
            onclick1 = self.internal_on_opponents_points
            onclick2 = None
            
        self.pb1 = DigitalBoards.PointsBoard(scale=self._scale, left_align=False, onclick=onclick1)
        self.colon = DigitalBoards.Colon(scale=self._scale)
        self.pb2 = DigitalBoards.PointsBoard(scale=self._scale, left_align=True, onclick=onclick2)
        
        # Fouls
        self.fb1 = DigitalBoards.FoulsBoard(scale=self._scale)
        self.fb2 = DigitalBoards.FoulsBoard(scale=self._scale)
        
        fwidth1 = (twidth - self.fb1.width)*0.1
        fwidth2 = (twidth - self.fb1.width)*0.9
        fheight = self.fb1.height
        self.spacer3 = v.Html(tag='div', children=[' '], style_='width: %fvw; height: %fvh; background-color: %s;'%(fwidth1, fheight, self.tb.color_back))
        
        self.spacer3B = v.Html(tag='div', children=[' '], style_='width: %fvw; height: %fvh; background-color: %s;'%(fwidth1*4.86, fheight, self.tb.color_back))
        
        # Time-outs
        self.timeouts1 = 0
        self.timeouts2 = 0
        
        self.cardtimeout1 = v.Card(flat=True, color=self.tb.color_back, tile=True, width='%fvw'%fwidth2, height='%fvh'%fheight, ripple=False, nuxt=False, class_='ml-0 noselect',
                                   style_='overflow: hidden; color: #ffffff; font-size: %fvh; line-height: %fvh; font-family: "%s", serif; vertical-align: baseline; text-align: center; writing-mode: tb-rl;'%(self.text_height*0.94,
                                                                                                                                                                                                                self.theight,
                                                                                                                                                                                                                self.font_name))        
        
        self.cardtimeout2 = v.Card(flat=True, color=self.tb.color_back, tile=True, width='%fvw'%fwidth2, height='%fvh'%fheight, ripple=False, nuxt=False, class_='noselect',
                                   style_='overflow: hidden; color: #ffffff; font-size: %fvh; line-height: %fvh; font-family: "%s", serif; vertical-align: baseline; text-align: center; writing-mode: tb-rl;'%(self.text_height*0.94,
                                                                                                                                                                                                                self.theight,
                                                                                                                                                                                                                self.font_name))        

        # Abbreviated name of the two teams
        style_text = 'color: white; background-color: %s; font-size: %fvh; line-height: %fvh; font-family: "%s", serif; vertical-align: baseline;'%(self.tb.color_back, self.text_height, self.theight, self.font_name)
        self.team1  = v.Html(tag='div', children=[self.team1_abbr], class_='noselect', style_='width: %fvw; height: %fvh; %s; overflow: hidden; text-align: left;  padding-left:  %fvw;'%(twidth, self.theight, style_text, fwidth1*1.2))
        self.team2  = v.Html(tag='div', children=[self.team2_abbr], class_='noselect', style_='width: %fvw; height: %fvh; %s; overflow: hidden; text-align: right; padding-right: %fvw;'%(twidth, self.theight, style_text, fwidth1*1.2))

        # Backgound image for field orentation and quick stats display
        self.info_field_left = True
        infoh = self.tb.height + space_height + self.fb1.height + space_height*0.5
        self.infow = (infoh*856/1050)/2.0
        self.throwmap = ThrowMap.ThrowMap(self, width=self.infow, output=self.output)

        # Card for the buttons
        self.showOverImage = 'T'
        wi = '%fvw'%(self.infow/7)
        self.iPoints = iconButton.iconButton(width=wi, onclick=self.showPoints, large=True, outlined=False, rounded=False, icon='mdi-alpha-p', tooltip='Display points scored')
        self.iTime   = iconButton.iconButton(width=wi, onclick=self.showTime,   large=True, outlined=False, rounded=False, icon='mdi-alpha-t', color='red', tooltip='Display time on the field')
        self.iValue  = iconButton.iconButton(width=wi, onclick=self.showValue,  large=True, outlined=False, rounded=False, icon='mdi-alpha-v', tooltip='Display players evaluation')
        self.iOER    = iconButton.iconButton(width=wi, onclick=self.showOER,    large=True, outlined=False, rounded=False, icon='mdi-alpha-o', tooltip='Display Offensive Efficency Rating')
        self.iVIR    = iconButton.iconButton(width=wi, onclick=self.showVIR,    large=True, outlined=False, rounded=False, icon='mdi-alpha-i', tooltip='Display Value Index Rating')
        self.iPlusM  = iconButton.iconButton(width=wi, onclick=self.showPlusM,  large=True, outlined=False, rounded=False, icon='mdi-alpha-m', tooltip='Display Plus/Minus')
        self.iTShoot = iconButton.iconButton(width=wi, onclick=self.showTShoot, large=True, outlined=False, rounded=False, icon='mdi-alpha-s', tooltip='Display True Shooting Percentage')
        self.iconButtons = [self.iPoints, self.iTime, self.iValue, self.iOER, self.iVIR, self.iPlusM, self.iTShoot]
        
        wi = '%fvw'%(self.infow/3)
        self.iSmall  = iconButton.iconButton(width=wi, onclick=self.scaleSmall,  x_large=True, outlined=False, rounded=False, icon='mdi-square-small',  tooltip='Scale to small size')
        self.iMedium = iconButton.iconButton(width=wi, onclick=self.scaleMedium, x_large=True, outlined=False, rounded=False, icon='mdi-square-medium', tooltip='Scale to medium size')
        self.iLarge  = iconButton.iconButton(width=wi, onclick=self.scaleLarge,  x_large=True, outlined=False, rounded=False, icon='mdi-square',        tooltip='Scale to large size')
        
        h = 'calc(%fvw - 4px)'%(self.width/5)
        self.cbuttons = v.Card(flat=True, tile=True, color=self.tb.color_back, width='%fvw'%self.infow, height=h,
                               children=[v.Row(align='center', justify='space-around', no_gutters=True,
                                               children=[self.iPoints.draw(), self.iTime.draw(), self.iValue.draw(), 
                                                         self.iOER.draw(), self.iVIR.draw(), self.iPlusM.draw(), self.iTShoot.draw()]),
                                         v.Row(align='center', justify='space-around', no_gutters=True,
                                               children=[self.iSmall.draw(), self.iMedium.draw(), self.iLarge.draw()])
                                        ])
        
        
        # Players on the field
        self.players_card = []
        self.player_selected = None    # Name of the currently selected player
        self.player_index    = -1      # Index of the currently selected player (-1, or 0,1,2,3,4)
        
        self.onfield, self.players_card = self.game.playersList(self.game.on_field, self.click_on_player)
        
        # Set the status
        self.game.setBoardStatus()
        
        # Update the timeouts
        self.cardtimeout1.children = ['•'*self.timeouts1]
        self.cardtimeout1.on_event('click', self.click_on_timeout1)
        self.cardtimeout2.children = ['•'*self.timeouts2]
        self.cardtimeout2.on_event('click', self.click_on_timeout2)
        
        # Update throwMap for the Team
        self.throwmap.updateThrows(self.game.events_df, background=True)
        
        self.children = [
                    HTML('''
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Roboto+Condensed:ital,wght@0,100..900;1,100..900&display=swap" rel="stylesheet">
<style>
.black_background {
    background-color: black;
}
</style>
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
'''),
                    widgets.HBox([
                        widgets.VBox([self.team1,
                                      self.spacer2,
                                      widgets.HBox([self.spacer3, self.fb1, self.cardtimeout1]),
                                      self.spacer2b]),

                        widgets.VBox([self.tb,
                                      self.qcard,
                                      widgets.HBox([self.pb1, self.colon, self.pb2, self.spacer3B]),
                                      self.spacer1b]),

                        widgets.VBox([self.team2,
                                      self.spacer2,
                                      widgets.HBox([self.cardtimeout2, self.fb2, self.spacer3]),
                                      self.spacer2b]),
                        
                        self.throwmap
                    ]),
            
                    widgets.HBox([self.onfield, self.cbuttons])
        ]
        
        
    ###########################################################################################################################################################################
    # Time management
    ###########################################################################################################################################################################

    # Compensate elapsed time with the time on the field of the players
    def timer_compensate(self):
        
        # Calculate total elapsed seconds
        total_seconds = 0.0
        for q in range(1,self.quarter):  # For all the finished quarters
            if q <= 4:
                total_seconds += 600.0
            else:
                total_seconds += 300.0
        
        # Sum the time of the current quarter
        if self.quarter <= 4:
            total_seconds += 600.0 - self.tb.seconds
        else:
            total_seconds += 300.0 - self.tb.seconds
            
        total_seconds *= 5
            
        # Calculate the total seconds on the field of all the players
        total_onfield = 0.0
        for name, player in self.game.players_info.items():
            total_onfield += player['time_on_field']
           
        # Missing seconds
        if total_onfield > 0:
            missing_seconds_perc = total_seconds/total_onfield
            
            # Assign missing seconds to all the players that touched the field
            for player_name in self.game.players_info.keys():
                self.game.players_info[player_name]['time_on_field'] *= missing_seconds_perc
            

    # Update info displayed on top of player images
    def updateInfoOnPlayerImages(self):
        for player_name in self.game.on_field:
            if player_name is not None and len(player_name) > 0:
                if self.showOverImage in ['T', 'I']:
                    self.game.playerDisplayInfo(player_name)

                    
    # Called by the timer at each update
    def on_timer_update(self, seconds_elapsed):
        seconds_to_add = seconds_elapsed - self.timer_last_second_elapsed
        self.timer_last_second_elapsed = seconds_elapsed
        for player_name in self.game.on_field:
            if player_name is not None and len(player_name) > 0:
                self.game.players_info[player_name]['time_on_field'] += seconds_to_add
        self.updateInfoOnPlayerImages()

                
    # Called when the timer is stopped
    def on_timer_stopped(self):
        self.timer_last_second_elapsed = 0.0
        self.timer_compensate()
        self.updateInfoOnPlayerImages()
        self.game.saveGame()

    
    # Called when timer reaches 0 seconds: perform end of quarter activities
    def on_timer_terminated(self):
        
        self.timer_compensate()
        self.updateInfoOnPlayerImages()
        self.game.saveGame()
        
        # If the game continues
        if self.quarter < 4 or self.pb1.points == self.pb2.points:
            
            # Move to next quarter
            self.quarter += 1
            self.qcard.children = ['- '*self.quarter]
        
            # Reset timeouts at the start of 3rd quarter
            if self.quarter == 3:
                self.timeouts1 = self.timeouts2 = 0
                self.cardtimeout1.children = ['•'*self.timeouts1]
                self.cardtimeout2.children = ['•'*self.timeouts2]

            # Reset the team fouls
            if self.quarter <= 4:
                self.fb1.fouls = 0
                self.fb2.fouls = 0
                
            # Reset the TimeBoar to 10 or 5 minutes
            if self.quarter <= 4: self.tb.seconds = 600.0
            else:                 self.tb.seconds = 300.0
            self.tb.gameover = False
        
        # If the game is over
        else:
            self.tb.gameover  = True
            self.pb1.gameover = True
            self.pb2.gameover = True
            
            # Team total fouls
            df = self.game.events_df[(self.game.events_df['team']==Config.TEAM)]
            team_fouls = Stats.count(df, 'FCom')

            # Opponents total fouls
            df = self.game.events_df[(self.game.events_df['team']==Config.OPPO)]
            oppo_fouls = Stats.count(df, 'FCom')
            
            # Display th etotal fouls for the two teams
            if self.home_game:
                self.fb1.fouls = team_fouls
                self.fb2.fouls = oppo_fouls
            else:
                self.fb1.fouls = oppo_fouls
                self.fb2.fouls = team_fouls
            
        
    ###########################################################################################################################################################################
    # Players, timeouts, points, fouls management
    ###########################################################################################################################################################################
        
    # Selection of one of the players on the field
    def click_on_player(self, widget, event, data):
        if widget.outlined:
            widget.outlined = False
            self.player_selected = None
            self.player_index    = -1
        else:
            for c in self.players_card:
                c.outlined = False
                
            self.player_index    = self.players_card.index(widget)
            self.player_selected = self.game.on_field[self.player_index]
            self.game.playerDisplayInfo(self.player_selected)
            widget.outlined = True
        
        if self.on_player_selected is not None:
            self.on_player_selected()
        

    # Add a timeout for team 1
    def click_on_timeout1(self, *args):
        if not self.tb.gameover:
            if self.timeouts1 <= 2:
                self.timeouts1 += 1
                self.cardtimeout1.children = ['•'*self.timeouts1]
                if self.home_game:
                    if self.on_team_timeout is not None:
                        self.on_team_timeout()
                else:
                    if self.on_opponents_timeout is not None:
                        self.on_opponents_timeout()
       
        
    # Add a timeout for team 2
    def click_on_timeout2(self, *args):
        if not self.tb.gameover:
            if self.timeouts2 <= 2:
                self.timeouts2 += 1
                self.cardtimeout2.children = ['•'*self.timeouts2]
                if self.home_game:
                    if self.on_opponents_timeout is not None:
                        self.on_opponents_timeout()
                else:
                    if self.on_team_timeout is not None:
                        self.on_team_timeout()
        

    # Add points to team
    def add_team_points(self, num_points):
        # Update plusminus to all the players on the field
        for player_name in self.game.on_field:
            if player_name is not None and len(player_name) > 0:
                self.game.players_info[player_name]['plusminus'] += num_points
                self.game.playerDisplayInfo(player_name)
                
        if self.home_game:
            self.pb1.points += num_points
        else:
            self.pb2.points += num_points

            
    # Add one foul to the team
    def add_team_foul(self):
        if self.home_game:
            self.fb1.fouls += 1
        else:
            self.fb2.fouls += 1
        
    # Add one foul to the opponents
    def add_opponents_foul(self):
        if self.home_game:
            self.fb2.fouls += 1
        else:
            self.fb1.fouls += 1

        
    # Remove one foul from the team
    def remove_team_foul(self):
        if self.home_game:
            self.fb1.fouls -= 1
        else:
            self.fb2.fouls -= 1


    # Remove one foul from the opponents
    def remove_opponents_foul(self):
        if self.home_game:
            self.fb2.fouls -= 1
        else:
            self.fb1.fouls -= 1
        
        
    # Add points to opponent team
    def internal_on_opponents_points(self, num_points):
        # Remove scored points
        if num_points < 0:
            if self.on_opponents_points is not None:
                self.on_opponents_points(num_points)
            else:
                doupdate = False
                if self.home_game:
                    if self.pb2.points >= -num_points:
                        doupdate = True
                        self.pb2.points += num_points
                else:
                    if self.pb1.points >= -num_points:
                        doupdate = True
                        self.pb1.points += num_points

                # Update plusminus to all the players on the field
                if doupdate:
                    for player_name in self.game.on_field:
                        if player_name is not None and len(player_name) > 0:
                            self.game.players_info[player_name]['plusminus'] -= num_points
                            self.game.playerDisplayInfo(player_name)

        # Add scored points
        else:
            if self.on_opponents_points is not None:
                self.on_opponents_points(num_points)
            else:
                self.doadd_opponent_points(num_points)
        

    # Real add of points to the opponents
    def doadd_opponent_points(self, num_points):

        # Update plusminus to all the players on the field
        for player_name in self.game.on_field:
            if player_name is not None and len(player_name) > 0:
                self.game.players_info[player_name]['plusminus'] -= num_points
                self.game.playerDisplayInfo(player_name)
                
        if self.home_game:
            self.pb2.points += num_points
        else:
            self.pb1.points += num_points
        

    ###########################################################################################################################################################################
    # Properties
    ###########################################################################################################################################################################
        
    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, s: float):
        self._scale = s
        self.createControls()
        
        
    # Current seconds
    @property
    def seconds(self):
        return self.tb.seconds

    @seconds.setter
    def seconds(self, s: float):
        self.tb.seconds = s
        

    # Returns the list of players currently on the bench (not in the field)
    @property
    def bench(self):
        return sorted(list(set(self.game.players_by_name) - set(self.game.on_field)))
    
    
    ###########################################################################################################################################################################
    # Send to field, send to bench a player
    ###########################################################################################################################################################################
    
    # Send a player to the field (and stops the timer)
    def toField(self, player_name, position=0):
        self.tb.stop()
        self.game.playerToField(player_name, position=position)
      
    
    # Send a player to the bench (and stops the timer)
    def toBench(self, player_name):
        self.tb.stop()
        self.game.playerToBench(player_name)
        

    ###########################################################################################################################################################################
    # Select info to be displayed on top of players' images
    ###########################################################################################################################################################################
        
    # Select points to be displayed on top of the player image
    def showPoints(self):
        self.showOverImage = 'P'
        for i in self.iconButtons: i.color = settings.color_first
        self.iPoints.color = 'red'
        self.game.playerDisplayInfoAll()
        
    # Select time to be displayed on top of the player image
    def showTime(self):
        self.showOverImage = 'T'
        for i in self.iconButtons: i.color = settings.color_first
        self.iTime.color = 'red'
        self.game.playerDisplayInfoAll()
        
    # Select value to be displayed on top of the player image
    def showValue(self):
        self.showOverImage = 'V'
        for i in self.iconButtons: i.color = settings.color_first
        self.iValue.color  = 'red'
        self.game.playerDisplayInfoAll()
        
    # Select OER to be displayed on top of the player image
    def showOER(self):
        self.showOverImage = 'O'
        for i in self.iconButtons: i.color = settings.color_first
        self.iOER.color  = 'red'
        self.game.playerDisplayInfoAll()
        
    # Select VIR to be displayed on top of the player image
    def showVIR(self):
        self.showOverImage = 'I'
        for i in self.iconButtons: i.color = settings.color_first
        self.iVIR.color  = 'red'
        self.game.playerDisplayInfoAll()
        
    # Select PlusMinus to be displayed on top of the player image
    def showPlusM(self):
        self.showOverImage = 'M'
        for i in self.iconButtons: i.color = settings.color_first
        self.iPlusM.color  = 'red'
        self.game.playerDisplayInfoAll()
        
    # Select TrueShooting to be displayed on top of the player image
    def showTShoot(self):
        self.showOverImage = 'S'
        for i in self.iconButtons: i.color = settings.color_first
        self.iTShoot.color  = 'red'
        self.game.playerDisplayInfoAll()
        
        
    ###########################################################################################################################################################################
    # Scaling
    ###########################################################################################################################################################################

    def scaleSmall(self):
        if self.on_scaling is not None:
            self.on_scaling(0.4)
    
    def scaleMedium(self):
        if self.on_scaling is not None:
            self.on_scaling(0.55)

    def scaleLarge(self):
        if self.on_scaling is not None:
            self.on_scaling(0.75)

    
        