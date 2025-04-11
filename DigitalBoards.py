"""Time, Points, Fouls boards implemented using digital numbers"""
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
import threading
import time
import ipyvuetify as v
from PIL import Image
from ipyevents import Event

# vois imports
from vois import colors
from vois.vuetify import settings, iconButton


###########################################################################################################################################################################
# Digital display
###########################################################################################################################################################################
TICKS = [
           [ [  2,  0], [ 98,  0], [ 73, 25], [ 27, 25]                                             ],  # 0
           [ [  0,  2], [ 25, 27], [ 25, 57], [ 14, 67], [  0, 67]                                  ],  # 1
           [ [100,  2], [100, 67], [ 86, 67], [ 75, 57] ,[ 75, 27]                                  ],  # 2
           [ [ 17, 69], [ 27, 59], [ 73, 59], [ 84, 69], [ 84, 73], [ 73, 83], [ 27, 83], [ 17, 73] ],  # 3
           [ [  0, 75], [ 14, 75], [ 25, 87], [ 25,114], [  0,139]                                  ],  # 4
           [ [100, 75], [100,139], [ 75,114], [ 75, 87], [ 86, 75]                                  ],  # 5
           [ [ 27,116], [ 73,116], [ 98,141], [  2,141]                                             ],  # 6
           [ [ 37, 30], [ 62, 30], [ 62, 54], [ 37, 54]                                             ],  # 7
           [ [ 37, 88], [ 62, 88], [ 62,113], [ 37,113]                                             ]   # 8
]


FIGURES = [ # 0  1  2  3  4  5  6  7  8
            [ 1, 1, 1, 0, 1, 1, 1, 0, 0 ],    # 0
            [ 0, 0, 1, 0, 0, 1, 0, 0, 0 ],    # 1
            [ 1, 0, 1, 1, 1, 0, 1, 0, 0 ],    # 2
            [ 1, 0, 1, 1, 0, 1, 1, 0, 0 ],    # 3
            [ 0, 1, 1, 1, 0, 1, 0, 0, 0 ],    # 4
            [ 1, 1, 0, 1, 0, 1, 1, 0, 0 ],    # 5
            [ 1, 1, 0, 1, 1, 1, 1, 0, 0 ],    # 6
            [ 1, 0, 1, 0, 0, 1, 0, 0, 0 ],    # 7
            [ 1, 1, 1, 1, 1, 1, 1, 0, 0 ],    # 8
            [ 1, 1, 1, 1, 0, 1, 1, 0, 0 ],    # 9
            [ 0, 0, 0, 0, 0, 0, 0, 0, 0 ],    # blank
            [ 0, 0, 0, 0, 0, 0, 0, 1, 1 ],    # :
]


# Utility: returns a string containing the SVG path from a tick
def tick2Path(index, sizex, sizey, dx=0, dy=2, on=True, prefix='time'):
    tick = TICKS[index]
    path = "M%f %f"%(dx+tick[0][0]*sizex, dy+tick[0][1]*sizey)
    for p in tick:
        path += "L%f %f"%(dx+p[0]*sizex,dy+p[1]*sizey)
    path += " Z"

    if on: c = "%s_tick_on"%prefix
    else:  c = "%s_tick_off"%prefix
    
    return '<path class="%s" pointer-events="none" d="%s"/>'%(c,path)


# Utility: SVG of a figure
def figure(f, sizex, sizey, dx, position=0, prefix='time'):
    d = dx * position - 1
    
    if f >= 0 and f < len(FIGURES):
        fig = FIGURES[f]
    else:
        fig = [0]*9

    svg = ''
    for i in range(len(TICKS)):
        svg += tick2Path(i, sizex, sizey, dx=d, on=fig[i], prefix=prefix)
        
    return svg




