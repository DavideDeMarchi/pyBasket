"""Select file .game to load"""
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
import glob
import os

# vois imports
from vois.vuetify import dialogGeneric, selectSingle, tabs


###########################################################################################################################################################################
# SelectGame class
###########################################################################################################################################################################
class SelectGame():
    
    def __init__(self, output, folder='./data', on_ok=None, title='Load a Game'):
        self.output = output
        self.on_ok  = on_ok
        
        # Conversion to int without errors
        def toint(x):
            try:
                return int(x)
            except:
                return 999999
            
        spacer = v.Html(tag='div', style_='width: 20px; height: 50px;', children=[''])
        
        allfiles = glob.glob('./data/*.game')
        self.phases = sorted(list(set([os.path.basename(x).split('-')[1] for x in allfiles if '-' in x and '.a-' in x])))
        
        self.cards = []
        self.sels  = []
        for phase in self.phases:

            # File of the phase
            files = [x for x in allfiles if phase in x and os.path.basename(x).split('-')[1] == phase]

            # Sort on increasing phase + round
            rounds = [toint(os.path.basename(x).split('.')[0]) for x in files]
            files  = [file for r, file in sorted(zip(rounds, files))]

            sel = selectSingle.selectSingle('Select the game to load (%s):'%phase,
                                            files,
                                            selection='',
                                            width=700,
                                            onchange=self.onselect)
            c = v.Card(flat=True, children=[sel.draw(), spacer], class_='pa-0 ma-0 mt-5')
            self.cards.append(c)
            self.sels.append(sel)

        self.t = tabs.tabs(0, self.phases, contents=self.cards, onchange=self.onChangePhase, row=True)
        self.t.tabswidget.class_ = 'pa-0 ma-0 ml-4'

        self.dlg = dialogGeneric.dialogGeneric(title=title,
                                               text=' ', titleheight=26,
                                               show=True, addclosebuttons=True, width=760,
                                               addokcancelbuttons=True, on_ok=self._on_ok,
                                               fullscreen=False, content=[self.t.draw()], output=self.output)
        self.dlg.dialog.children[0].style_ = 'overflow: hidden;'
        self.dlg.okdisabled = True
        
        
    # Change of the championship phase
    def onChangePhase(self, index):
        sel = self.sels[index]
        self.dlg.okdisabled = sel.value is None or len(sel.value) == 0

    # Selection of one of the .game files
    def onselect(self):
        self.dlg.okdisabled = False
        
    # Exit with OK button
    def _on_ok(self):
        if self.on_ok is not None:
            sel = self.sels[self.t.value]
            self.on_ok(sel.value)
