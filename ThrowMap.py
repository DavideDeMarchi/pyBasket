"""Input position of throws and displays all throws of player or team"""
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
from PIL import Image, ImageDraw, ImageFont
from ipyevents import Event
import math
import pandas as pd

# vois imports
from vois import colors
from vois.vuetify import dialogGeneric

# local imports
import Stats
import Config

# Form Factor and background image dimensions
FORM_FACTOR         = 1.0
IMAGE_HEIGHT_PIXELS = 1050
IMAGE_WIDTH_PIXELS  = 856


###########################################################################################################################################################################
# ThrowMap class
###########################################################################################################################################################################
class ThrowMap(widgets.VBox):
    
    def __init__(self,
                 board,                   # Instance of ScoreBoard
                 width=25.0,              # Dimension in percentage of the screen width
                 scale=1.0,               # Overall scaling
                 color_back='#000000',    # Background color
                 field_left=True,         # Basket is on the left of the screen
                 output=None):            # Output to display CSS and dialog
    
        super().__init__()
        
        self.board = board
        self.game  = self.board.game
        
        self._scale = scale
        self._width  = width
        self._height = FORM_FACTOR * width * IMAGE_HEIGHT_PIXELS / IMAGE_WIDTH_PIXELS
        self._width  *= self._scale
        self._height *= self._scale
        
        self.color_back  = color_back
        self._field_left = field_left
        
        self.mode = 1       # 1=display full field,  2=display 2 points area,  3=display 3 points area
        
        self.output = output
        
        self.debug = widgets.Output()
        
        self.dlg = None
        
        self.onclick  = None
        self.argument = None
        self.scored   = True
        
        # Current player ad throws displayed in the background map
        self.current_player = ''
        self.current_df     = None

        # Images for scored and missed throws
        self.imgScored = Image.open('./resources/scored.png')
        self.imgMissed = Image.open('./resources/missed.png')
        
        self.createControls()

        
    # Creation of the controls
    def createControls(self):

        # Pixels to add to the output Widget in order to not see the scrollbars
        self.added_pixels_width  = 5
        self.added_pixels_height = 5

        # Output widget to display all the throws
        self.outdraw = widgets.Output(layout=Layout(width= '%fvw'%self._width,
                                                    height='%fvw'%self._height,
                                                    margin='0px 0px 0px 0px'))
        self.outdraw.add_class('black_background')

        self.imgBackground = self.background_image(self.mode)
        self.img = v.Img(width='calc(%fvw - %dpx)'%(self._width, self.added_pixels_width), height='calc(%fvw - %dpx)' % (self._height,self.added_pixels_height),
                         contain=True, src=colors.image2Base64(self.imgBackground), style_='background-color: black;')
        with self.outdraw:
            display(self.img)
            
        self.imgSelect = None

        # Create the Event manager
        dh = Event(source=self.outdraw, watched_events=['click'])
        dh.on_dom_event(self.handle_event_background)
        
        self.children = [self.outdraw]

     
    # Returns the PIL image to show as background
    def background_image(self, mode):
        if self.field_left:
            if mode == 2:
                img = Image.open('./resources/MappaTiroL2.png')
            elif mode == 3:
                img = Image.open('./resources/MappaTiroL3.png')
            else:
                img = Image.open('./resources/MappaTiroL.png')
        else:
            if mode == 2:
                img = Image.open('./resources/MappaTiroR2.png')
            elif mode == 3:
                img = Image.open('./resources/MappaTiroR3.png')
            else:
                img = Image.open('./resources/MappaTiroR.png')
                
        return img
    
    
    # Select a point
    def select(self,
               mode=2,
               df=None,          # Optional Pandas Dataframe of events to display player previous throws
               width=25.0,       # Dimension in percentage of the screen width
               scale=1.0,        # Overall scaling
               onclick=None,
               argument=None,
               scored=True):
        
        w  = width
        h = FORM_FACTOR * w * IMAGE_HEIGHT_PIXELS / IMAGE_WIDTH_PIXELS
        w *= scale
        h *= scale
        
        self.mode_select = mode
        self.onclick     = onclick
        self.argument    = argument
        self.scored      = scored
        
        if self.dlg is not None:
            self.dlg.close()
            self.imgSelect = None
            
        # Output widget to capture the click event
        self.outselect = widgets.Output(layout=Layout(width= 'calc(%fvw + %dpx)' % (w,self.added_pixels_width), 
                                      height='calc(%fvw + %dpx)' % (h,self.added_pixels_height),
                                      margin='0px 0px 0px 0px')) #, border='1px solid red'))
        self.outselect = widgets.Output(layout=Layout(width= '%fvw'%w, 
                                                      height='%fvw'%h,
                                                      margin='0px 0px 0px 0px'))
        self.outselect.add_class('black_background')
        
        # Create the Event manager
        dh = Event(source=self.outselect, watched_events=['click'])
        dh.on_dom_event(self.handle_event_select)        
            
        self.imgSelectBackground = self.background_image(mode)
        self.imgSelect = v.Img(width='calc(%fvw - %dpx)'%(w, self.added_pixels_width), height='calc(%fvw - %dpx)' % (h,self.added_pixels_height),
                               contain=True, src=colors.image2Base64(self.imgSelectBackground), style_='background-color: black;')
        with self.outselect:
            display(self.imgSelect)
            
        if df is not None:
            self.updateThrows(df, self.argument[0], background=False)
            
        self.dlg = dialogGeneric.dialogGeneric(title='Select throw position', text='', titleheight=26,
                                               show=True, addclosebuttons=True, width='%fvw'%w,
                                               fullscreen=False, content=[self.outselect], output=self.output)
    
    
    # Reset empty background image
    def reset(self):
        self.imgBackground = self.background_image(self.mode)
        self.img.src = colors.image2Base64(self.imgBackground)
        
    
    # Display a list of throws from a Pandas Dataframe
    def displayThrows(self, tdf, background=True):
        if background:
            back_image = self.imgBackground
        else:
            back_image = self.imgSelectBackground
            
        w,h = back_image.size
        for index, row in tdf.iterrows():
            if row['event'] in [2,3,4,5]:
                if row['event'] in [2,4]: img = self.imgScored
                else:                     img = self.imgMissed
                iw,ih = img.size
                x = row['x']
                y = row['y']
                if not self.field_left: x = 100.0 - x
                px = int(w*x/100.0) - iw//2
                py = int(h*y/100.0) - ih//2
                back_image.paste(img, (px,py), img)
            
        # Display stats on top
        if background :
            if self.current_df is not None:
                
                def stat(ok, err):
                    s = '%d/%-d'%(ok,ok+err)
                    if ok+err ==0:
                        return s,''
                    else:
                        return s, '%d%%'%round(100.0*ok/(ok+err))
                
                T1ok  = self.current_df[(self.current_df['team']==Config.TEAM)&(self.current_df['event_name']=='T1ok') ].shape[0]
                T1err = self.current_df[(self.current_df['team']==Config.TEAM)&(self.current_df['event_name']=='T1err')].shape[0]
                T2ok  = self.current_df[(self.current_df['team']==Config.TEAM)&(self.current_df['event_name']=='T2ok') ].shape[0]
                T2err = self.current_df[(self.current_df['team']==Config.TEAM)&(self.current_df['event_name']=='T2err')].shape[0]
                T3ok  = self.current_df[(self.current_df['team']==Config.TEAM)&(self.current_df['event_name']=='T3ok') ].shape[0]
                T3err = self.current_df[(self.current_df['team']==Config.TEAM)&(self.current_df['event_name']=='T3err')].shape[0]
                
                w,h = back_image.size
                draw = ImageDraw.Draw(back_image)

                textcolor = "black"
                fontsize  = 25

                fontBold   = ImageFont.truetype('fonts/Roboto-Bold.ttf',    fontsize)
                fontNormal = ImageFont.truetype('fonts/Roboto-Regular.ttf', fontsize)

                name = 'Team'
                if self.current_player is not None: name = self.current_player

                if self.field_left:
                    x1 = (w*2)//3 - 26
                    x2 = x1 + 36
                    x3 = x2 + 74
                else:
                    x1 = 10
                    x2 = x1 + 40
                    x3 = x2 + 74
                    
                y = 10
                dy = 30
                draw.text((x1,y), name, textcolor, font=fontBold)
                y += 6
                
                # Display scored and missed
                s,p = stat(T1ok,T1err)
                draw.text((x1,y+1*dy), 'T1', textcolor, font=fontNormal)
                draw.text((x2,y+1*dy), s,    textcolor, font=fontNormal)
                draw.text((x3,y+1*dy), p,    textcolor, font=fontNormal)
                
                s,p = stat(T2ok,T2err)
                draw.text((x1,y+2*dy), 'T2', textcolor, font=fontNormal)
                draw.text((x2,y+2*dy), s,    textcolor, font=fontNormal)
                draw.text((x3,y+2*dy), p,    textcolor, font=fontNormal)

                s,p = stat(T3ok,T3err)
                draw.text((x1,y+3*dy), 'T3', textcolor, font=fontNormal)
                draw.text((x2,y+3*dy), s,    textcolor, font=fontNormal)
                draw.text((x3,y+3*dy), p,    textcolor, font=fontNormal)
                
                # Display additional stats for the current player
                if not self.field_left:
                    x2 = x1
                    x3 = x1 + 60
                    
                y += 8
                draw.text((x2,y+4*dy), 'P:', textcolor, font=fontNormal)
                draw.text((x3,y+4*dy), '%d'%Stats.points(self.current_df, self.current_player), textcolor, font=fontNormal)
                    
                draw.text((x2,y+5*dy), 'VAL:', textcolor, font=fontNormal)
                draw.text((x3,y+5*dy), '%d'%Stats.value(self.current_df, self.current_player), textcolor, font=fontNormal)

                draw.text((x2,y+6*dy), 'OER:', textcolor, font=fontNormal)
                draw.text((x3,y+6*dy), '%.2f'%Stats.oer(self.current_df, self.current_player), textcolor, font=fontNormal)

                draw.text((x2,y+7*dy), 'VIR:', textcolor, font=fontNormal)
                draw.text((x3,y+7*dy), '%.2f'%Stats.vir(self.current_df, self.current_player, self.game.players_info), textcolor, font=fontNormal)
                    
                draw.text((x2,y+8*dy), '+/-:', textcolor, font=fontNormal)
                draw.text((x3,y+8*dy), '%d'%Stats.plusminus(self.current_player, self.game.players_info), textcolor, font=fontNormal)
                    
                draw.text((x2,y+9*dy), 'TS:', textcolor, font=fontNormal)
                draw.text((x3,y+9*dy), '%.0f%%'%Stats.trueshooting(self.current_df, self.current_player), textcolor, font=fontNormal)
                    
                    
                # Display points per quarters
                if self.field_left: x2 -= 16
                else:               x2 = x1
                y = h - dy - 6
                dy = 26
                sq = self.game.pointsPerQuarter()
                for s in sq[::-1]:
                    draw.text((x2,y), s, textcolor, font=fontNormal)
                    y -= dy
                
        
        
    # Update of the throw map from the events stored in the Pandas Dataframe
    def updateThrows(self, df, player_name=None, background=True):
        if df is not None and 'team' in df.columns:
            self.current_player = ''
            self.current_df     = None

            if background: 
                self.imgBackground = self.background_image(self.mode)

            if player_name is None:                   # No players selected --> Throws for the Team
                tdf = df[(df['team']==Config.TEAM)]
                if background:
                    self.current_player = None
                    self.current_df     = tdf.copy()
                self.displayThrows(tdf, background=background)
            elif player_name == '':                   # Empty player selected --> no Throws displayed
                pass
            else:                                     # Normal player selected --> player's trows displayed
                tdf = df[(df['team']==Config.TEAM)&(df['player']==player_name)]
                if background:
                    self.current_player = player_name
                    self.current_df     = tdf.copy()
                self.displayThrows(tdf, background=background)

            if background:
                self.img.src = colors.image2Base64(self.imgBackground)
            else:
                self.imgSelect.src = colors.image2Base64(self.imgSelectBackground)
        
        
    # Add a throw on top of the background image for the selection dialog
    def addThrowSelect(self, x, y, scored=True):
        if scored: img = self.imgScored
        else:      img = self.imgMissed
        iw,ih = img.size

        if self.imgSelect is not None:
            w,h = self.imgSelectBackground.size

            px = int(w*x/100.0) - iw//2
            py = int(h*y/100.0) - ih//2

            self.imgSelectBackground.paste(img, (px,py), img)
            self.imgSelect.src = colors.image2Base64(self.imgSelectBackground)
            
               
    # Manage the click event on the output widget
    def handle_event_select(self, event):

        # Insert the position of a throw
        if self.onclick is not None:
            px = event['relativeX']
            py = event['relativeY']
            widthpixel  = event['boundingRectWidth']  - self.added_pixels_width
            heightpixel = event['boundingRectHeight'] - self.added_pixels_height

            ffoutput = widthpixel / heightpixel
            ffimage  = IMAGE_WIDTH_PIXELS / IMAGE_HEIGHT_PIXELS
            
            bandx = 0
            bandy = 0
            if ffoutput > ffimage:                                 # two black bands on left and right sides
                image_height = heightpixel
                image_width  = heightpixel*ffimage
                bandx = (widthpixel  - image_width)//2
            else:                                                  # two black bands on top and bottom sides
                image_height = widthpixel/ffimage
                image_width  = widthpixel
                bandy = (heightpixel - image_height)//2
            
            #with self.debug:
                #print('px',px,'py',py)
                #print('ffoutput',ffoutput)
                #print('ffimage ',ffimage)
                #print('bandx', bandx, 'bandy', bandy)

            px -= bandx
            py -= bandy

            x = 100.0 * px / image_width
            if x > 100: x = 100

            y = 100.0 * py / image_height
            if y > 100: y = 100

            min_dist_for_3 = 41.0
            if self.field_left:
                cx = 22.55
                cy = 50.15
            else:
                cx = 77.25
                cy = 50.15

            dist = math.hypot(x - cx, y - cy)

            doclose = True
            if self.mode_select == 3:
                if False: #dist < min_dist_for_3:
                    doclose = False
            elif self.mode_select == 2:
                if False: #dist > min_dist_for_3:
                    doclose = False

            if doclose:
                self.addThrowSelect(x,y, self.scored)

                self.imgSelect = None
                if self.dlg is not None:
                    self.dlg.close()

                if not self.field_left:
                    x = 100.0 - x
                self.onclick(x,y, self.argument)
            
            
    # Manage the click event on the output widget
    def handle_event_background(self, event):
        
        # Switch field orientation
        self.field_left = not self.field_left
        

    ###########################################################################################################################################################################
    # Properties
    ###########################################################################################################################################################################
        
    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, s: float):
        self._width  /= self._scale
        self._height /= self._scale

        self._scale = s
        
        self._width  *= self._scale
        self._height *= self._scale
        
        self.createControls()
        
        
    # Field orientation
    @property
    def field_left(self):
        return self._field_left

    @field_left.setter
    def field_left(self, f: bool):
        self._field_left = f
        self.reset()
        
        # Display the current throws
        if self.current_df is not None:
            self.displayThrows(self.current_df, background=True)
            self.img.src = colors.image2Base64(self.imgBackground)