###########################################################################################################################################################################
# Time board: display time in minutes:seconds using SVG
###########################################################################################################################################################################
class TimeBoard(widgets.HBox):
    
    def __init__(self,
                 width=32.0,              # Dimension in percentage of the screen width
                 scale=1.0,               # Overall scaling
                 color_back='#000000',    # Background color
                 color_on='#00DD00',      # Color for digits on
                 color_off='#1A1A1A',     # Color for digits off
                 color_decs='#009900',    # Color for decimal digits on
                 onstarted=None,          # Called when the timer is restarted (beginning of each quarter)
                 onupdate=None,           # Update time on the field for each player
                 onstopped=None,          # Called when the timer is paused
                 onterminated=None):      # Called when the current quarter is terminated by clicking in the "stop" iconButton
    
        super().__init__()
    
        self._scale = scale
        self._width  = width
        self._height = width * 0.24
        self._width  *= self._scale
        self._height *= self._scale
        
        self.color_back = color_back
        self.color_on   = color_on
        self.color_off  = color_off
        self.color_decs = color_decs
        
        rgb = colors.hex2rgb(self.color_decs)
        dark = colors.monochromaticColor(rgb, -0.2)
        self.color_doff = colors.rgb2hex(dark)
        
        self.onstarted    = onstarted
        self.onupdate     = onupdate
        self.onstopped    = onstopped
        self.onterminated = onterminated
        
        self.svgwidth  = 170.0
        self.svgheight =  44.0
        
        self.dx = 24.7
        
        self.sizex = 0.23
        self.sizey = 0.28
        
        self._minutes = 0
        self._seconds = 0
        self._decs    = 0
        
        self.debug = widgets.Output()
        
        # Timer thread members
        self.timer = None
        self.timer_stop = True
        
        # True when a quarter is going to start
        self.restarted = True
        
        # True when the game is over
        self._gameover = False
        
        self.createControls()

        
    # Creation of the controls
    def createControls(self):
        
        # Create the vuetify Card where the svg is displayed
        self.card = v.Card(flat=True, color=self.color_back, tile=True, width='%fvw'%self._width, height='calc(%fvw + 3px)'%self._height, ripple=False, nuxt=False, 
                           class_='noselect', style_='overflow: hidden; color: rgba(0,0,0,0) !important;')

        # Create the controls card
        cwidth = self._width*0.12
        self.controls = v.Card(flat=True, color=self.color_back, tile=True, width='%fvw'%cwidth, height='calc(%fvw + 3px)'%self._height, ripple=False, nuxt=False, 
                               class_='noselect', style_='overflow: hidden; color: rgba(0,0,0,0) !important;')
        
        self.isTerminated = False
        
        h = 40
        x_large = True
        if self.scale < 0.4:
            x_large = False
            h = 20
            
        self.playpause = iconButton.iconButton(onclick=self.onplaypause, icon='mdi-play', width='calc(%fvw - 6px)'%cwidth, x_large=x_large, tooltip='Start/Stop the timer',          color=settings.color_first)
        self.playpause.btn.height = h
        self.terminate = iconButton.iconButton(onclick=self.onterminate, icon='mdi-stop', width='calc(%fvw - 6px)'%cwidth, x_large=x_large, tooltip='Terminate the current quarter', color=settings.color_first, disabled=True)
        self.terminate.btn.height = h
        
        self.controls.children = [self.playpause.draw(), self.terminate.draw()]

        self.updateChart()
        
        self.children = [self.card, self.controls]
        
        
    ###########################################################################################################################################################################
    # Manage iconButtons for play, pause and terminate
    ###########################################################################################################################################################################
    
    # Start and stop button
    def onplaypause(self):
        if not self._gameover:
            if self.timer_stop:
                
                if self.restarted:
                    self.restarted = False
                    if self.onstarted is not None:
                        self.onstarted()
                    
                if self.start():
                    self.playpause.icon = 'mdi-pause'
            else:
                self.stop()
                self.playpause.icon = 'mdi-play'

            
    # Terminate button
    def onterminate(self):
        if self.onterminated is not None:
            self.isTerminated = True
            self.terminate.disabled = True
            self.onterminated()
            self.playpause.icon = 'mdi-play'
        
        
    ###########################################################################################################################################################################
    # Start, Stop, threading function for time management
    ###########################################################################################################################################################################
        
    # Start the timer
    def start(self):
        if not self.timer_stop:
            self.stop()
            
        if self.seconds <= 0:
            self.onterminate()
            return False
        else:
            self.timer_stop = False
            self.timer = threading.Thread(target=self.timerfunc)
            self.timer.start()
            return True
        
        
    # Stop the timer
    def stop(self):
        self.timer_stop = True
        time.sleep(0.3333333)
        self.timer = None
        if self.onstopped:
            self.onstopped()
        

    # Timer multithread function
    def timerfunc(self):
 
        self.start_time = time.time()
        self.start_seconds = self.seconds
    
        while True:
            if self.timer_stop:
                break
                
            #time.sleep(0.33333333333)
            #time.sleep(0.4)

            time.sleep(0.1111111)
            if self.timer_stop:
                break
            
            time.sleep(0.1111111)
            if self.timer_stop:
                break

            time.sleep(0.1111111)
            if self.timer_stop:
                break
                
            new_time = time.time()
            
            seconds_elapsed = new_time - self.start_time
            self.seconds = self.start_seconds - seconds_elapsed
            
            if self.onupdate is not None:
                self.onupdate(seconds_elapsed)
            
            # Stop timer when reaches 0 seconds
            if self.seconds <= 0:
                self.playpause.disabled = True
                self.terminate.disabled = False
                self.timer_stop = True
               
                # Saves the game!
                if self.onstopped:
                    self.onstopped()                

            if self.timer_stop:
                break

        self.updateChart()

        
    ###########################################################################################################################################################################
    # Display 
    ###########################################################################################################################################################################
            
    # Update the chart: display the SVG inside the self.card widget
    def updateChart(self):
        svg = self.createSVG()
        self.card.children = [HTML(svg)]
        
        
    # Create the SVG drawing and returns a string
    def createSVG(self):
        preserve = 'xMidYMid meet'    # Center the chart in the parent
        svg = '''<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xml:space="preserve"
viewBox="0 0 %f %f"
preserveAspectRatio="%s"
width="%fvw"
height="%fvw">''' % (self.svgwidth,self.svgheight, preserve, self._width,self._height)

        svg += '''
    <style type="text/css">
         .time_back     { fill: %s; stroke-width: 0; }
         .time_tick_on  { fill: %s; stroke-width: 0; }
         .time_tick_off { fill: %s; stroke-width: 0; }
         .decs_tick_on  { fill: %s; stroke-width: 0; }
         .decs_tick_off { fill: %s; stroke-width: 0; }
         .doff_tick_on  { fill: %s; stroke-width: 0; }
         .doff_tick_off { fill: %s; stroke-width: 0; }
    </style>
    '''%(self.color_back, self.color_on, self.color_off, self.color_decs, self.color_off, self.color_doff, self.color_off)
            
        # Background
        svg += '<rect class="time_back" x="0" y="0" width="%f" height="%f"></rect>' % (self.svgwidth,self.svgheight)
    
        # Figures
        if self.timer_stop:
            prefix  = 'decs'
            predecs = 'doff'
        else:
            prefix  = 'time'
            predecs = 'decs'
            
        if self._gameover:
            prefix  = 'doff'
            svg += figure(10, sizex=self.sizex, sizey=self.sizey, dx=self.dx, position=0, prefix=prefix)
            svg += figure(10, sizex=self.sizex, sizey=self.sizey, dx=self.dx, position=1, prefix=prefix)
            svg += figure(10, sizex=self.sizex, sizey=self.sizey, dx=self.dx, position=2, prefix=prefix)
            svg += figure(10, sizex=self.sizex, sizey=self.sizey, dx=self.dx, position=3, prefix=prefix)
            svg += figure(10, sizex=self.sizex, sizey=self.sizey, dx=self.dx, position=4, prefix=prefix)
            svg += figure(10, sizex=self.sizex, sizey=self.sizey, dx=self.dx, position=5, prefix=prefix)
            svg += figure(10, sizex=self.sizex, sizey=self.sizey, dx=self.dx, position=6, prefix=prefix)
        else:
            svg += figure(self._minutes // 10, sizex=self.sizex, sizey=self.sizey, dx=self.dx, position=0, prefix=prefix)
            svg += figure(self._minutes %  10, sizex=self.sizex, sizey=self.sizey, dx=self.dx, position=1, prefix=prefix)
            svg += figure(11,                  sizex=self.sizex, sizey=self.sizey, dx=self.dx, position=2, prefix=prefix)
            svg += figure(self._seconds // 10, sizex=self.sizex, sizey=self.sizey, dx=self.dx, position=3, prefix=prefix)
            svg += figure(self._seconds %  10, sizex=self.sizex, sizey=self.sizey, dx=self.dx, position=4, prefix=prefix)
            svg += figure(11,                  sizex=self.sizex, sizey=self.sizey, dx=self.dx, position=5, prefix='decs')
            svg += figure(self._decs,          sizex=self.sizex, sizey=self.sizey, dx=self.dx, position=6, prefix=predecs)
    
        svg += '</svg>'
        
        return svg
    
    
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
        
        
    @property
    def width(self):
        return self._width*1.12
    
    @property
    def height(self):
        return self._height

    @property
    def seconds(self):
        return self._seconds + self._minutes * 60 + self._decs/10

    @seconds.setter
    def seconds(self, s: float):
        if s < 0.0:
            s = 0.0
            
        if self.isTerminated and s > 0.0:
            self.isTerminated = False
            self.playpause.disabled = False
            self.terminate.disabled = True
            
        if s <= 0.0:
            self.playpause.disabled = True
            self.terminate.disabled = False
            
        self._minutes = int(s // 60)
        self._seconds = int(s  % 60)
        self._decs    = round((s-int(s)) * 10) % 10
        self.updateChart()
    
    
    @property
    def gameover(self):
        return self._gameover

    @gameover.setter
    def gameover(self, f: bool):
        self._gameover = f
        if self._gameover:
            self.seconds = 0.0
            self.playpause.disabled = False
            self.terminate.disabled = True
            self.playpause.icon     = 'mdi-close-box'
            self.playpause.color    = 'red'
            self.playpause.tooltip  = 'Game is over'
        else:
            self.playpause.disabled = False
            self.terminate.disabled = True
            self.playpause.icon     = 'mdi-play'
            self.playpause.color    = settings.color_first
            self.playpause.tooltip  = 'Start/Stop the timer'
            
        self.updateChart()
    
    
    
###########################################################################################################################################################################
# Points board: display points (or fouls) for a team in SVG
# Manages click events on the three figures (3 points, 2 points, free throw)
###########################################################################################################################################################################
class PointsBoard(widgets.HBox):
    
    def __init__(self,
                 width=15.0,            # Dimension in percentage of the screen width
                 scale=1.0,             # Overall scaling
                 color_back='#000000',  # Background color
                 color_on='#FF0000',    # Color for digits on
                 color_off='#1A1A1A',   # Color for digits off
                 fill_zero=True,        # If True shows 000
                 left_align=False,      # Alignment of digits
                 onclick=None):         # Called when click on one figure

        super().__init__()
        
        self._scale  = scale
        self._width  = width
        self._height = width * 0.55
        self._width  *= self._scale
        self._height *= self._scale
        
        self.color_back = color_back
        self.color_on   = color_on
        self.color_off  = color_off
        self.fill_zero  = fill_zero
        self.left_align = left_align
        
        self.onclick = onclick
        
        # Create a darker color for the initial 0 figures
        rgb = colors.hex2rgb(self.color_on)
        dark = colors.monochromaticColor(rgb, -0.8)
        #self.color_zero = colors.rgb2hex(dark)
        self.color_zero = self.color_off

        self.svgwidth  = 70.0
        self.svgheight = 44.0
        
        self.dx = 24.7
        self.dy = 20.0

        self.sizex = 0.23
        self.sizey = 0.28
        
        self._points = 0
        
        self._gameover = False
        
        self.createControls()

        
    # Creation of the controls
    def createControls(self):
        
        # Pixels to add to the output Widget in order to not see the scrollbars
        self.added_pixels_width  = 14
        self.added_pixels_height = 14

        # Create the vuetify Card where the svg is displayed
        self.card = v.Card(flat=True, color=self.color_back, tile=True, width='calc(%fvw + 6px)'%self._width, height='calc(%fvw + 6px)'%self._height, ripple=False, nuxt=False,
                           class_='noselect', style_='overflow: hidden; color: rgba(0,0,0,0) !important;')

        # Output widget to capture the click event
        self.output = widgets.Output(layout=Layout(width= 'calc(%fvw + %dpx)' % (self._width,self.added_pixels_width), 
                                     height='calc(%fvw + %dpx)' % (self._height,self.added_pixels_height),
                                     margin='0px 0px 0px 0px')) #, border='1px solid red'))

        self.updateChart()
        self.card.children = [self.output]

        # Create the Event manager
        dh = Event(source=self.output, watched_events=['click'])
        dh.on_dom_event(self.handle_event)

        self.children = [self.card]
        
        
    # Update the chart: display the SVG inside the self.output widget
    def updateChart(self):
        self.output.clear_output(wait=True)
        svg = self.createSVG()
        with self.output:
            display(HTML(svg))
        
        
    # Create the SVG drawing and returns a string
    def createSVG(self):
        preserve = 'xMidYMid meet'    # Center the chart in the parent
        svg = '''<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xml:space="preserve"
viewBox="0 0 %f %f"
preserveAspectRatio="%s"
width="%fvw"
height="%fvw">''' % (self.svgwidth,self.svgheight, preserve, self._width,self._height)

        svg += '''
    <style type="text/css">
         .points_back          { fill: %s; stroke-width: 0; cursor: default; }
         .points_plus_pointer  { fill: %s; stroke-width: 0; cursor: crosshair; }
         .points_minus_pointer { fill: %s; stroke-width: 0; cursor: vertical-text; }
         .points_tick_on       { fill: %s; stroke-width: 0; }
         .points_tick_off      { fill: %s; stroke-width: 0; }
         .zero_tick_on         { fill: %s; stroke-width: 0; }
         .zero_tick_off        { fill: %s; stroke-width: 0; }
    </style>
    '''%(self.color_back, self.color_back, self.color_back, self.color_on, self.color_off, self.color_zero, self.color_off)
            
        # Background
        if self.onclick is None:
            svg += '<rect class="points_back" x="0" y="0" width="%f" height="%f"></rect>'%(self.svgwidth,self.svgheight)
        else:
            svg += '<rect class="points_plus_pointer"  x="0" y="0"  width="%f" height="%f"></rect>'%(self.svgwidth,self.svgheight/2)
            svg += '<rect class="points_minus_pointer" x="0" y="%f" width="%f" height="%f"></rect>'%(self.svgheight/2, self.svgwidth,self.svgheight/2)
    
        # Figures
        if self.left_align:
            if self._points < 10:    order = [2,1,0]
            elif self._points < 100: order = [2,0,1]
            else:                    order = [0,1,2]
        else:
            order = [0,1,2]
            
        if self.fill_zero:
            if self._points < 100: prefix = 'zero'
            else:                  prefix = 'points'
            svg += figure(self._points // 100, sizex=self.sizex, sizey=self.sizey, dx=self.dx, position=order[0], prefix=prefix)
            
            if self._points < 10: prefix = 'zero'
            else:                 prefix = 'points'
            svg += figure((self._points % 100) // 10,  sizex=self.sizex, sizey=self.sizey, dx=self.dx, position=order[1], prefix=prefix)
            
            svg += figure(self._points %  10,  sizex=self.sizex, sizey=self.sizey, dx=self.dx, position=order[2], prefix='points')
        else:
            cents = self._points // 100
            if cents <= 0:
                cents = -1
            svg += figure(cents, sizex=self.sizex, sizey=self.sizey, dx=self.dx, position=order[0], prefix='points')

            decs = (self._points % 100) // 10
            if decs <= 0 and cents <= 0:
                decs = -1
            svg += figure(decs,  sizex=self.sizex, sizey=self.sizey, dx=self.dx, position=order[1], prefix='points')

            svg += figure(self._points %  10,  sizex=self.sizex, sizey=self.sizey, dx=self.dx, position=order[2], prefix='points')
    
        svg += '</svg>'
        
        return svg
    
    
    # Manage the click event on the output widget
    def handle_event(self, event):

        if not self._gameover:
            px = event['relativeX']
            py = event['relativeY']
            widthpixel  = event['boundingRectWidth']  - self.added_pixels_width
            heightpixel = event['boundingRectHeight'] - self.added_pixels_height

            sx = self.svgwidth  * px / widthpixel
            sy = self.svgheight * py / heightpixel

            if self.onclick is not None:
                if sy <= self.dy:
                    if sx <= self.dx:
                        self.onclick(3)
                    elif sx > self.dx and sx <= self.dx*2:
                        self.onclick(2)
                    else:
                        self.onclick(1)
                else:
                    if sx <= self.dx:
                        self.onclick(-3)
                    elif sx > self.dx and sx <= self.dx*2:
                        self.onclick(-2)
                    else:
                        self.onclick(-1)
    
        
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

        
    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, p: int):
        self._points = p
        if self._points < 0:
            self._points = 0
        self.updateChart()
        

    @property
    def gameover(self):
        return self._gameover

    @gameover.setter
    def gameover(self, f: bool):
        self._gameover = f
        

        
###########################################################################################################################################################################
# Colon char to be displayed between the points of the two teams
###########################################################################################################################################################################
class Colon(widgets.HBox):
    
    def __init__(self,
                 width=5.0,             # Dimension in percentage of the screen width
                 scale=1.0,             # Overall scaling
                 color_back='#000000',  # Background color
                 color_on='#FF0000',    # Color for digits on
                 color_off='#1A1A1A'):  # Color for digits off

        super().__init__()
        
        self._scale = scale
        self._width  = width
        self._height = width * 1.65
        self._width  *= self._scale
        self._height *= self._scale
        
        self.color_back = color_back
        self.color_on   = color_on
        self.color_off  = color_off
        
        self.svgwidth  = 20.0
        self.svgheight = 44.0
        
        self.dx = 24.7
        
        self.sizex = 0.23
        self.sizey = 0.28
        
        self.createControls()

        
    # Creation of the controls
    def createControls(self):

        # Pixels to add to the output Widget in order to not see the scrollbars
        self.added_pixels_width  = 14
        self.added_pixels_height = 14

        # Create the vuetify Card where the svg is displayed
        self.card = v.Card(flat=True, color=self.color_back, tile=True, width='calc(%fvw + 6px)'%self._width, height='calc(%fvw + 6px)'%self._height, ripple=False, nuxt=False,
                           class_='noselect', style_='overflow: hidden; color: rgba(0,0,0,0) !important;')

        # Output widget to capture the click event
        self.output = widgets.Output(layout=Layout(width= 'calc(%fvw + %dpx)' % (self._width,self.added_pixels_width), 
                                     height='calc(%fvw + %dpx)' % (self._height,self.added_pixels_height),
                                     margin='0px 0px 0px 0px')) #, border='1px solid red'))

        self.updateChart()
        self.card.children = [self.output]
        
        self.children = [self.card]


    
    # Update the chart: display the SVG inside the self.output widget
    def updateChart(self):
        self.output.clear_output(wait=True)
        svg = self.createSVG()
        with self.output:
            display(HTML(svg))
        
        
    # Create the SVG drawing and returns a string
    def createSVG(self):
        preserve = 'xMidYMid meet'    # Center the chart in the parent
        svg = '''<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xml:space="preserve"
viewBox="0 0 %f %f"
preserveAspectRatio="%s"
width="%fvw"
height="%fvw">''' % (self.svgwidth,self.svgheight, preserve, self._width,self._height)

        svg += '''
    <style type="text/css">
         .colon_back     { fill: %s; stroke-width: 0; }
         .colon_tick_on  { fill: %s; stroke-width: 0; }
         .colon_tick_off { fill: %s; stroke-width: 0; }
    </style>
    '''%(self.color_back, self.color_on, self.color_off)
            
        # Background
        svg += '<rect class="colon_back" x="0" y="0" width="%f" height="%f"></rect>' % (self.svgwidth,self.svgheight)
    
        # Figures
        svg += figure(11, sizex=self.sizex, sizey=self.sizey, dx=self.dx, position=0, prefix='colon')
    
        svg += '</svg>'
        
        return svg

    
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
    
    
        
###########################################################################################################################################################################
# Fouls board for a team: display fouls for a team in SVG
###########################################################################################################################################################################
class FoulsBoard(widgets.HBox):
    
    def __init__(self,
                 width=10.0,              # Dimension in percentage of the screen width
                 scale=1.0,               # Overall scaling
                 color_back='#000000',    # Background color
                 color_on='#00DD00',      # Color for digits on
                 color_off='#1A1A1A',     # Color for digits off
                 color_bonus='#DD0000'):  # Color for digits when team is in bonus

        super().__init__()
        
        self._scale = scale
        self._width  = width
        self._height = width * 0.8
        self._width  *= self._scale
        self._height *= self._scale
        
        self.color_back  = color_back
        self.color_on    = color_on
        self.color_off   = color_off
        self.color_bonus = color_bonus
        
        self.svgwidth  = 45.0
        self.svgheight = 44.0
        
        self.dx = 24.7
        
        self.sizex = 0.23
        self.sizey = 0.28
        
        self._fouls = 0
        
        self.createControls()

        
    # Creation of the controls
    def createControls(self):

        # Pixels to add to the output Widget in order to not see the scrollbars
        self.added_pixels_width  = 14
        self.added_pixels_height = 14

        # Create the vuetify Card where the svg is displayed
        self.card = v.Card(flat=True, color=self.color_back, tile=True, width='calc(%fvw + 6px)'%self._width, height='calc(%fvw + 6px)'%self._height, ripple=False, nuxt=False,
                           class_='noselect', style_='overflow: hidden; color: rgba(0,0,0,0) !important;')

        # Output widget to capture the click event
        self.output = widgets.Output(layout=Layout(width= 'calc(%fvw + %dpx)' % (self._width,self.added_pixels_width), 
                                     height='calc(%fvw + %dpx)' % (self._height,self.added_pixels_height),
                                     margin='0px 0px 0px 0px')) #, border='1px solid red'))

        self.updateChart()
        self.card.children = [self.output]
        
        self.children = [self.card]

        
    # Update the chart: display the SVG inside the self.output widget
    def updateChart(self):
        self.output.clear_output(wait=True)
        svg = self.createSVG()
        with self.output:
            display(HTML(svg))
        
        
    # Create the SVG drawing and returns a string
    def createSVG(self):
        preserve = 'xMidYMid meet'    # Center the chart in the parent
        svg = '''<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xml:space="preserve"
viewBox="0 0 %f %f"
preserveAspectRatio="%s"
width="%fvw"
height="%fvw">''' % (self.svgwidth,self.svgheight, preserve, self._width,self._height)

        svg += '''
    <style type="text/css">
         .fouls_back     { fill: %s; stroke-width: 0; }
         .fouls_tick_on  { fill: %s; stroke-width: 0; }
         .fouls_tick_off { fill: %s; stroke-width: 0; }
         .bonus_tick_on  { fill: %s; stroke-width: 0; }
    </style>
    '''%(self.color_back, self.color_on, self.color_off, self.color_bonus)
            
        # Background
        svg += '<rect class="fouls_back" x="0" y="0" width="%f" height="%f"></rect>' % (self.svgwidth,self.svgheight)
    
        # Figures
        if self._fouls >= 4: prefix = 'bonus'
        else:                prefix = 'fouls'
        svg += figure((self._fouls % 100) // 10, sizex=self.sizex, sizey=self.sizey, dx=self.dx, position=0, prefix=prefix)
        svg += figure(self._fouls %  10,         sizex=self.sizex, sizey=self.sizey, dx=self.dx, position=1, prefix=prefix)
    
        svg += '</svg>'
        
        return svg

    
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
        
        
    @property
    def width(self):
        return self._width
    
    @property
    def height(self):
        return self._height
    

    @property
    def fouls(self):
        return self._fouls

    @fouls.setter
    def fouls(self, f: int):
        self._fouls = f
        if self._fouls < 0:
            self._fouls = 0
        self.updateChart()
        