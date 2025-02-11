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
from random import randrange
from IPython.display import HTML as ipyHTML   # !!!
import io
import datetime

# vois imports
from vois import download
from vois.vuetify import settings, iconButton, dialogGeneric, IconClipboard

# local imports
import Config
import ScoreBoard
import BoxScore
import ThrowMap
import Game
import Stats


###########################################################################################################################################################################
# Events: display cards to insert player events
###########################################################################################################################################################################
class Events(widgets.VBox):
    
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
        
        self.board.on_quarter_start     = self.on_quarter_start       # Called at the start of each quarter
        self.board.on_quarter_end       = self.on_quarter_end         # Called at the end of each quarter
        self.board.on_game_loaded       = self.on_game_loaded         # Called when a game is loaded
        
        
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
            self.df = pd.DataFrame(columns=['team', 'player', 'event', 'event_name', 'event_description', 'quarter', 'seconds', 'x', 'y', 'time'])
             
            # Add reference to events dataframe to the players instance
            self.game.events_df = self.df
        else:
            self.df = self.game.events_df
        
        self.createControls()
        
        if self.board.tb.gameover:
            self.gameover()
            
        self.on_player_selected()

        
    # Creation of the controls
    def createControls(self):

        # Two rows of cards to manage all types of events
        self.eventcards1 = []
        self.eventcards2 = []

        w = self.board.width/10.0   # Dimension to match the board width
        hcards = w*1.02

        text_height = w*0.7
        theight = w*0.92
        font_name = self.board.font_name
        style_text      = 'color: white;  background-color: #000000; font-size: %fvw; line-height: %fvw; font-family: "%s", serif; vertical-align: baseline;'%(text_height*0.25, theight*0.18, font_name)
        style_text_bold = 'color: yellow; background-color: #000000; font-size: %fvw; line-height: %fvw; font-family: "%s", serif; font-weight: bold;'%(text_height*0.45, theight*0.18, font_name)

        self.plus_buttons  = {}
        self.minus_buttons = {}
        
        self.event_card_not_countable = []
        
        for event in Config.EVENTS:
            title = v.Html(tag='div',children=[event['description']], style_='text-align: center; %s'%style_text)
            
            if Config.EVENT_COUNTABLE[event['id']]:
                value = v.Html(tag='div',children=[''], style_=style_text_bold)
                plus = iconButton.iconButton(onclick=self.click_plus,  argument=event['id'], icon='mdi-plus',  color='green')
                self.plus_buttons[event['id']] = plus
                minus = iconButton.iconButton(onclick=self.click_minus, argument=event['id'], icon='mdi-minus', color='red', disabled=True)
                self.minus_buttons[event['id']] = minus
                action = v.CardActions(children=[plus.draw(), value, minus.draw()], class_='mt-auto justify-center mb-2')
                c = v.Card(flat=True, tile=True, outlined=True, color=self.board.tb.color_back, ripple=False, children=[title, action], width='%fvw'%w, height='calc(%fvw + 4px)'%hcards, class_='pa-0 pt-2 noselect d-flex flex-column',
                           style_='border-width: 1px; border-color: #BBBBBB !important; overflow: hidden;')
            else:
                if event['id'] == 18: icon = 'mdi-arrow-left-bold'
                else:                 icon = 'mdi-arrow-right-bold'
                fire = iconButton.iconButton(onclick=self.click_fire,  argument=event['id'], icon=icon, x_large=True, width='%fvw'%(w*0.9), color='yellow')
                action = v.CardActions(children=[fire.draw()], class_='mt-auto justify-center mb-2')
                c = v.Card(flat=True, tile=True, outlined=True, color=self.board.tb.color_back, ripple=False, children=[title, action], width='%fvw'%w, height='calc(%fvw + 4px)'%hcards, class_='pa-0 pt-2 noselect d-flex flex-column',
                           style_='border-width: 1px; border-color: #BBBBBB !important; overflow: hidden;')
                self.event_card_not_countable.append(c)
                
            c.id = event['id']
            self.event_card[event['id']] = c
            
            if Config.EVENT_TEAM[c.id]: c.disabled = False
            else:                       c.disabled = True

            if   event['row'] == 1: self.eventcards1.append(c)
            elif event['row'] == 2: self.eventcards2.append(c)

        # Card for buttons
        cwidth = self.board.infow*1.184
        self.cbuttons = v.Card(flat=True, tile=True, color=self.board.tb.color_back, width='%fvw'%cwidth, height='calc(%fvw + 8px)'%(2*hcards), class_='pa-2', style_='overflow: hidden;')

        bw = 'calc(%fvw - 16px)'%cwidth
        bh = 'calc(calc(%fvw / 2.8) - 4px)'%hcards
        small   = False
        x_small = False
        large   = False
        x_large = False
        if self.board.scale < 0.4:
            x_small = True      
        elif self.board.scale < 0.5:
            small = True
        #elif self.board.scale > 0.65:
        #    large = True
        #elif self.board.scale > 0.8:
        #    large = True
        
        iScore   = v.Icon(right=True, children=['mdi-table'])
        iPlay    = v.Icon(right=True, children=['mdi-format-list-bulleted'])
        iChart   = v.Icon(right=True, children=['mdi-chart-line'])
        iMap     = v.Icon(right=True, children=['mdi-basketball'])
        iSummary = v.Icon(right=True, children=['mdi-sigma'])
        
        disabled = 'opponents' not in self.board.game.game_data
        self.bScore   = v.Btn(children=['Score Sheet', iScore],   x_small=x_small, small=small, large=large, x_large=x_large, width=bw, height=bh, color=settings.color_first, class_='mb-2', disabled=disabled)
        self.bPlay    = v.Btn(children=['Play-By-Play',iPlay],    x_small=x_small, small=small, large=large, x_large=x_large, width=bw, height=bh, color=settings.color_first, class_='mb-2', disabled=disabled)
        self.bChart   = v.Btn(children=['Points Chart',iChart],   x_small=x_small, small=small, large=large, x_large=x_large, width=bw, height=bh, color=settings.color_first, class_='mb-2', disabled=disabled)
        self.bThrows  = v.Btn(children=['Throws Map',  iMap],     x_small=x_small, small=small, large=large, x_large=x_large, width=bw, height=bh, color=settings.color_first, class_='mb-2', disabled=disabled)
        self.bSummary = v.Btn(children=['Game Summary',iSummary], x_small=x_small, small=small, large=large, x_large=x_large, width=bw, height=bh, color=settings.color_first, disabled=disabled)
        
        self.bScore.on_event(  'click', self.showScoreSheet)
        self.bPlay.on_event(   'click', self.showPlayByPlay)
        self.bChart.on_event(  'click', self.showChart)
        self.bThrows.on_event( 'click', self.showThrows)
        self.bSummary.on_event('click', self.showSummary)
        
        self.cbuttons.children = [self.bScore, self.bPlay, self.bChart, self.bThrows, self.bSummary]
        
        self.children = [ self.board, widgets.HBox([widgets.VBox([widgets.HBox(self.eventcards1), widgets.HBox(self.eventcards2)]), self.cbuttons]) ]
        
        self.layout = Layout(margin='0px 0px 0px 0px')
        
        
    def waitOpen(self):
        self.board.waitOpen()
        
    def waitClose(self):
        self.board.waitClose()
        
        
    # Disable controls when the game is over
    def gameover(self):
        
        for c in self.event_card_not_countable:
            c.disabled = True
        
        for event_id, c in self.event_card.items():
            if event_id in self.plus_buttons:
                plus  = self.plus_buttons[event_id]
                minus = self.minus_buttons[event_id]
                plus.disabled = True
                minus.disabled = True
            
        
    # Display the ScoreSheet
    def showScoreSheet(self, *args):
        self.board.tb.stop()
        
        # Download ScoreSheet in HTML format
        def on_download():
            html = BoxScore.html(self.df, game=self.board.game)

            filename = '%s-%s_ScoreSheet'%(self.board.team1_abbr,self.board.team2_abbr)
            if not self.board.tb.gameover:
                filename += '_Q%d'%self.board.quarter

            download.output.clear_output()
            with download.output:
                download.downloadText(html, fileName='%s.html'%filename)
            download.output.clear_output()
            
            # TODO: Generate the .html file inside the github repo and then view it like: https://html-preview.github.io/?url=https://github.com/DavideDeMarchi/voici-demo/blob/main/ScoreSheet.html
            
        
        w = (self.board.width + self.board.infow)*0.99
        
        self.waitOpen()
        self.svg = BoxScore.svg(self.df, game=self.board.game, width=w)
        self.waitClose()
        
        dialogGeneric.dialogGeneric(title='Score Sheet', text='', titleheight=26, dark=False,
                                    show=True, addclosebuttons=True, width='calc(%fvw + 4px)'%w,
                                    custom_icon='mdi-download', custom_tooltip='Click to download the Score Sheet', custom_icon_onclick=on_download,
                                    fullscreen=False, content=[HTML(self.svg)], output=self.board.output)

        
    # Display PlayByPlay in HTML format
    def showPlayByPlay(self, *args):
        self.board.tb.stop()
        
        # Download
        def on_download():
            filename = '%s-%s_PlayByPlay'%(self.board.team1_abbr,self.board.team2_abbr)
            if not self.board.tb.gameover:
                filename += '_Q%d'%self.board.quarter

            download.output.clear_output()
            with download.output:
                download.downloadText(self.playbyplay, fileName='%s.html'%filename)
            download.output.clear_output()
            
            # TODO: Generate the .html file inside the github repo and then view it like: https://html-preview.github.io/?url=https://github.com/DavideDeMarchi/voici-demo/blob/main/ScoreSheet.html
            
        
        w = (self.board.width + self.board.infow)*0.99
        
        self.waitOpen()
        self.playbyplay = BoxScore.play_by_play(self.df, game=self.board.game)
        html = '<div style="max-width: %fvw; max-height: 520px; overflow: auto; background-color: #ffffff;">%s</div>'%(w,self.playbyplay)
        self.waitClose()
        
        dlg = dialogGeneric.dialogGeneric(title='Play-By-Play', text='', titleheight=26, dark=False,
                                          show=True, addclosebuttons=True, width='calc(%fvw + 2px)'%w,
                                          custom_icon='mdi-download', custom_tooltip='Click to download the Play-By-Play report', custom_icon_onclick=on_download,
                                          fullscreen=False, content=[HTML(html)], output=self.board.output)

        
    # Display the Points Chart
    def showChart(self, *args):
        self.board.tb.stop()
        
        def on_download():
            bbb = self.fig.to_image('png', width=4000, height=1400)

            filename = '%s-%s_PointsChart'%(self.board.team1_abbr,self.board.team2_abbr)
            if not self.board.tb.gameover:
                filename += '_Q%d'%self.board.quarter
            
            download.output.clear_output()
            with download.output:
                download.downloadBytes(bbb, fileName='%s.png'%filename)
            download.output.clear_output()
            
        
        self.waitOpen()
        
        w = (self.board.width + self.board.infow)
        height_in_pixels = 450
        
        self.fig = BoxScore.pointsChart(self.df, game=self.board.game, height_in_pixels=height_in_pixels)
        
        out = widgets.Output(layout=Layout(width='%fvw'%w, height='%dpx'%(height_in_pixels+4)))
        out.add_class('black_background')
        with out:
            self.fig.show(config={'displayModeBar': False})
        self.waitClose()

        dlg = dialogGeneric.dialogGeneric(title='Points Chart', text='', titleheight=26, dark=False,
                                          show=True, addclosebuttons=True, width='calc(%fvw + 5px)'%w,
                                          custom_icon='mdi-download', custom_tooltip='Click to download the Points Chart', custom_icon_onclick=on_download,
                                          fullscreen=False, content=[out], output=self.board.output)
        dlg.dialog.children[0].color = 'black'
        
        
    # Display the ThrowMap
    def showThrows(self, *args):

        selected_player = 'Team'
        
        def on_download():
            
            # Save ThrowMap image in PNG format in bytes in memory 
            temp = io.BytesIO()
            m.imgBackground.save(temp, format="png")
            
            filename = '%s-%s_ThrowMap_%s'%(self.board.team1_abbr,self.board.team2_abbr, selected_player)
            
            download.output.clear_output()
            with download.output:
                download.downloadBytes(temp.getvalue(), fileName='%s.png'%filename)
            download.output.clear_output()
            
        
        def on_selected(widget, event, data):
            nonlocal selected_player
            if widget.outlined:
                selected_player = 'Team'
                m.updateThrows(self.board.game.events_df)
                widget.outlined = False
            else:
                selected_player = widget.children[0].children[0]
                m.updateThrows(self.board.game.events_df, selected_player)
                for w in cards1+cards2: w.outlined = False
                widget.outlined = True
                

        self.waitOpen()
                
        playerw = 'calc(%fvw - 43px)'%(self.board.width/5)
        if self.board.scale < 0.5:   playerw = 'calc(%fvw - 34px)'%(self.board.width/5)
        elif self.board.scale > 0.7: playerw = 'calc(%fvw - 26px)'%(self.board.width/6.2)
        widget1,cards1 = self.board.game.playersList(self.board.game.players_by_number[:6], onclick=on_selected, single_line=False, show_info=True, one_line_if_less_than=0, w=playerw)
        widget2,cards2 = self.board.game.playersList(self.board.game.players_by_number[6:], onclick=on_selected, single_line=False, show_info=True, one_line_if_less_than=4, w=playerw, initial_id=len(cards1))

        if self.board.scale < 0.5:
            scale = 0.688
            wscale = 0.82
        elif self.board.scale < 0.6:
            scale = 0.91
            wscale = 0.827
        elif self.board.scale < 0.7:
            scale = 1.168
            wscale = 0.844
        else:
            scale = 1.38
            wscale = 0.775
        
        m = ThrowMap.ThrowMap(board=self.board, scale=scale, field_left=True, output=self.board.output)
        m.updateThrows(self.board.game.events_df)
        
        spacerY = v.Html(tag='div',children=[' '], style_='width: 1000px; height: 5px; background-color: %s;'%self.board.tb.color_back)
        wplayer = (self.board.width/5)*0.8
        
        out = widgets.Output()
        out.add_class('black_background')
        with out:
            display(widgets.HBox([ widgets.VBox([widget1, spacerY, widget2], layout=Layout(max_width='calc(%fvw * 3)'%wplayer)), m]))
        
        w = (self.board.width + self.board.infow)*wscale

        self.waitClose()
        
        dlg = dialogGeneric.dialogGeneric(title='Throw Map', text='', titleheight=26, dark=False,
                                          show=True, addclosebuttons=True, width='%fvw'%w,
                                          custom_icon='mdi-download', custom_tooltip='Click to download the Throw Map', custom_icon_onclick=on_download,
                                          fullscreen=False, content=[out], output=self.board.output)
        dlg.dialog.children[0].color = 'black'
            
            
    # Display the Summary
    def showSummary(self, *args):
        self.board.tb.stop()
        
        def on_text_changed(*args):
            ic.text = str(ta.v_model)
        
        # Download Summary in .txt format
        def on_download():
            filename = '%s-%s_Summary'%(self.board.team1_abbr,self.board.team2_abbr)
            if not self.board.tb.gameover:
                filename += '_Q%d'%self.board.quarter

            download.output.clear_output()
            with download.output:
                download.downloadText(str(ta.v_model), fileName='%s.txt'%filename)
            download.output.clear_output()
            
        w = (self.board.width + self.board.infow)*0.9
        
        self.summary = BoxScore.summary(self.df, game=self.board.game)
       
        taid = 'textarea_id_%d'%randrange(100000)
        ta = v.Textarea(id=taid, auto_grow=False, color=settings.color_first, rows=13, clearable=False, no_resize=True, dense=True, outlined=True, class_='pa-0 ma-0 mt-2')
        ta.v_model = self.summary
        ta.on_event('input', on_text_changed)

        # Icon to copy to the clipboard
        ic = IconClipboard(self.board.output, margins='pa-0 ma-0 ml-2', x_large=True, tooltip='Copy summary to clipboard')
        ic.text = self.summary

        c = v.Card(flat=True, children=[ta], class_='pa-0 pl-3 pr-3')
        
        dlg = dialogGeneric.dialogGeneric(title='Game Summary', text='', titleheight=26, dark=False,
                                          show=True, addclosebuttons=True, width='calc(%fvw + 4px)'%w,
                                          custom_icon='mdi-download', custom_tooltip='Click to download the Game Summary', custom_icon_onclick=on_download,
                                          fullscreen=False, content=[widgets.VBox([ic, c])], output=self.board.output)
        dlg.dialog.children[0].color = 'black'
        
        # Remove the spellcheck property from the textarea!!!
        with self.board.output:
            display(ipyHTML('<script>editor = document.getElementById("%s"); editor.spellcheck = false;</script>'%ta.id))

            
    # Called at the start of each quarter
    def on_quarter_start(self):
        
        # Remove all 'Entr' events at the beginning of the current quarter
        startseconds = 600.0
        if self.board.quarter > 4: startseconds = 300.0
        df = self.df[(self.df['team']==Config.TEAM)&(self.df['quarter']==self.board.quarter)&(self.df['seconds']==startseconds)&(self.df['event']=='Entr')]
        for evid in df.index:
            self.df.drop(evid, inplace=True)
        
        # Add 'Entr' event for the players on the field
        for player_name in self.game.on_field:
            self.storeEvent(player_name, 18)

        
    # Called at the end of each quarter
    def on_quarter_end(self):
        
        # Add 'Usci' event for the players on the field
        for player_name in self.game.on_field:
            self.storeEvent(player_name, 19)
            
            
    # Called when a game is loaded
    def on_game_loaded(self):
        self.df = self.game.events_df

        self.board.player_selected = None
        self.on_player_selected()
        
        self.board.after_game_loaded()
        
        
        
    # Add an event to the pandas dataframe of events
    def storeEvent(self, player_name, event_id, x=0, y=0, team=Config.TEAM):
        if self.df.shape[0] > 0:
            evid = max(self.df.index) + 1
        else:
            evid = 0

        if player_name is None:
            player_name = Config.TEAM

        if not 'time' in self.df.columns:
            self.df["time"] = ""
            
        d = datetime.datetime.today()
            
        self.df.loc[evid] = [team, player_name, event_id, Config.EVENT_NAME[event_id], Config.EVENT_DESCRIPTION[event_id], self.board.quarter, self.board.seconds, x, y, d.strftime('%Y-%m-%d %H:%M:%S')]
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
    def selectPlayerToEnter(self, addclosebuttons=False):
        def onselect(player_name):
            self.board.toField(player_name, position=self.board.player_index)
            self.storeEvent(player_name, 18)

        self.game.selectFromBench(onselect=onselect, addclosebuttons=addclosebuttons)
        
        
    # Fire an uncountable event ("go to field" or "go to bench")
    def click_fire(self, event_id):
        
        # Selection of a player to go on the field
        if event_id == 18:
            self.selectPlayerToEnter(addclosebuttons=True)
            
        # Uscita dal campo
        elif event_id == 19:
            player_name = self.board.player_selected
            self.storeEvent(player_name, event_id)
            self.board.toBench(player_name)

            self.selectPlayerToEnter(addclosebuttons=True)
        
        
    # Called when one of the player on the field is selected from the board
    def on_player_selected(self):
        
        if self.board.player_selected is None:               # No players selected --> Events go to the Team
            for c in self.eventcards1+self.eventcards2:
                if Config.EVENT_TEAM[c.id]: c.disabled = False
                else:                       c.disabled = True
                self.update(c.id)
        elif self.board.player_selected == '':               # Empty player selected: only "Entrata in campo" is enabled
            for c in self.eventcards1+self.eventcards2:
                if c.id == 18 and not self.board.tb.gameover:  c.disabled = False
                else:                                          c.disabled = True
                self.update(c.id)
        else:
            for c in self.eventcards1+self.eventcards2:      # Normal player selected: only "Entrata in campo" is disabled
                if c.id == 18:  c.disabled = True
                else:
                    if c.id == 19 and self.board.tb.gameover:
                        c.disabled = True
                    else:
                        c.disabled = False
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
            plus  = self.plus_buttons[event_id]
            minus = self.minus_buttons[event_id]

            player = self.board.player_selected
            if player is None:
                df = self.df[(self.df['team']==Config.TEAM)&(self.df['event']==event_id)]
            else:
                df = self.df[(self.df['team']==Config.TEAM)&(self.df['player']==player)&(self.df['event']==event_id)]

            if self.board.tb.gameover:
                plus.disabled = True
            else:
                plus.disabled = False

            if df.shape[0] == 0:
                html.children = ['']
                minus.disabled = True
            else:
                html.children  = [str(df.shape[0])]
                
                if self.board.tb.gameover:
                    minus.disabled = True
                else:
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
        
        dogameover = False
        if self.board.tb.gameover:
            dogameover = True
            
        self.createControls()
        if dogameover:
            self.board.tb.gameover  = dogameover
            self.board.pb1.gameover = dogameover
            self.board.pb2.gameover = dogameover
            self.gameover()
    
    # Scaling called from the ScoreBoard
    def on_scaling(self, scale):
        self.scale = scale