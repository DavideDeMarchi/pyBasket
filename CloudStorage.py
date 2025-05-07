"""Manage read and write of files on a cloud storage (pCloud)"""
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
import ipyvuetify as v
from vois.vuetify import settings, dialogMessage, dialogGeneric
from pcloud import PyCloud
from pcloud.api import AuthenticationError


###########################################################################################################################################################################
# CloudStorage
###########################################################################################################################################################################
class CloudStorage():
    
    # Initialization
    def __init__(self, output):
        self.output = output
        self.pc = None
        self.folderpath = '/'
        self.gamefiles = []
        self.teamfile = ''
    
    # Connect to a pCloud instance
    def connect(self):
        
        def on_ok():
            try:
                self.pc = PyCloud('davide.demarchi@yahoo.it', tfp.v_model, endpoint="eapi")
            except AuthenticationError as e:
                errorcode = str(e)
                dlg = dialogMessage.dialogMessage(title='Error',
                                                  titleheight=30,
                                                  text='Cannot connect to pCloud storage server!\n\nError: %s'%errorcode,
                                                  addclosebuttons=True,
                                                  show=True, width=450, output=self.output)

        tfp = v.TextField(v_model='', autofocus=True, type='password', label='Insert password', color=settings.color_first, dense=False, class_="pa-0 ma-0 ml-8 mr-8")
        dlg = dialogGeneric.dialogGeneric(title='pCloud Storage access',
                                          text=' ', titleheight=30,
                                          show=True, addclosebuttons=True, width=460,
                                          addokcancelbuttons=True, on_ok=on_ok,
                                          fullscreen=False, content=[tfp], output=self.output)
        
        
    
    # Open a folder on the cloud storage
    def open(self, folderpath):
        self.folderpath = '/'
        self.gamefiles = []
        
        if self.pc is None:
            print('Not connected!')
            
        res = self.pc.listfolder(path=folderpath)
        if 'metadata' in res:
            metadata = res['metadata']
            
            if 'path' in metadata and 'isfolder' in metadata and metadata['isfolder'] and 'contents' in metadata:
                contents = metadata['contents']
                self.folderpath = folderpath
                for c in contents:
                    if not c['isfolder'] and 'name' in c and c['name'][-5:] == '.game':
                        self.gamefiles.append(c['name'])
                    elif not c['isfolder'] and 'name' in c and c['name'][-5:] == '.team':
                        self.teamfile = c['name']
        

