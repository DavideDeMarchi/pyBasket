"""Display time, points and fouls as digital numbers"""
from ipywidgets import widgets, HTML, Layout
from multiprocessing import Process
import time
import ipyvuetify as v
from ipyevents import Event
from vois import colors


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


# Returns a string containing the SVG path from a tick
def tick2Path(index, sizex, sizey, dx=0, dy=2, on=True, prefix='time'):
    tick = TICKS[index]
    path = "M%f %f"%(dx+tick[0][0]*sizex, dy+tick[0][1]*sizey)
    for p in tick:
        path += "L%f %f"%(dx+p[0]*sizex,dy+p[1]*sizey)
    path += " Z"

    if on: c = "%s_tick_on"%prefix
    else:  c = "%s_tick_off"%prefix
    
    return '<path class="%s" d="%s"/>'%(c,path)


# SVG of a figure
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



pppout = widgets.Output()

def ppp(tb):
    while True:
        with pppout:
            print('ppp')
            tb.seconds = tb.seconds + 1
            time.sleep(1.0)


###########################################################################################################################################################################
# Time board: display time in minutes:seconds using SVG
###########################################################################################################################################################################
class TimeBoard():
    
    def __init__(self,
                 width=32.0,              # Dimension in percentage of the screen width
                 scale=1.0,               # Overall scaling
                 color_back='#000000',    # Background color
                 color_on='#00CC00',      # Color for digits on
                 color_off='#1A1A1A',     # Color for digits off
                 color_decs='#006000',    # Color for decimal digits on
                 onclick=None):           # Click on the digits to start and stop the time
    
        self._width  = width
        self._height = width * 0.5
        self._width  *= scale
        self._height *= scale
        
        self.color_back = color_back
        self.color_on   = color_on
        self.color_off  = color_off
        self.color_decs = color_decs
        
        self.onclick = onclick
        
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
        
        # Pixels to add to the output Widget in order to not see the scrollbars
        self.added_pixels_width  = 14
        self.added_pixels_height = 14

        # Create the vuetify Card where the svg is displayed
        self.card = v.Card(flat=True, color=self.color_back, tile=True, width='%fvw'%self._width, height='%fvh'%self._height, ripple=False, nuxt=False, style_='overflow: hidden; color: rgba(0,0,0,0) !important;')

        # Output widget to capture the click event
        self.output = widgets.Output(layout=Layout(width= 'calc(%fvw + %dpx)' % (self._width,self.added_pixels_width), 
                                     height='calc(%fvh + %dpx)' % (self._height,self.added_pixels_height),
                                     margin='0px 0px 0px 0px')) #, border='1px solid red'))

        self.updateChart()
        self.card.children = [self.output]

        # Create the Event manager
        dh = Event(source=self.output, watched_events=['click'])
        dh.on_dom_event(self.handle_event)
        
        
    # Destructor
    def __del__(self):
        pass
        
        #self.timer_stop = True
        #time.sleep(0.2)
        
        #self.timer.join()
        #with self.debug:
        #    print('Timer stopped')
        
    
    # Timer multithread function
    def timerfunc(self):

        self.ms = time.time_ns() // 1_000_000
        with self.debug:
            print('Timer started:', self.ms)

        return 0
    
        while True:
            time.sleep(0.1)
            
            seconds_elapsed = ((time.time_ns() // 1_000_000) - self.ms) / 1000
            self.seconds = self.seconds - seconds_elapsed

            with self.debug:
                print('seconds:', self.seconds)
            
            if self.timer_stop:
                break
                
                
    # Manage the click event on the output widget
    def handle_event(self, event):
        
        px = event['relativeX']
        widthpixel  = event['boundingRectWidth']  - self.added_pixels_width
        
        # Click on the last digit to the right: open settings dialog
        if px >= widthpixel*6/7.0:
            pass
        # Click on one of the 6 left digits: start and stop the time
        else:
            if self.timer_stop:
                with self.debug:
                    print('starting')
                self.timer_stop = False
                #self.timer = Process(target=ppp, args=(self,)) #self.timerfunc)
                self.timer = Process(target=self.timerfunc)
                self.timer.start()
            else:
                with self.debug:
                    print('stopping')
                    self.timer_stop = True
                    self.timer.terminate()
                    self.timer.kill()
                    self.timer = None
            
        if self.onclick is not None:
            self.onclick()
            
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
height="%fvh">''' % (self.svgwidth,self.svgheight, preserve, self._width,self._height)

        svg += '''
    <style type="text/css">
         .time_back     { fill: %s; stroke-width: 0; }
         .time_tick_on  { fill: %s; stroke-width: 0; }
         .time_tick_off { fill: %s; stroke-width: 0; }
         .decs_tick_on  { fill: %s; stroke-width: 0; }
         .decs_tick_off { fill: %s; stroke-width: 0; }
    </style>
    '''%(self.color_back, self.color_on, self.color_off, self.color_decs, self.color_off)
            
        # Background
        svg += '<rect class="time_back" x="0" y="0" width="%f" height="%f"></rect>' % (self.svgwidth,self.svgheight)
    
        # Figures
        svg += figure(self._minutes // 10, sizex=self.sizex, sizey=self.sizey, dx=self.dx, position=0, prefix='time')
        svg += figure(self._minutes %  10, sizex=self.sizex, sizey=self.sizey, dx=self.dx, position=1, prefix='time')
        svg += figure(11,                  sizex=self.sizex, sizey=self.sizey, dx=self.dx, position=2, prefix='time')
        svg += figure(self._seconds // 10, sizex=self.sizex, sizey=self.sizey, dx=self.dx, position=3, prefix='time')
        svg += figure(self._seconds %  10, sizex=self.sizex, sizey=self.sizey, dx=self.dx, position=4, prefix='time')
        svg += figure(11,                  sizex=self.sizex, sizey=self.sizey, dx=self.dx, position=5, prefix='decs')
        svg += figure(self._decs,          sizex=self.sizex, sizey=self.sizey, dx=self.dx, position=6, prefix='decs')
    
        svg += '</svg>'
        
        return svg
    
    
    
    @property
    def width(self):
        return self._width
    
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
        self._minutes = int(s // 60)
        self._seconds = int(s  % 60)
        self._decs    = round((s-int(s)) * 10) % 10
        self.updateChart()
    
    
    
###########################################################################################################################################################################
# Points board: display points (or fouls) for a team in SVG
# Manages click events on the three figures (3 points, 2 points, free throw)
###########################################################################################################################################################################
class PointsBoard():
    
    def __init__(self,
                 width=14.0,            # Dimension in percentage of the screen width
                 scale=1.0,             # Overall scaling
                 color_back='#000000',  # Background color
                 color_on='#FF0000',    # Color for digits on
                 color_off='#1A1A1A',   # Color for digits off
                 fill_zero=True,        # If True shows 000
                 left_align=False,      # Alignment of digits
                 onclick=None):         # Called when click on one figure

        self._width  = width
        self._height = width * 16 / 14.0
        self._width  *= scale
        self._height *= scale
        
        self.color_back = color_back
        self.color_on   = color_on
        self.color_off  = color_off
        self.fill_zero  = fill_zero
        self.left_align = left_align
        
        self.onclick = onclick
        
        # Create a darker color for the initial 0 figures
        rgb = colors.hex2rgb(self.color_on)
        dark = colors.monochromaticColor(rgb, -0.8)
        self.color_zero = colors.rgb2hex(dark)
        
        self.svgwidth  = 70.0
        self.svgheight = 44.0
        
        self.dx = 24.7
        
        self.sizex = 0.23
        self.sizey = 0.28
        
        self._points = 0
        
        # Pixels to add to the output Widget in order to not see the scrollbars
        self.added_pixels_width  = 14
        self.added_pixels_height = 14

        # Create the vuetify Card where the svg is displayed
        self.card = v.Card(flat=True, color=self.color_back, tile=True, width='%fvw'%self._width, height='%fvh'%self._height, ripple=False, nuxt=False, style_='overflow: hidden; color: rgba(0,0,0,0) !important;')

        # Output widget to capture the click event
        self.output = widgets.Output(layout=Layout(width= 'calc(%fvw + %dpx)' % (self._width,self.added_pixels_width), 
                                     height='calc(%fvh + %dpx)' % (self._height,self.added_pixels_height),
                                     margin='0px 0px 0px 0px')) #, border='1px solid red'))

        self.updateChart()
        self.card.children = [self.output]

        # Create the Event manager
        dh = Event(source=self.output, watched_events=['click'])
        dh.on_dom_event(self.handle_event)

        
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
height="%fvh">''' % (self.svgwidth,self.svgheight, preserve, self._width,self._height)

        svg += '''
    <style type="text/css">
         .points_back     { fill: %s; stroke-width: 0; }
         .points_tick_on  { fill: %s; stroke-width: 0; }
         .points_tick_off { fill: %s; stroke-width: 0; }
         .zero_tick_on    { fill: %s; stroke-width: 0; }
         .zero_tick_off   { fill: %s; stroke-width: 0; }
    </style>
    '''%(self.color_back, self.color_on, self.color_off, self.color_zero, self.color_off)
            
        # Background
        svg += '<rect class="points_back" x="0" y="0" width="%f" height="%f"></rect>' % (self.svgwidth,self.svgheight)
    
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

        px = event['relativeX']
        py = event['relativeY']
        widthpixel  = event['boundingRectWidth']  - self.added_pixels_width
        heightpixel = event['boundingRectHeight'] - self.added_pixels_height

        sx = self.svgwidth * px / widthpixel

        if self.onclick is not None:
            if sx <= self.dx:
                self.onclick(3)
            elif sx > self.dx and sx <= self.dx*2:
                self.onclick(2)
            else:
                self.onclick(1)
    
        
    
    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, p: int):
        self._points = p
        if self._points < 0:
            self._points = 0
        self.updateChart()
        
        

        
###########################################################################################################################################################################
# Colon char to be displayed between the points of the two teams
###########################################################################################################################################################################
class Colon():
    
    def __init__(self,
                 width=5.0,             # Dimension in percentage of the screen width
                 scale=1.0,             # Overall scaling
                 color_back='#000000',  # Background color
                 color_on='#FF0000',    # Color for digits on
                 color_off='#1A1A1A'):  # Color for digits off

        self._width  = width
        self._height = width * 16 / 5.0
        self._width  *= scale
        self._height *= scale
        
        self.color_back = color_back
        self.color_on   = color_on
        self.color_off  = color_off
        
        self.svgwidth  = 20.0
        self.svgheight = 44.0
        
        self.dx = 24.7
        
        self.sizex = 0.23
        self.sizey = 0.28
        
        # Pixels to add to the output Widget in order to not see the scrollbars
        self.added_pixels_width  = 14
        self.added_pixels_height = 14

        # Create the vuetify Card where the svg is displayed
        self.card = v.Card(flat=True, color=self.color_back, tile=True, width='%fvw'%self._width, height='%fvh'%self._height, ripple=False, nuxt=False, style_='overflow: hidden; color: rgba(0,0,0,0) !important;')

        # Output widget to capture the click event
        self.output = widgets.Output(layout=Layout(width= 'calc(%fvw + %dpx)' % (self._width,self.added_pixels_width), 
                                     height='calc(%fvh + %dpx)' % (self._height,self.added_pixels_height),
                                     margin='0px 0px 0px 0px')) #, border='1px solid red'))

        self.updateChart()
        self.card.children = [self.output]


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
height="%fvh">''' % (self.svgwidth,self.svgheight, preserve, self._width,self._height)

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
# Fouls board for a team: display fouls for a team in SVG
###########################################################################################################################################################################
class FoulsBoard():
    
    def __init__(self,
                 width=10.0,              # Dimension in percentage of the screen width
                 scale=1.0,               # Overall scaling
                 color_back='#000000',    # Background color
                 color_on='#00CC00',      # Color for digits on
                 color_off='#1A1A1A',     # Color for digits off
                 color_bonus='#CC0000'):  # Color for digits when team is in bonus

        self._width  = width
        self._height = width * 16 / 10.0
        self._width  *= scale
        self._height *= scale
        
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
        
        # Pixels to add to the output Widget in order to not see the scrollbars
        self.added_pixels_width  = 14
        self.added_pixels_height = 14

        # Create the vuetify Card where the svg is displayed
        self.card = v.Card(flat=True, color=self.color_back, tile=True, width='%fvw'%self._width, height='%fvh'%self._height, ripple=False, nuxt=False, style_='overflow: hidden; color: rgba(0,0,0,0) !important;')

        # Output widget to capture the click event
        self.output = widgets.Output(layout=Layout(width= 'calc(%fvw + %dpx)' % (self._width,self.added_pixels_width), 
                                     height='calc(%fvh + %dpx)' % (self._height,self.added_pixels_height),
                                     margin='0px 0px 0px 0px')) #, border='1px solid red'))

        self.updateChart()
        self.card.children = [self.output]


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
height="%fvh">''' % (self.svgwidth,self.svgheight, preserve, self._width,self._height)

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
                
            
###########################################################################################################################################################################
# Overall Board
###########################################################################################################################################################################
class OverallBoard():
    
    def __init__(self, scale=1.0):   # Overall scaling

        self.team1_name = 'Pallacanestro Urbania'
        self.team1_abbr = 'URB'
        self.team2_name = 'Baskers Forlimpopoli'
        self.team2_abbr = 'FOR'
        
        self.scale = scale
        
        self.tb  = TimeBoard(scale=scale*1.0313, onclick=self.startstop)  # To make it the same width of the Score1 + Colon + Score2
        
        twidth  = self.tb.width*0.55
        theight = self.tb.height
        text_height = theight*0.98
        
        space_height = theight*0.3
                
        self.font_name = 'Roboto Condensed'
        self.spacer1 = v.Html(tag='div',children=[' '], style_='width: %fvw; height: %fvh; background-color: %s;'%(self.tb.width, space_height, self.tb.color_back))
        self.spacer2 = v.Html(tag='div',children=[' '], style_='width: %fvw; height: %fvh; background-color: %s;'%(twidth, space_height, self.tb.color_back))
        self.spacer1b = v.Html(tag='div',children=[' '], style_='width: %fvw; height: %fvh; background-color: %s;'%(self.tb.width, space_height*0.5, self.tb.color_back))
        self.spacer2b = v.Html(tag='div',children=[' '], style_='width: %fvw; height: %fvh; background-color: %s;'%(twidth, space_height*0.5, self.tb.color_back))
        
        self.pb1 = PointsBoard(scale=scale, left_align=False)
        self.colon = Colon(scale=scale)
        self.pb2 = PointsBoard(scale=scale, left_align=True)
        
        self.fb1 = FoulsBoard(scale=scale)
        self.fb2 = FoulsBoard(scale=scale)
        
        fwidth1 = (twidth - self.fb1.width)*0.1
        fwidth2 = (twidth - self.fb1.width)*0.9
        fheight = self.fb1.height
        self.spacer3 = v.Html(tag='div',children=[' '], style_='width: %fvw; height: %fvh; background-color: %s;'%(fwidth1, fheight, self.tb.color_back))
        self.spacer4 = v.Html(tag='div',children=[' '], style_='width: %fvw; height: %fvh; background-color: %s;'%(fwidth2, fheight, self.tb.color_back))
        
        style_text = 'color: white; background-color: %s; font-size: %fvh; line-height: %fvh; font-family: "%s", serif; vertical-align: baseline;'%(self.tb.color_back, text_height, theight, self.font_name)
        self.team1  = v.Html(tag='div',children=[self.team1_abbr], style_='width: %fvw; height: %fvh; %s; overflow: hidden; text-align: left;  padding-left:  %fvw;'%(twidth, theight, style_text, fwidth1*1.2))
        self.team2  = v.Html(tag='div',children=[self.team2_abbr], style_='width: %fvw; height: %fvh; %s; overflow: hidden; text-align: right; padding-right: %fvw;'%(twidth, theight, style_text, fwidth1*1.2))

        
    # Start and stop of the time
    def startstop(self):
        pass
        
        
    # Draw the board
    def draw(self):
        return widgets.HBox([
                    HTML('''
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Roboto+Condensed:ital,wght@0,100..900;1,100..900&display=swap" rel="stylesheet">
'''),
                    widgets.VBox([self.team1,
                                  self.spacer2,
                                  widgets.HBox([self.spacer3, self.fb1.card, self.spacer4]),
                                  self.spacer2b]),
            
                    widgets.VBox([self.tb.card,
                                  self.spacer1,
                                  widgets.HBox([self.pb1.card, self.colon.card, self.pb2.card]),
                                  self.spacer1b]),
            
                    widgets.VBox([self.team2,
                                  self.spacer2,
                                  widgets.HBox([self.spacer4, self.fb2.card, self.spacer3]),
                                  self.spacer2b]),
        ])

        

