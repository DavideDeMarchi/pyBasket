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

import zipfile
import io
import json
import uuid
import os


###########################################################################################################################################################################
# CloudStorage
###########################################################################################################################################################################
class CloudStorage():
    
    # Initialization
    def __init__(self, output):
        self.output = output
        self.pc = None
        self.folderpath = '/'
        
        self.gamefiles_names = []
        self.gamefiles_ids   = []
        self.teamfile_name   = ''
        self.teamfile_id     = 0
    
    
    # Connect to a pCloud instance
    def connect(self):
    
        try:
            with open("CloudStorage.pass","r") as f:
                password = f.read().replace('\n','')
                
                try:
                    self.pc = PyCloud('davide.demarchi@yahoo.it', password, endpoint="eapi")
                except AuthenticationError as e:
                    errorcode = str(e)
                    dlg = dialogMessage.dialogMessage(title='Error',
                                                      titleheight=30,
                                                      text='Cannot connect to pCloud storage server!\n\nError: %s'%errorcode,
                                                      addclosebuttons=True,
                                                      show=True, width=450, output=self.output)
        except:
    
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
        
        self.gamefiles_names = []
        self.gamefiles_ids   = []
        self.teamfile_name   = ''
        self.teamfile_id     = 0
        
        if self.pc is None:
            print('Not connected!')
            
        res = self.pc.listfolder(path=folderpath)
        if 'metadata' in res:
            metadata = res['metadata']
            
            if 'path' in metadata and 'isfolder' in metadata and metadata['isfolder'] and 'contents' in metadata:
                contents = metadata['contents']
                self.folderpath = folderpath
                for c in contents:
                    if not c['isfolder'] and 'name' in c and 'id' in c and c['name'][-5:] == '.game':
                        self.gamefiles_names.append(c['name'])
                        self.gamefiles_ids.append(int(c['id'][1:]))
                    elif not c['isfolder'] and 'name' in c and 'id' in c and c['name'][-5:] == '.team':
                        self.teamfile_name = c['name']
                        self.teamfile_id   = int(c['id'][1:])
        
        

    # Read a file from the cloud storage
    def read(self, fileid, filename):
        buffer = self.pc.getzip(fileids=[fileid])
        z = zipfile.ZipFile(io.BytesIO(buffer))
        foo = z.read(filename)
        data = json.loads( foo.decode() )
        return data
    
    
    # Read data for a game: returns a dictionary
    def readGame(self, gamefilename):
        if gamefilename in self.gamefiles_names:
            pos = self.gamefiles_names.index(gamefilename)
            game = self.read(fileid=self.gamefiles_ids[pos], filename=gamefilename)
            return game
        
        if self.pc is None:
            print('Not connected!')
        else:
            print('Game %s not found'%gamefilename)

        
    # Read team data: returns a dictionary
    def readTeam(self):
        if len(self.teamfile_name) > 0:
            team = self.read(fileid=self.teamfile_id, filename=self.teamfile_name)
            return team
        
        if self.pc is None:
            print('Not connected!')
        else:
            print('Team file %s not found'%self.teamfile_name)
        

    # Write data for a game
    def writeGame(self, gamefilename, gamedata):
        if self.pc is None:
            print('Not connected!')
        elif gamefilename not in self.gamefiles_names:
            print('Game %s not in games list'%gamefilename)
        else:
            #filepath = '/tmp/' + uuid.uuid4().hex + '.txt'
            filepath = '/tmp/' + gamefilename

            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(gamedata, f, ensure_ascii=False, indent=4)

                self.pc.uploadfile(files=[filepath], path=self.folderpath, nopartial='1')
                
            except:
                print('Error in writeGame')
        
            if os.path.isfile(filepath):
                os.unlink(filepath)

                
    # Write data for the team
    def writeTeam(self, teamdata):
        if self.pc is None:
            print('Not connected!')
        elif len(self.teamfile_name) == 0:
            print('Team file not read! Need to open a folder to have it.')
        else:
            #filepath = '/tmp/' + uuid.uuid4().hex + '.txt'
            filepath = '/tmp/' + self.teamfile_name

            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(teamdata, f, ensure_ascii=False, indent=4)

                self.pc.uploadfile(files=[filepath], path=self.folderpath, nopartial='1')
                
            except:
                print('Error in writeTeam')
        
            if os.path.isfile(filepath):
                os.unlink(filepath)
