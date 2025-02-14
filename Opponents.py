"""Edit info on opponents team players"""
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

# vois imports
from vois.vuetify import settings, sortableList, tooltip, dialogGeneric, dialogYesNo, Button

import SelectGame
import Game


###########################################################################################################################################################################
# Opponents class to edit info on opponents team players
###########################################################################################################################################################################
class Opponents():
    
    def __init__(self, board):    # Instance of ScoreBoard class
        
        self.board = board
        
        self.reset = v.Btn(icon=True, children=[v.Icon(children=['mdi-playlist-remove'])])
        self.reset.on_event('click', self.itemRemoveAll)

        self.spacer = v.Html(tag='div', class_="pa-0 ma-0 mr-6", children=[''])
        
        labelName   = v.Html(tag='div', class_="pa-0 ma-0 mr-6 mt-2 mb-n1", style_="width: 200px; font-weight: 700;", children=['Name'])
        labelNumber = v.Html(tag='div', class_="pa-0 ma-0 mr-6 mt-2 mb-n1", style_="width: 80px;  font-weight: 700;", children=['Number'])
        labelYear   = v.Html(tag='div', class_="pa-0 ma-0 mr-6 mt-2 mb-n1", style_="width: 80px;  font-weight: 700;", children=['Year'])
        labelFouls  = v.Html(tag='div', class_="pa-0 ma-0 mr-6 mt-2 mb-n1", style_="width: 50px;  font-weight: 700;", children=['Fouls'])
        labelPoints = v.Html(tag='div', class_="pa-0 ma-0 mr-6 mt-2 mb-n1", style_="width: 60px;  font-weight: 700;", children=['Points'])
        
        self.items = self.board.game.opponents
        
        # Add 12 opponents empty records
        if len(self.items) == 0:
            for i in range(12):
                self.items.append({"name": "", "number": "0", "year": "", "fouls": 0, "points": 0})
        
        b1 = Button('Import players from a string', text_weight=550, on_click=self.onImportFromString, width=320, height=38, text_color=settings.color_first,
                    tooltip='Import the opponents from a comma separated string (i.e. from the summary of a previous game)', outlined=True, rounded=False)
        
        b2 = Button('Import players from a game', text_weight=550, on_click=self.onImportFromGame, width=320, height=38, text_color=settings.color_first,
                    tooltip='Import the opponents from another game (i.e. the game with the same opponents on the previous phase)', outlined=True, rounded=False)
        
        buttons = v.Row(class_="pa-0 ma-0 ml-5 mr-3 mt-2", no_gutters=True, align='center', justify='space-around', style_='overflow: hidden;', dense=True, children=[b1, b2])
        header  = v.Row(class_="pa-0 ma-0 ml-5 mr-3", no_gutters=True, style_='overflow: hidden;', dense=True, children=[labelName, labelNumber, labelYear, labelFouls, labelPoints])

        self.sortablelist = sortableList.sortableList(items=self.items,
                                                      width=700,
                                                      outlined=False,
                                                      dark=False,
                                                      allowNew=True,
                                                      itemNew=self.itemNew,
                                                      itemContent=self.itemContent,
                                                      bottomContent=[tooltip.tooltip("Remove all players", self.reset)],
                                                      tooltipadd='Add new player',
                                                      buttonstooltip=True)
        self.sortablelist.style_ = 'overflow: hidden;'
        self.sortablelist.output.style_ = 'overflow: hidden;'
        self.sortablelist.output.class_ = 'ma-0 ml-3 mr-3'
        self.sortablelist.outputplus.class_ = 'ma-0 ml-3 mr-3'

        self.dlg = dialogGeneric.dialogGeneric(title='Edit opponents team players',
                                               text='', titleheight=26,
                                               show=True, addclosebuttons=True, width=720,
                                               addokcancelbuttons=True, on_ok=self.on_ok,
                                               fullscreen=False, content=[widgets.VBox([buttons, header, self.sortablelist.draw()])], output=self.board.output)
        
        
    # Impost opponents from a string
    def onImportFromString(self, *args):
        
        def on_ok():
            a = tf.v_model.replace('.','').split(',')
            self.items = []
            for elem in a:
                elem.replace('ne','').replace('Ne','').replace('NE','').replace('nE','').replace('n.e.','').replace('N.e.','')
                elem = elem.strip()
                if ' ' in elem:
                    aaa = elem.split(' ')[:-1]
                    elem = ' '.join(aaa)
                    
                self.items.append({"name": elem, "number": "0", "year": "", "fouls": 0, "points": 0})
            self.sortablelist.items = self.items    
        
        
        tf = v.TextField(v_model='', autofocus=True, label='Opponents players string', color=settings.color_first, dense=True, class_="pa-0 ma-0 mt-8 ml-3 mr-3")
        dlg = dialogGeneric.dialogGeneric(title='Import opponents players from a string',
                                          text='', titleheight=26,
                                          show=True, addclosebuttons=True, width=920,
                                          addokcancelbuttons=True, on_ok=on_ok,
                                          fullscreen=False, content=[tf], output=self.board.output)
    
    
    # Impost opponents from another game
    def onImportFromGame(self, *args):
        
        def on_ok(selected_path):
            othergame = Game.Game(board=self.board, team_file=self.board.team_file, game_file=selected_path)
            self.items = []
            for player_name in othergame.opponents_by_number:
                item = othergame.opponents_info[player_name].copy()
                item['fouls'] = 0
                item['points'] = 0
                self.items.append(item)
            self.sortablelist.items = self.items
    
        s = SelectGame.SelectGame(output=self.board.output, on_ok=on_ok, title='Select a Game')
    
    
    # Exit with OK button
    def on_ok(self):
        
        # Fill missing info (numbers, years, etc...)
        items = []
        for item in self.items:
            if item['name'] != '':
                if item['number'] == '': item['number'] = '0'
                items.append(item)
        
        self.board.game.opponents = items
        self.board.game.saveGame()
        
        
    # Creation of a new item
    def itemNew(self):
        self.sortablelist.items = self.items   # V.I. to preserve the edits!!!
        return { "name": "", "number": "", "year": "", "fouls": 0, "points": 0 }


    # Remove all items
    def itemRemoveAll(self, widget, event, data):

        def on_yes():
            self.items = []
            self.sortablelist.items = self.items

        dialogYesNo.dialogYesNo(title='Please confim', text='Confirm removal of all the players?', titleheight=40, width=400, output=self.board.output, show=True, on_yes=on_yes)


    # Content of an item
    def itemContent(self, item, index):

        def onname(widget, event, data):
            item["name"] = data

        def onnumber(widget, event, data):
            item["number"] = data

        def onyear(widget, event, data):
            item["year"] = data

        def onfouls(widget, event, data):
            if not isinstance(data, dict):
                f = int(data)
                if f < 0: f = 0
                if f > 5: f = 5
                widget.v_model = f
                item["fouls"] = f

        def onpoints(widget, event, data):
            if not isinstance(data, dict):
                f = int(data)
                if f < 0: f = 0
                if f > 100: f = 100
                widget.v_model = f
                item["points"] = f

        tfname = v.TextField(value=item['name'], color=settings.color_first, dense=True, style_="max-width: 200px", class_="pa-0 ma-0 mb-n4")
        tfname.on_event('input', onname)

        tfnumber = v.TextField(value=item['number'], color=settings.color_first, dense=True, style_="max-width: 80px", class_="pa-0 ma-0 mb-n4")
        tfnumber.on_event('input', onnumber)

        tfyear = v.TextField(value=item['year'], color=settings.color_first, dense=True, style_="max-width: 80px", class_="pa-0 ma-0 mb-n4")
        tfyear.on_event('input', onyear)

        tffouls = v.TextField(v_model=item['fouls'], type='number', color=settings.color_first, dense=True, style_="max-width: 50px", class_="pa-0 ma-0 mb-n4")
        tffouls.on_event('input', onfouls)

        tfpoints = v.TextField(v_model=item['points'], type='number', color=settings.color_first, dense=True, style_="max-width: 60px", class_="pa-0 ma-0 mb-n4")
        tfpoints.on_event('input', onpoints)

        return [ v.Row(class_="pa-0 ma-0 ml-2", no_gutters=True, dense=True, children=[tfname, self.spacer, tfnumber, self.spacer, tfyear, self.spacer, tffouls, self.spacer, tfpoints]) ]

