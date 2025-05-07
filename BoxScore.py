"""Creation of the Box Score of a game starting from the events DataFrame"""
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
import pandas as pd
import numpy as np
import datetime
from PIL import Image
import plotly.graph_objects as go

# vois imports
from vois import colors

# local imports
import Config
import Stats
import Game


###########################################################################################################################################################################
# Constants
###########################################################################################################################################################################

# Font name and URL
font_name = 'Roboto'
font_url  = 'https://fonts.googleapis.com/css?family=%s:400,100,100italic,300,300italic,400italic,500,500italic,700,700italic,900,900italic' % (font_name)

#font_name = 'Open Sans'
#font_url  = 'https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,300..800;1,300..800&family=Roboto+Condensed:ital,wght@0,100..900;1,100..900&display=swap'


# Dimension of the BoxScore.png background image
IMAGE_WIDTH_IN_PIXELS  = 2200
IMAGE_HEIGHT_IN_PIXELS = 1130

# Dimension of height compared to width of the BoxScore
FORM_FACTOR = IMAGE_HEIGHT_IN_PIXELS/IMAGE_WIDTH_IN_PIXELS

# Positioning
YSQUADRA1  =  1.00
YSQUADRA2  =  1.52
YQUARTI    =  1.56
YLUOGO     =  0.15
YRIGA0     =  3.18

XSQUADRE   =  3.00
XPUNTEGGIO = 11.20

XPARZIALI  = 12.50
XPARZIALID =  1.10

XLEFT      =  0.32
XRIGHT     = 21.68

XSQUADRA   =  1.75
XNUMERO    =  0.40
XNOME      =  0.90
XSTARTERS  =  3.00

XMINUTI    =  3.80
XPUNTI     =  4.65
X2P        =  5.87
X2P_PERC   =  6.50
X3P        =  7.76
X3P_PERC   =  8.32
XTOTTIRI   =  9.52
XTOT_PERC  = 10.10
X1P        = 11.41
X1P_PERC   = 12.06
XASSIST    = 12.66
XRIMBALZI  = 13.74
XRDIF      = 13.25
XROFF      = 13.74
XRTOT      = 14.26
XFALLI     = 15.11
XFATTI     = 14.87
XSUBITI    = 15.35
XPALLE     = 16.27
XPREC      = 15.96
XPPER      = 16.44
XSTOPPATE  = 17.31
XSTOFA     = 17.08
XSTOSU     = 17.53
XVAL       = 18.12
XOER       = 18.87
XVIR       = 19.80
XPLUSMIN   = 20.59
XTRUE      = 21.28



###########################################################################################################################################################################
# Returns the BoxScore in svg format
###########################################################################################################################################################################
def svg(df, game, team_logo_img=None, width=80, quarter=None, downloadMode=False):   # Dimensioning in vw/vh
    
    # Read seconds on field from the game if the overall sheet has to be produced
    if quarter is None:
        seconds_on_field = {x: game.players_info[x]['time_on_field'] for x in game.players_info.keys()}
        
    # Filter events of a single quarter
    else:
        df = df[df['quarter']==quarter].copy()
    
        # Calculates time on field for all the players
        df2 = df[(df['team']==Config.TEAM)&(df['event'].isin([18,19]))]
        seconds_on_field = {x: 0.0 for x in df2['player']}
        on_field = {}
        for index, row in df2.iterrows():
            event   = row['event']
            quarter = row['quarter']
            seconds = row['seconds']
            player  = row['player']

            if event == 18:
                on_field[player] = seconds

            if event == 19:
                if player in on_field.keys():
                    s = on_field[player] - seconds
                    del on_field[player]
                    seconds_on_field[player] += s

        for player in on_field.keys():
            s = on_field[player]
            seconds_on_field[player] += s
            
            
    
    height = 2.005*FORM_FACTOR*width    # 2 means that 1vw = 2vh in general screens
    
    svgwidth  = IMAGE_WIDTH_IN_PIXELS  / 100.0    # 21.30
    svgheight = IMAGE_HEIGHT_IN_PIXELS / 100.0    # 10.90
    
    
    # In doanloda mode, do not use vw/vh units!!!
    if downloadMode:
        xunits = ''
        yunits = ''
    else:
        xunits = 'vw'
        yunits = 'vh'
    
    preserve = 'xMidYMin meet'    # Center the chart in the parent
    svg = '''<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xml:space="preserve"
viewBox="0 0 %f %f"
preserveAspectRatio="%s"
width="%f%s"
height="%f%s">''' % (svgwidth,svgheight, preserve, width, xunits, height, yunits)

    svg += '''
    <style type="text/css">
       @import url('%s');
    </style>
    ''' % font_url
    
    # Fill modes
    white   = 'fill="white"'
    black   = 'fill="black"'
    darkred = 'fill="#9c0000"'
    red     = 'fill="#c00000"'
    grey    = 'fill="#dcdcdc"'

    # Stroke modes
    none   = 'stroke-width="0"'
    xsmall = 'stroke="black" stroke-width="0.001"'
    small  = 'stroke="black" stroke-width="0.012"'
    medium = 'stroke="black" stroke-width="0.038"'
    
    
    # Background
    svg += '<rect x="0" y="0" width="%f" height="%f" %s %s></rect>' % (svgwidth,svgheight, white, none)
    
    #svg += '<text x="10.0" y="5.0" fill="black" stroke="none" font-size="2.0" font-weight="400" font-family="Roboto">prova</text>'
    #svg += '</svg>'
    #return svg


    # Background image
    backimg = Image.open('./resources/BoxScore.png')
    backimgbase64 = colors.image2Base64(backimg)
    svg += '<image x="0.0" y="0.0" width="%f" height="%f" href="%s" preserveAspectRatio="xMidYMid meet"></image>'%(svgwidth, svgheight, backimgbase64)
    
    #svg += '<rect x="5.0" y="4.0" width="12.0" height="2.0" %s %s></rect>' % (red, small)
    #svg += '<rect x="5.0" y="1.0" width="12.0" height="2.0" %s %s></rect>' % (darkred, medium)
    
    # Team logo
    imgbase64 = None
    if game is not None:
        imgbase64 = colors.image2Base64(game.team_logo_img)
    else:
        if team_logo_img is not None :
            imgbase64 = colors.image2Base64(team_logo_img)
            
    if imgbase64 is not None:
        svg += '<image x="0.55" y="-0.1" width="1.9" height="2.5" href="%s" preserveAspectRatio="xMidYMid meet"></image>'%imgbase64

        
    # DrawText internal function
    def text(x, y, s, dim=0.28, w=500, align='start', color='black'):
        if downloadMode: outputdim = dim*0.9
        else:            outputdim = dim*0.99
        return '<text x="%f" y="%f" fill="%s" stroke="none" font-size="%f" font-weight="%d" font-family="%s" text-anchor="%s" alignment-baseline="hanging">%s</text>' % (x, y, color, outputdim, w, font_name, align, s)
        
        
    # Top texts
    if game is not None:
        g = game.game_data
        #svg += '<line x1="2" y1="%f" x2="20" y2="%f" stroke="black" stroke-width="0.001"/>' % (YLUOGO, YLUOGO)

        hRigaTestata = 0.30
        dimSquadre   = 0.52
        dimParziali  = 0.25
        
        d = datetime.datetime.strptime(g['date'], "%d/%m/%Y")
        day = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica'][d.weekday()]
        svg += text(XSQUADRE, YLUOGO,                day + ' ' + g['date'] + ' Ore ' + g['time'])
        svg += text(X3P,      YLUOGO,                g['location'])
        
        if (g['referee1'] != 'nan' and g['referee1'] != '') or (g['referee2'] != 'nan' and g['referee2'] != ''):
            svg += text(XSQUADRE, YLUOGO + hRigaTestata, 'Arbitri: ' + g['referee1'] + ',  ' + g['referee2'])
        
        svg += text(XRIGHT, YLUOGO,                g['season'], align='end')
        svg += text(XRIGHT, YLUOGO+1*hRigaTestata, g['championship'], align='end')
        svg += text(XRIGHT, YLUOGO+2*hRigaTestata, 'Girone ' + g['phase'], align='end')
        svg += text(XRIGHT, YLUOGO+3*hRigaTestata, str(g['round']) + '.a Giornata', align='end')
        
        # Current score of the two teams
        pt = Stats.points(df)
        po = Stats.points(df, team=Config.OPPO)

        if g['home']:
            svg += text(XSQUADRE, YSQUADRA1, game.team_data['name'].upper(), dim=dimSquadre, w=700)
            svg += text(XSQUADRE, YSQUADRA2, g['opponents'].upper(),         dim=dimSquadre, w=700)

            svg += text(XPUNTEGGIO, YSQUADRA1, str(pt), dim=dimSquadre, w=700)
            svg += text(XPUNTEGGIO, YSQUADRA2, str(po), dim=dimSquadre, w=700)
        else:
            svg += text(XSQUADRE, YSQUADRA1, g['opponents'].upper(),         dim=dimSquadre, w=700)
            svg += text(XSQUADRE, YSQUADRA2, game.team_data['name'].upper(), dim=dimSquadre, w=700)

            svg += text(XPUNTEGGIO, YSQUADRA1, str(po), dim=dimSquadre, w=700)
            svg += text(XPUNTEGGIO, YSQUADRA2, str(pt), dim=dimSquadre, w=700)
            
            
        # Partial score of the teams by quarters
        x = XPARZIALI
        hParziali = dimParziali*1.45

        ptt = 0
        pto = 0
        for q in sorted(df['quarter'].unique()):
            if q < 5: name = 'Q%d'%q
            else:     name = 'S%d'%(q-4)
            
            if quarter is None:
                svg += text(x, YSQUADRA1, name, dim=dimParziali, align='middle')
                dfq = df[df['quarter']==q]
                pqt = Stats.points(dfq)
                pqo = Stats.points(dfq, team=Config.OPPO)
                ptt += pqt
                pto += pqo

                if g['home']:
                    if q == 1:
                        svg += text(x, YSQUADRA1+hParziali,   str(pqt), dim=dimParziali, align='middle')
                        svg += text(x, YSQUADRA1+2*hParziali, str(pqo), dim=dimParziali, align='middle')
                    else:
                        svg += text(x, YSQUADRA1+hParziali,   '%d (%d)'%(pqt,ptt), dim=dimParziali, align='middle')
                        svg += text(x, YSQUADRA1+2*hParziali, '%d (%d)'%(pqo,pto), dim=dimParziali, align='middle')
                else:
                    if q == 1:
                        svg += text(x, YSQUADRA1+hParziali,   str(pqo), dim=dimParziali, align='middle')
                        svg += text(x, YSQUADRA1+2*hParziali, str(pqt), dim=dimParziali, align='middle')
                    else:
                        svg += text(x, YSQUADRA1+hParziali,   '%d (%d)'%(pqo,pto), dim=dimParziali, align='middle')
                        svg += text(x, YSQUADRA1+2*hParziali, '%d (%d)'%(pqt,ptt), dim=dimParziali, align='middle')
            else:
                svg += text(x, YSQUADRA1+0.25, name, dim=dimSquadre, align='middle', w=700)

                    
            x += XPARZIALID

                
    # Grid headers
    y1 = YRIGA0 - 0.55
    hRiga = 0.36
    y2 = y1 + 1.0*hRiga
    svg += text(XSQUADRA, y1+0.4*hRiga, game.team_data['short'].upper(), w=700, dim=0.32, color='white', align='middle')
    
    svg += text(XMINUTI,   y2, 'Minuti',      w=700, color='white', align='middle')
    svg += text(XPUNTI,    y2, 'Pt',          w=700, color='white', align='middle')
    svg += text(X2P,       y1, 'Tiri 2P',     w=700, color='white', align='middle')
    svg += text(X2P_PERC,  y2, '%',           w=700, color='white', align='middle')
    svg += text(X3P,       y1, 'Tiri 3P',     w=700, color='white', align='middle')
    svg += text(X3P_PERC,  y2, '%',           w=700, color='white', align='middle')
    svg += text(XTOTTIRI,  y1, 'Tot. Tiri',   w=700, color='white', align='middle')
    svg += text(XTOT_PERC, y2, '%',           w=700, color='white', align='middle')
    svg += text(X1P,       y1, 'Tiri liberi', w=700, color='white', align='middle')
    svg += text(X1P_PERC,  y2, '%',           w=700, color='white', align='middle')
    svg += text(XASSIST,   y2, 'Ass',         w=700, color='white', align='middle')
    svg += text(XRIMBALZI, y1, 'Rimbalzi',    w=700, color='white', align='middle')
    svg += text(XRDIF,     y2, 'Dif',         w=700, color='white', align='middle')
    svg += text(XROFF,     y2, 'Off',         w=700, color='white', align='middle')
    svg += text(XRTOT,     y2, 'Tot',         w=700, color='white', align='middle')
    svg += text(XFALLI,    y1, 'Falli',       w=700, color='white', align='middle')
    svg += text(XFATTI,    y2, 'Fa',          w=700, color='white', align='middle')
    svg += text(XSUBITI,   y2, 'Su',          w=700, color='white', align='middle')
    svg += text(XPALLE,    y1, 'Palle',       w=700, color='white', align='middle')
    svg += text(XPREC,     y2, 'PR',          w=700, color='white', align='middle')
    svg += text(XPPER,     y2, 'PP',          w=700, color='white', align='middle')
    svg += text(XSTOPPATE, y1, 'Stopp.',      w=700, color='white', align='middle')
    svg += text(XSTOFA,    y2, 'Fa',          w=700, color='white', align='middle')
    svg += text(XSTOSU,    y2, 'Su',          w=700, color='white', align='middle')
    svg += text(XVAL,      y1, 'Val',         w=700, color='white', align='middle')
    svg += text(XVAL,      y2, 'Leg',         w=700, color='white', align='middle')
    svg += text(XOER,      y1, 'Val',         w=700, color='white', align='middle')
    svg += text(XOER,      y2, 'Oer',         w=700, color='white', align='middle')
    svg += text(XVIR,      y1, 'Val',         w=700, color='white', align='middle')
    svg += text(XVIR,      y2, 'VIR',         w=700, color='white', align='middle')
    svg += text(XPLUSMIN,  y1, 'Val',         w=700, color='white', align='middle')
    svg += text(XPLUSMIN,  y2, '+/-',         w=700, color='white', align='middle')
    svg += text(XTRUE,     y1, 'TS',          w=700, color='white', align='middle')
    svg += text(XTRUE,     y2, '%',           w=700, color='white', align='middle')

    
    # Players texts
    y1 = YRIGA0 + 0.2
    hRiga = 0.4
    ysum = y1+13*hRiga-0.01
    
    # Numero maglia
    y = y1
    for number in game.players_numbers:
        svg += text(XNUMERO, y, str(number), color='white')
        y += hRiga
        
    # Nome
    y = y1
    for player_name in game.players_by_number:
        svg += text(XNOME, y, player_name, color='white')
        y += hRiga
    svg += text(XNOME, ysum, 'SQUADRA', color='white')
    
    # Starters
    starters = list(df[(df['team']==Config.TEAM)&(df['quarter']==1)&(df['event_name']=='Entr')&(df['seconds']==600.0)]['player'])[-5:]    # Last 5 players entered on the field at the beginning of 1st quarter
    for player_name in starters:
        if player_name in game.players_by_number:
            pos = game.players_by_number.index(player_name)
            y = y1 + pos*hRiga
            svg += text(XSTARTERS, y, 'Q', align='middle', color='white')
        
    # Minuti in campo
    y = y1
    total_seconds = 0.0
    for player_name in game.players_by_number:
        if player_name in seconds_on_field.keys():
            seconds = seconds_on_field[player_name]
        else:
            seconds = 0.0
        total_seconds += seconds
        if seconds > 0:
            svg += text(XMINUTI, y, '%d\'%02d"'%(seconds//60, int(seconds%60)), align='middle')
        y += hRiga
    if total_seconds > 0.0: svg += text(XMINUTI, ysum, '%d\'%02d"'%(total_seconds//60, int(total_seconds%60)), align='middle', color='white')
    
    # Punti realizzati
    y = y1
    for player_name in game.players_by_number:
        points = Stats.points(df, player_name)
        if points > 0:
            svg += text(XPUNTI, y, str(points), align='middle', w=700)
        y += hRiga
    t = Stats.points(df)
    if t > 0: svg += text(XPUNTI, ysum, str(t), align='middle', color='white', w=700)
        
    # T2
    y = y1
    for player_name in game.players_by_number:
        s,p = Stats.tperc(df, player_name, throw=2)
        if len(s) > 0:
            svg += text(X2P-0.7, y, s)
            svg += text(X2P_PERC+0.15, y, p, align='end')
        y += hRiga
    s,p = Stats.tperc(df, throw=2)
    if len(s) > 0:
        svg += text(X2P-0.7, ysum, s, color='white')
        svg += text(X2P_PERC+0.15, ysum, p, align='end', color='white')
    
    # T3
    y = y1
    for player_name in game.players_by_number:
        s,p = Stats.tperc(df, player_name, throw=3)
        if len(s) > 0:
            svg += text(X3P-0.7, y, s)
            svg += text(X3P_PERC+0.15, y, p, align='end')
        y += hRiga
    s,p = Stats.tperc(df, throw=3)
    if len(s) > 0:
        svg += text(X3P-0.7, ysum, s, color='white')
        svg += text(X3P_PERC+0.15, ysum, p, align='end', color='white')
        
    # T2 + T3
    y = y1
    for player_name in game.players_by_number:
        s,p = Stats.tperc(df, player_name, throw=0)
        if len(s) > 0:
            svg += text(XTOTTIRI-0.7, y, s)
            svg += text(XTOT_PERC+0.15, y, p, align='end')
        y += hRiga
    s,p = Stats.tperc(df, throw=0)
    if len(s) > 0:
        svg += text(XTOTTIRI-0.7, ysum, s, color='white')
        svg += text(XTOT_PERC+0.15, ysum, p, align='end', color='white')
    
    # T1
    y = y1
    for player_name in game.players_by_number:
        s,p = Stats.tperc(df, player_name, throw=1)
        if len(s) > 0:
            svg += text(X1P-0.7, y, s)
            svg += text(X1P_PERC+0.15, y, p, align='end')
        y += hRiga
    s,p = Stats.tperc(df, throw=1)
    if len(s) > 0:
        svg += text(X1P-0.7, ysum, s, color='white')
        svg += text(X1P_PERC+0.15, ysum, p, align='end', color='white')
        

    # ASSIST
    y = y1
    for player_name in game.players_by_number:
        v = Stats.countforplayer(df,player_name,'Ass')
        if v > 0:
            svg += text(XASSIST, y, str(v), align='middle')
        y += hRiga
    t = Stats.countforteam(df,'Ass')
    if t > 0: svg += text(XASSIST, ysum, str(t), align='middle', color='white')
        
        
    # RIMBALZI
    y = y1
    for player_name in game.players_by_number:
        vo = Stats.countforplayer(df,player_name,'ROff')
        if vo > 0: svg += text(XROFF, y, str(vo), align='middle')
        
        vd = Stats.countforplayer(df,player_name,'RDif')
        if vd > 0: svg += text(XRDIF, y, str(vd), align='middle')
        
        if (vd+vo) > 0: svg += text(XRTOT, y, str(vd+vo), align='middle')
        
        y += hRiga
    to = Stats.countforteam(df,'ROff')
    if to > 0: svg += text(XROFF, ysum, str(to), align='middle', color='white')
    td = Stats.countforteam(df,'RDif')
    if to > 0: svg += text(XRDIF, ysum, str(td), align='middle', color='white')
    if (to+td) > 0: svg += text(XRTOT, ysum, str(to+td), align='middle', color='white')

    
    # FALLI
    y = y1
    for player_name in game.players_by_number:
        v = Stats.countforplayer(df,player_name,'FCom')
        if v > 0: svg += text(XFATTI, y, str(v), align='middle')
        
        v = Stats.countforplayer(df,player_name,'FSub')
        if v > 0: svg += text(XSUBITI, y, str(v), align='middle')
        
        y += hRiga
    t = Stats.countforteam(df,'FCom')
    if t > 0: svg += text(XFATTI, ysum, str(t), align='middle', color='white')
    t = Stats.countforteam(df,'FSub')
    if t > 0: svg += text(XSUBITI, ysum, str(t), align='middle', color='white')

    
    # PALLE PERSE E RECUPERATE
    y = y1
    for player_name in game.players_by_number:
        v = Stats.countforplayer(df,player_name,'PRec')
        if v > 0: svg += text(XPREC, y, str(v), align='middle')
        
        v = Stats.countforplayer(df,player_name,'PPer')
        if v > 0: svg += text(XPPER, y, str(v), align='middle')
        
        y += hRiga
    t = Stats.countforteam(df,'PRec')
    if t > 0: svg += text(XPREC, ysum, str(t), align='middle', color='white')
    t = Stats.countforteam(df,'PPer')
    if t > 0: svg += text(XPPER, ysum, str(t), align='middle', color='white')

    
    # STOPPATE
    y = y1
    for player_name in game.players_by_number:
        v = Stats.countforplayer(df,player_name,'SDat')
        if v > 0: svg += text(XSTOFA, y, str(v), align='middle')
        
        v = Stats.countforplayer(df,player_name,'SSub')
        if v > 0: svg += text(XSTOSU, y, str(v), align='middle')
        
        y += hRiga
    t = Stats.countforteam(df,'SDat')
    if t > 0: svg += text(XSTOFA, ysum, str(t), align='middle', color='white')
    t = Stats.countforteam(df,'SSub')
    if t > 0: svg += text(XSTOSU, ysum, str(t), align='middle', color='white')    
    
    
    # Valutazione di lega
    y = y1
    maxv = -1000
    for player_name in game.players_by_number:
        v = Stats.value(df, player_name)
        if v > maxv: maxv = v
    for player_name in game.players_by_number:
        v = Stats.value(df, player_name)
        if player_name in seconds_on_field.keys() and v != 0:
            if v == maxv:
                color = '#008800'
                w = 700
            else:
                color = 'black'
                w = 500
            svg += text(XVAL, y, str(v), align='middle', color=color, w=w)
        y += hRiga
    t = Stats.value(df)
    svg += text(XVAL, ysum, str(t), align='middle', color='white')
        
        
    # Valutazione OER
    y = y1
    maxv = -1000
    for player_name in game.players_by_number:
        v = Stats.oer(df, player_name)
        if v > maxv: maxv = v
    for player_name in game.players_by_number:
        v = Stats.oer(df, player_name)
        if player_name in seconds_on_field.keys() and v != 0:
            if v == maxv:
                color = '#008800'
                w = 700
            else:
                color = 'black'
                w = 500
            svg += text(XOER, y, '%.2f'%v, align='middle', color=color, w=w)
        y += hRiga
    t = Stats.oer(df)
    if t > 0: svg += text(XOER, ysum, '%.2f'%t, align='middle', color='white')
        
        
    # Valutazione VIR
    y = y1
    maxv = -1000
    for player_name in game.players_by_number:
        v = Stats.vir(df, player_name, game.players_info)
        if v > maxv: maxv = v
    for player_name in game.players_by_number:
        v = Stats.vir(df, player_name, game.players_info)
        if player_name in seconds_on_field.keys() and v != 0:
            if v == maxv:
                color = '#008800'
                w = 700
            else:
                color = 'black'
                w = 500
            svg += text(XVIR, y, '%.2f'%v, align='middle', color=color, w=w)
        y += hRiga
    t = Stats.vir(df, players_info=game.players_info)
    if t > 0: svg += text(XVIR, ysum, '%.2f'%t, align='middle', color='white')

    
    # Valutazione PlusMinus
    y = y1
    maxv = -1000
    for player_name in game.players_by_number:
        v = Stats.plusminus(player_name, game.players_info)
        if v > maxv: maxv = v
    for player_name in game.players_by_number:
        v = Stats.plusminus(player_name, game.players_info)
        if player_name in seconds_on_field.keys() and v != 0:
            if v == maxv:
                color = '#008800'
                w = 700
            else:
                color = 'black'
                w = 500
            svg += text(XPLUSMIN, y, str(v), align='middle', color=color, w=w)
        y += hRiga
    t = Stats.plusminus(players_info=game.players_info)
    svg += text(XPLUSMIN, ysum, str(t), align='middle', color='white')
        
        
    # Valutazione TrueShooting
    y = y1
    maxv = -1000
    for player_name in game.players_by_number:
        v = Stats.trueshooting(df, player_name)
        if v > maxv: maxv = v
    for player_name in game.players_by_number:
        if player_name in seconds_on_field.keys():
            t = Stats.trueshooting(df, player_name)
            if t == maxv:
                color = '#008800'
                w = 700
            else:
                color = 'black'
                w = 500
            if t >= 0.0:
                svg += text(XTRUE, y, '%.1f'%t, align='middle', color=color, w=w)
        y += hRiga
    t = Stats.trueshooting(df)
    if t >= 0: svg += text(XTRUE, ysum, '%.1f'%t, align='middle', color='white')
        
    
    # Bottom texts
    y1 = YRIGA0
    hRiga = 0.36
    hRigaNote = 3*hRiga/5
    yNote = y1 + 16*hRiga
    y2 = yNote + 0.3*hRigaNote
    
    svg += text(XLEFT,  y2-0.06, 'Allenatore: ' + game.team_data['trainer'])
    svg += text(XPUNTI, y2-0.06, 'Assistente: ' + game.team_data['assistant'])
    
    dimNote = 0.14
    svg += text(XRIGHT, y2-0.06, 'Rilevazioni statistiche realizzate con pyBasket', dim=dimNote, align='end')
    
    svg += text(XLEFT, yNote + 1.75*hRigaNote, 'Note sulle valutazioni:', dim=dimNote)
    svg += text(XLEFT, yNote + 2.75*hRigaNote, 'Valutazione di Lega = (TL+) - (TL-) + [(T2+) x 2 - (T2-)] + [(T3+) x 3) - (T3-)] + PR - PP + RO + RD + AS - FF + FS + SD - SS', dim=dimNote)
    svg += text(XLEFT, yNote + 3.75*hRigaNote, 'Valutazione OER = Coefficiente di Efficacia Offensiva =  Punti realizzati / Possessi      dove Possessi = T2 + T3 + (TL/2) + PP', dim=dimNote)
    svg += text(XLEFT, yNote + 4.75*hRigaNote, 'Valutazione VIR = Value Index Rating = [(Punti fatti + AS x 1,5 + PR + SD x 0,75 + RO x 1,25 + RD x 0,75 + T3+/2 + FS/2 - FF/2 - ((T3-) + (T2-)) x 0,75 - PP - (TL-)/2) / Minuti giocati]', dim=dimNote)
    svg += text(XLEFT, yNote + 5.75*hRigaNote, 'Valutazione +/- = + Punti segnati dalla squadra - Punti segnati dagli avversari quando il giocatore è in campo', dim=dimNote)
    svg += text(XLEFT, yNote + 6.75*hRigaNote, 'Valutazione TS% = Punti / 2*(NumeroTiriCampo + 0.44*NumeroTiriLiberi) - True Shooting Percentage', dim=dimNote)
    
    
    # Sintesi dei punti
    dimSintesi = 0.24
    
    pt = []
    po = []
    for player_name in game.players_by_number:
        if player_name not in seconds_on_field.keys() or seconds_on_field[player_name]==0: pt.append('%s ne'%player_name)
        else:
            ps = Stats.points(df, player_name)
            if ps > 0:  pt.append('%s %d'%(player_name, ps))
            else:       pt.append(player_name)
                
    for player_name in game.opponents_by_number:
        points = Stats.points(df, player_name, team=Config.OPPO)
        
        # Recover opponent points from the game if greater than the numbers calculated from the events
        if player_name in game.game_data['opponents_info']:
            p = game.game_data['opponents_info'][player_name]['points']
            if p > points: points = p
        
        if points > 0: po.append('%s %d'%(player_name,points))
        else:
            if quarter is None:
                if player_name in game.game_data['opponents_info']:
                    points = game.game_data['opponents_info'][player_name]['points']
                    if points > 0: po.append('%s %d'%(player_name,points))
                    else:          po.append(player_name)
            else:
                po.append(player_name)
    
    if g['home']:
        svg += text(XLEFT, yNote + 8.1*hRigaNote,   game.team_data['name'].upper() + ': ', dim=dimSintesi)
        svg += text(XLEFT, yNote + 9.6*hRigaNote,   g['opponents'].upper() + ': ',         dim=dimSintesi)
        svg += text(XMINUTI-0.1, yNote + 8.1*hRigaNote, ', '.join(pt), dim=dimSintesi)
        svg += text(XMINUTI-0.1, yNote + 9.6*hRigaNote, ', '.join(po), dim=dimSintesi)
    else:
        svg += text(XLEFT, yNote + 8.1*hRigaNote,   g['opponents'].upper() + ': ',         dim=dimSintesi)
        svg += text(XLEFT, yNote + 9.6*hRigaNote,   game.team_data['name'].upper() + ': ', dim=dimSintesi)
        svg += text(XMINUTI-0.1, yNote + 8.1*hRigaNote, ', '.join(po), dim=dimSintesi)
        svg += text(XMINUTI-0.1, yNote + 9.6*hRigaNote, ', '.join(pt), dim=dimSintesi)
    
    svg += '</svg>'
    return svg


###########################################################################################################################################################################
# Returns the BoxScore in html format (full screen) as a string
###########################################################################################################################################################################
def html(df, game, team_logo_img=None):
    return '<html><body><div style="text-align:center;">%s</div></body></html>'%svg(df, game=game, team_logo_img=team_logo_img, width=90.0)




###########################################################################################################################################################################
# Returns the overall BoxScore in svg format
###########################################################################################################################################################################
def totalsvg(df, game, players_info, average=False, team_logo_img=None, width=80):   # Dimensioning in vw/vh
    
    # Add number of games played to all players
    for player_name, info in players_info.items():
        info['games'] = len(df[(df['player']==player_name)&(df['event']==18)]['game_number'].unique())
    
    players_by_number = [x[0] for x in sorted([[x[1]['name'],x[1]['number']] for x in players_info.items() if x[1]['games'] > 0], key=lambda x: int(x[1]))]
    players_numbers   = [x[1] for x in sorted([[x[1]['name'],x[1]['number']] for x in players_info.items() if x[1]['games'] > 0], key=lambda x: int(x[1]))]
        
    height = 2.005*FORM_FACTOR*width    # 2 means that 1vw = 2vh in general screens
    
    svgwidth  = IMAGE_WIDTH_IN_PIXELS  / 100.0    # 21.30
    svgheight = IMAGE_HEIGHT_IN_PIXELS / 100.0    # 10.90
    
    preserve = 'xMidYMin meet'    # Center the chart in the parent
    svg = '''<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xml:space="preserve"
viewBox="0 0 %f %f"
preserveAspectRatio="%s"
width="%fvw"
height="%fvh">''' % (svgwidth,svgheight, preserve, width,height)

    svg += '''
    <style type="text/css">
       @import url('%s');
    </style>
    ''' % font_url
    
    # Fill modes
    white   = 'fill="white"'
    black   = 'fill="black"'
    darkred = 'fill="#9c0000"'
    red     = 'fill="#c00000"'
    grey    = 'fill="#dcdcdc"'

    # Stroke modes
    none   = 'stroke-width="0"'
    xsmall = 'stroke="black" stroke-width="0.001"'
    small  = 'stroke="black" stroke-width="0.012"'
    medium = 'stroke="black" stroke-width="0.038"'
    
    
    # Background
    svg += '<rect x="0" y="0" width="%f" height="%f" %s %s></rect>' % (svgwidth,svgheight, white, none)
    
    #svg += '<text x="10.0" y="5.0" fill="black" stroke="none" font-size="2.0" font-weight="400" font-family="Roboto">prova</text>'
    #svg += '</svg>'
    #return svg


    # Background image
    backimg = Image.open('./resources/BoxScore.png')
    backimgbase64 = colors.image2Base64(backimg)
    svg += '<image x="0.0" y="0.0" width="%f" height="%f" href="%s" preserveAspectRatio="xMidYMid meet"></image>'%(svgwidth, svgheight, backimgbase64)
    
    #svg += '<rect x="5.0" y="4.0" width="12.0" height="2.0" %s %s></rect>' % (red, small)
    #svg += '<rect x="5.0" y="1.0" width="12.0" height="2.0" %s %s></rect>' % (darkred, medium)
    
    # Team logo
    imgbase64 = None
    if game is not None:
        imgbase64 = colors.image2Base64(game.team_logo_img)
    else:
        if team_logo_img is not None :
            imgbase64 = colors.image2Base64(team_logo_img)
            
    if imgbase64 is not None:
        svg += '<image x="0.55" y="-0.1" width="1.9" height="2.5" href="%s" preserveAspectRatio="xMidYMid meet"></image>'%imgbase64

        
    # DrawText internal function
    def text(x, y, s, dim=0.25, w=500, align='start', color='black'):
        return '<text x="%f" y="%f" fill="%s" stroke="none" font-size="%f" font-weight="%d" font-family="%s" text-anchor="%s" alignment-baseline="hanging">%s</text>' % (x, y, color, dim, w, font_name, align, s)
        
        
    # Top texts
    if game is not None:
        #svg += '<line x1="2" y1="%f" x2="20" y2="%f" stroke="black" stroke-width="0.001"/>' % (YLUOGO, YLUOGO)

        hRigaTestata = 0.30
        dimSquadre   = 0.52
        dimParziali  = 0.25
        
        tot_win = 0
        tot_los = 0
        tot_pt  = 0
        tot_po  = 0
        home_win = 0
        home_los = 0
        home_pt  = 0
        home_po  = 0
        home_win_pt = 0
        home_win_po = 0
        home_los_pt = 0
        home_los_po = 0
        away_win = 0
        away_los = 0
        away_pt  = 0
        away_po  = 0
        away_win_pt = 0
        away_win_po = 0
        away_los_pt = 0
        away_los_po = 0
        for n in df['game_number'].unique():
            dg = df[df['game_number']==n]
            pt = Stats.points(dg)
            po = Stats.points(dg, team=Config.OPPO)
            tot_pt += pt
            tot_po += po
            home = list(dg.head(1)['home'])[0]

            if home:
                home_pt += pt
                home_po += po
            else:
                away_pt += pt
                away_po += po
            
            if pt > po:
                tot_win += 1
                if home:
                    home_win += 1
                    home_win_pt += pt
                    home_win_po += po
                else:
                    away_win += 1
                    away_win_pt += pt
                    away_win_po += po
            else:
                tot_los += 1
                if home:
                    home_los += 1
                    home_los_pt += pt
                    home_los_po += po
                else:
                    away_los += 1
                    away_los_pt += pt
                    away_los_po += po
        
        tot_games  = tot_win  + tot_los
        home_games = home_win + home_los
        away_games = away_win + away_los
        
        if tot_games > 0:
            svg += text(XSQUADRE,     YLUOGO, 'Dati complessivi dopo %d partite giocate:'%(len(df['game_number'].unique())), dim=dimParziali)
            svg += text(X3P_PERC-0.3, YLUOGO, '%d vinte'%tot_win, dim=dimParziali)
            svg += text(XTOTTIRI-0.2, YLUOGO, '%d perse'%tot_los, dim=dimParziali)
            svg += text(X1P-0.9,      YLUOGO, '%.2f%% vittorie'%(100.0*tot_win/tot_games), dim=dimParziali)
            
            svg += text(XSQUADRE,     YLUOGO + 1*hRigaTestata, 'N. %d partite giocate in casa:'%len(df[df['home']==True]['game_number'].unique()),       dim=dimParziali)
            svg += text(X3P_PERC-0.3, YLUOGO + 1*hRigaTestata, '%d vinte'%home_win, dim=dimParziali)
            svg += text(XTOTTIRI-0.2, YLUOGO + 1*hRigaTestata, '%d perse'%home_los, dim=dimParziali)
            if home_games > 0:
                svg += text(X1P-0.9,      YLUOGO + 1*hRigaTestata, '%.2f%% vittorie'%(100.0*home_win/home_games), dim=dimParziali)
                
            svg += text(XSQUADRE,     YLUOGO + 2*hRigaTestata, 'N. %d partite giocate in trasferta:'%len(df[df['home']==False]['game_number'].unique()), dim=dimParziali)
            svg += text(X3P_PERC-0.3, YLUOGO + 2*hRigaTestata, '%d vinte'%away_win, dim=dimParziali)
            svg += text(XTOTTIRI-0.2, YLUOGO + 2*hRigaTestata, '%d perse'%away_los, dim=dimParziali)
            
            if away_games > 0:
                svg += text(X1P-0.9,      YLUOGO + 2*hRigaTestata, '%.2f%% vittorie'%(100.0*away_win/away_games), dim=dimParziali)
        
        svg += text(XRIGHT, YLUOGO,                game.game_data['season'], align='end')
        svg += text(XRIGHT, YLUOGO+1*hRigaTestata, game.game_data['championship'], align='end')
        if average:
            svg += text(XRIGHT, YLUOGO+2*hRigaTestata, 'Dati complessivi medi', align='end')
        else:
            svg += text(XRIGHT, YLUOGO+2*hRigaTestata, 'Dati complessivi totali', align='end')
        
        # Total points scored
        pt = Stats.points(df)
        po = Stats.points(df, team=Config.OPPO)

        svg += text(XSQUADRE, YSQUADRA1+0.7*hRigaTestata, game.team_data['name'].upper(), dim=dimSquadre, w=700)
        svg += text(XSQUADRE, YSQUADRA2+0.7*hRigaTestata, 'Squadre avversarie',           dim=dimSquadre, w=700)

        if tot_games > 0:
            svg += text(X1P-1.5, YSQUADRA1+0.7*hRigaTestata, '%.2f'%(pt/tot_games), dim=dimSquadre, w=700)
            svg += text(X1P-1.5, YSQUADRA2+0.7*hRigaTestata, '%.2f'%(po/tot_games), dim=dimSquadre, w=700)
        
        svg += text(XASSIST-1.25, YSQUADRA1+0.7*hRigaTestata, '(%d p.segnati)'%pt, dim=dimSquadre, color='#777777')
        svg += text(XASSIST-1.25, YSQUADRA2+0.7*hRigaTestata, '(%d p.subiti)'%po,  dim=dimSquadre, color='#777777')

        
        # Punti segnati e subiti in casa/trasferta nelle vittorie e nelle sconfitte
        x = XSTOPPATE-1.5
        hParziali = dimParziali*1.45
        dx = 1.0

        svg += text(x,        YSQUADRA1+0.3, 'CASA',   dim=dimParziali, align='middle')
        svg += text(x+1*dx,   YSQUADRA1+0.3, 'W',      dim=dimParziali, align='middle')
        svg += text(x+2*dx,   YSQUADRA1+0.3, 'L',      dim=dimParziali, align='middle')
        svg += text(x+3.5*dx, YSQUADRA1+0.3, 'TRASF.', dim=dimParziali, align='middle')
        svg += text(x+4.5*dx, YSQUADRA1+0.3, 'W',      dim=dimParziali, align='middle')
        svg += text(x+5.5*dx, YSQUADRA1+0.3, 'L',      dim=dimParziali, align='middle')
        
        if home_games > 0:
            svg += text(x, YSQUADRA2+0.4*hRigaTestata, '%.2f'%(home_pt/home_games), dim=dimParziali, align='middle')
            svg += text(x, YSQUADRA2+1.4*hRigaTestata, '%.2f'%(home_po/home_games), dim=dimParziali, align='middle')

        if home_win > 0:
            svg += text(x+1*dx, YSQUADRA2+0.4*hRigaTestata, '%.2f'%(home_win_pt/home_win), dim=dimParziali, align='middle')
            svg += text(x+1*dx, YSQUADRA2+1.4*hRigaTestata, '%.2f'%(home_win_po/home_win), dim=dimParziali, align='middle')
        
        if home_los > 0:
            svg += text(x+2*dx, YSQUADRA2+0.4*hRigaTestata, '%.2f'%(home_los_pt/home_los), dim=dimParziali, align='middle')
            svg += text(x+2*dx, YSQUADRA2+1.4*hRigaTestata, '%.2f'%(home_los_po/home_los), dim=dimParziali, align='middle')
        
        if away_games > 0:
            svg += text(x+3.5*dx, YSQUADRA2+0.4*hRigaTestata, '%.2f'%(away_pt/away_games), dim=dimParziali, align='middle')
            svg += text(x+3.5*dx, YSQUADRA2+1.4*hRigaTestata, '%.2f'%(away_po/away_games), dim=dimParziali, align='middle')
        
        if away_win > 0:
            svg += text(x+4.5*dx, YSQUADRA2+0.4*hRigaTestata, '%.2f'%(away_win_pt/away_win), dim=dimParziali, align='middle')
            svg += text(x+4.5*dx, YSQUADRA2+1.4*hRigaTestata, '%.2f'%(away_win_po/away_win), dim=dimParziali, align='middle')

        if away_los > 0:
            svg += text(x+5.5*dx, YSQUADRA2+0.4*hRigaTestata, '%.2f'%(away_los_pt/away_los), dim=dimParziali, align='middle')
            svg += text(x+5.5*dx, YSQUADRA2+1.4*hRigaTestata, '%.2f'%(away_los_po/away_los), dim=dimParziali, align='middle')
        
        
    # Grid headers
    y1 = YRIGA0 - 0.55
    hRiga = 0.36
    y2 = y1 + 1.0*hRiga
    svg += text(XSQUADRA, y1+0.4*hRiga, game.team_data['short'].upper(), w=700, dim=0.32, color='white', align='middle')
    
    svg += text(XMINUTI,   y2, 'Minuti',      w=700, color='white', align='middle')
    svg += text(XPUNTI,    y2, 'Pt',          w=700, color='white', align='middle')
    svg += text(X2P,       y1, 'Tiri 2P',     w=700, color='white', align='middle')
    svg += text(X2P_PERC,  y2, '%',           w=700, color='white', align='middle')
    svg += text(X3P,       y1, 'Tiri 3P',     w=700, color='white', align='middle')
    svg += text(X3P_PERC,  y2, '%',           w=700, color='white', align='middle')
    svg += text(XTOTTIRI,  y1, 'Tot. Tiri',   w=700, color='white', align='middle')
    svg += text(XTOT_PERC, y2, '%',           w=700, color='white', align='middle')
    svg += text(X1P,       y1, 'Tiri liberi', w=700, color='white', align='middle')
    svg += text(X1P_PERC,  y2, '%',           w=700, color='white', align='middle')
    svg += text(XASSIST,   y2, 'Ass',         w=700, color='white', align='middle')
    svg += text(XRIMBALZI, y1, 'Rimbalzi',    w=700, color='white', align='middle')
    svg += text(XRDIF,     y2, 'Dif',         w=700, color='white', align='middle')
    svg += text(XROFF,     y2, 'Off',         w=700, color='white', align='middle')
    svg += text(XRTOT,     y2, 'Tot',         w=700, color='white', align='middle')
    svg += text(XFALLI,    y1, 'Falli',       w=700, color='white', align='middle')
    svg += text(XFATTI,    y2, 'Fa',          w=700, color='white', align='middle')
    svg += text(XSUBITI,   y2, 'Su',          w=700, color='white', align='middle')
    svg += text(XPALLE,    y1, 'Palle',       w=700, color='white', align='middle')
    svg += text(XPREC,     y2, 'PR',          w=700, color='white', align='middle')
    svg += text(XPPER,     y2, 'PP',          w=700, color='white', align='middle')
    svg += text(XSTOPPATE, y1, 'Stopp.',      w=700, color='white', align='middle')
    svg += text(XSTOFA,    y2, 'Fa',          w=700, color='white', align='middle')
    svg += text(XSTOSU,    y2, 'Su',          w=700, color='white', align='middle')
    svg += text(XVAL,      y1, 'Val',         w=700, color='white', align='middle')
    svg += text(XVAL,      y2, 'Leg',         w=700, color='white', align='middle')
    svg += text(XOER,      y1, 'Val',         w=700, color='white', align='middle')
    svg += text(XOER,      y2, 'Oer',         w=700, color='white', align='middle')
    svg += text(XVIR,      y1, 'Val',         w=700, color='white', align='middle')
    svg += text(XVIR,      y2, 'VIR',         w=700, color='white', align='middle')
    svg += text(XPLUSMIN,  y1, 'Val',         w=700, color='white', align='middle')
    svg += text(XPLUSMIN,  y2, '+/-',         w=700, color='white', align='middle')
    svg += text(XTRUE,     y1, 'TS',          w=700, color='white', align='middle')
    svg += text(XTRUE,     y2, '%',           w=700, color='white', align='middle')

    
    # Players texts
    y1 = YRIGA0 + 0.2
    hRiga = 0.4
    ysum = y1+13*hRiga+0.02
    
    # Numero maglia
    y = y1
    for number in players_numbers:
        svg += text(XNUMERO, y, str(number), color='white')
        y += hRiga
        
    # Nome
    y = y1
    for player_name in players_by_number:
        svg += text(XNOME, y, player_name, color='white')
        y += hRiga
    svg += text(XNOME, ysum, 'SQUADRA', color='white')
    
    # Number of games played
    for player_name in players_by_number:
        ngames = players_info[player_name]['games']
        pos = players_by_number.index(player_name)
        y = y1 + pos*hRiga
        svg += text(XSTARTERS+0.19, y+0.05, '%d p.'%ngames, align='end', color='white', dim=0.23, w=300)
        
    # Minuti in campo
    y = y1
    total_seconds = 0.0
    for player_name in players_by_number:
        seconds = players_info[player_name]['time_on_field']
        total_seconds += seconds
        if average: seconds /= players_info[player_name]['games']
        if seconds > 0:
            svg += text(XMINUTI, y, '%d\'%02d"'%(seconds//60, int(seconds%60)), align='middle')
        y += hRiga
    if total_seconds > 0.0:
        if average: total_seconds /= tot_games
        svg += text(XMINUTI, ysum, '%d\'%02d"'%(total_seconds//60, int(total_seconds%60)), align='middle', color='white')
    
    # Punti realizzati
    y = y1
    for player_name in players_by_number:
        points = Stats.points(df, player_name)
        if points > 0:
            if average:
                points /= players_info[player_name]['games']
                svg += text(XPUNTI, y, '%.1f'%points, align='middle', w=700, dim=0.24)
            else:
                svg += text(XPUNTI, y, str(points), align='middle', w=700)
        y += hRiga
    t = Stats.points(df)
    if t > 0:
        if average:
            t /= tot_games
            svg += text(XPUNTI, y, '%.1f'%t, align='middle', color='white', w=700, dim=0.23)
        else:
            svg += text(XPUNTI, ysum, str(t), align='middle', color='white', w=700, dim=0.23)
        
    # T2
    y = y1
    for player_name in players_by_number:
        s,p = Stats.tperc(df, player_name, throw=2)
        if len(s) > 0:
            svg += text(X2P-0.7, y, s)
            svg += text(X2P_PERC+0.15, y, p, align='end')
        y += hRiga
    s,p = Stats.tperc(df, throw=2)
    if len(s) > 0:
        svg += text(X2P-0.8, ysum, s, color='white', dim=0.23)
        svg += text(X2P_PERC+0.15, ysum, p, align='end', color='white', dim=0.23)
    
    # T3
    y = y1
    for player_name in players_by_number:
        s,p = Stats.tperc(df, player_name, throw=3)
        if len(s) > 0:
            svg += text(X3P-0.7, y, s)
            svg += text(X3P_PERC+0.15, y, p, align='end')
        y += hRiga
    s,p = Stats.tperc(df, throw=3)
    if len(s) > 0:
        svg += text(X3P-0.85, ysum, s, color='white', dim=0.23)
        svg += text(X3P_PERC+0.15, ysum, p, align='end', color='white', dim=0.23)
        
    # T2 + T3
    y = y1
    for player_name in players_by_number:
        s,p = Stats.tperc(df, player_name, throw=0)
        if len(s) > 0:
            svg += text(XTOTTIRI-0.7, y, s)
            svg += text(XTOT_PERC+0.15, y, p, align='end')
        y += hRiga
    s,p = Stats.tperc(df, throw=0)
    if len(s) > 0:
        svg += text(XTOTTIRI-0.8, ysum, s, color='white', dim=0.23)
        svg += text(XTOT_PERC+0.15, ysum, p, align='end', color='white', dim=0.23)
    
    # T1
    y = y1
    for player_name in players_by_number:
        s,p = Stats.tperc(df, player_name, throw=1)
        if len(s) > 0:
            svg += text(X1P-0.7, y, s)
            svg += text(X1P_PERC+0.15, y, p, align='end')
        y += hRiga
    s,p = Stats.tperc(df, throw=1)
    if len(s) > 0:
        svg += text(X1P-0.85, ysum, s, color='white', dim=0.23)
        svg += text(X1P_PERC+0.15, ysum, p, align='end', color='white', dim=0.23)
        

    # ASSIST
    y = y1
    for player_name in players_by_number:
        v = Stats.countforplayer(df,player_name,'Ass')
        if v > 0:
            if average:
                v /= players_info[player_name]['games']
                svg += text(XASSIST, y, '%.1f'%v, align='middle')
            else:
                svg += text(XASSIST, y, str(v), align='middle')
        y += hRiga
    t = Stats.countforteam(df,'Ass')
    if t > 0:
        if average:
            t /= tot_games
            svg += text(XASSIST, ysum, '%.1f'%t, align='middle', color='white', dim=0.23)
        else:
            svg += text(XASSIST, ysum, str(t), align='middle', color='white', dim=0.23)
        
    # RIMBALZI
    y = y1
    for player_name in players_by_number:
        vo = Stats.countforplayer(df,player_name,'ROff')
        if vo > 0: 
            if average:
                svg += text(XROFF, y, '%.1f'%(vo/players_info[player_name]['games']), align='middle')
            else:
                svg += text(XROFF, y, str(vo), align='middle')
        
        vd = Stats.countforplayer(df,player_name,'RDif')
        if vd > 0:
            if average:
                svg += text(XRDIF, y, '%.1f'%(vd/players_info[player_name]['games']), align='middle')
            else:
                svg += text(XRDIF, y, str(vd), align='middle')
        
        if (vd+vo) > 0: 
            if average:
                vt = (vd+vo) / players_info[player_name]['games']
                svg += text(XRTOT, y, '%.1f'%vt, align='middle')
            else:
                svg += text(XRTOT, y, str(vd+vo), align='middle')
        
        y += hRiga
    to = Stats.countforteam(df,'ROff')
    if to > 0:
        if average:
            svg += text(XROFF, ysum, '%.1f'%(to/tot_games), align='middle', color='white', dim=0.23)
        else:
            svg += text(XROFF, ysum, str(to), align='middle', color='white', dim=0.23)
        
    td = Stats.countforteam(df,'RDif')
    if to > 0:
        if average:
            svg += text(XRDIF, ysum, '%.1f'%(td/tot_games), align='middle', color='white', dim=0.23)
        else:
            svg += text(XRDIF, ysum, str(td), align='middle', color='white', dim=0.23)
    
    if (to+td) > 0:
        if average:
            tt = (to+td) / tot_games
            svg += text(XRTOT, ysum, '%.1f'%tt, align='middle', color='white', dim=0.23)
        else:
            svg += text(XRTOT, ysum, str(to+td), align='middle', color='white', dim=0.23)

    
    # FALLI
    y = y1
    for player_name in players_by_number:
        v = Stats.countforplayer(df,player_name,'FCom')
        if v > 0:
            if average:
                svg += text(XFATTI, y, '%.1f'%(v/players_info[player_name]['games']), align='middle')
            else:
                svg += text(XFATTI, y, str(v), align='middle')
        
        v = Stats.countforplayer(df,player_name,'FSub')
        if v > 0:
            if average:
                svg += text(XSUBITI, y, '%.1f'%(v/players_info[player_name]['games']), align='middle')
            else:
                svg += text(XSUBITI, y, str(v), align='middle')
        
        y += hRiga
    
    t = Stats.countforteam(df,'FCom')
    if t > 0:
        if average:
            svg += text(XFATTI-0.05, ysum, '%.1f'%(t/tot_games), align='middle', color='white', dim=0.23)
        else:
            svg += text(XFATTI-0.05, ysum, str(t), align='middle', color='white', dim=0.23)
    
    t = Stats.countforteam(df,'FSub')
    if t > 0:
        if average:
            svg += text(XSUBITI+0.02, ysum, '%.1f'%(t/tot_games), align='middle', color='white', dim=0.23)
        else:
            svg += text(XSUBITI+0.02, ysum, str(t), align='middle', color='white', dim=0.23)

    
    # PALLE PERSE E RECUPERATE
    y = y1
    for player_name in players_by_number:
        v = Stats.countforplayer(df,player_name,'PRec')
        if v > 0:
            if average:
                svg += text(XPREC, y, '%.1f'%(v/players_info[player_name]['games']), align='middle')
            else:
                svg += text(XPREC, y, str(v), align='middle')
        
        v = Stats.countforplayer(df,player_name,'PPer')
        if v > 0:
            if average:
                svg += text(XPPER, y, '%.1f'%(v/players_info[player_name]['games']), align='middle')
            else:
                svg += text(XPPER, y, str(v), align='middle')
        
        y += hRiga
    
    t = Stats.countforteam(df,'PRec')
    if t > 0:
        if average:
            svg += text(XPREC-0.05, ysum, '%.1f'%(t/tot_games), align='middle', color='white', dim=0.23)
        else:
            svg += text(XPREC-0.05, ysum, str(t), align='middle', color='white', dim=0.23)
        
    t = Stats.countforteam(df,'PPer')
    if t > 0:
        if average:
            svg += text(XPPER+0.02, ysum, '%.1f'%(t/tot_games), align='middle', color='white', dim=0.23)
        else:
            svg += text(XPPER+0.02, ysum, str(t), align='middle', color='white', dim=0.23)

    
    # STOPPATE
    y = y1
    for player_name in players_by_number:
        v = Stats.countforplayer(df,player_name,'SDat')
        if v > 0:
            if average:
                svg += text(XSTOFA, y, '%.1f'%(v/players_info[player_name]['games']), align='middle')
            else:
                svg += text(XSTOFA, y, str(v), align='middle')
        
        v = Stats.countforplayer(df,player_name,'SSub')
        if v > 0:
            if average:
                svg += text(XSTOSU+0.02, y, '%.1f'%(v/players_info[player_name]['games']), align='middle')
            else:
                svg += text(XSTOSU+0.02, y, str(v), align='middle')
        
        y += hRiga
    
    t = Stats.countforteam(df,'SDat')
    if t > 0:
        if average:
            svg += text(XSTOFA-0.02, ysum, '%.1f'%(t/tot_games), align='middle', color='white', dim=0.23)
        else:
            svg += text(XSTOFA-0.02, ysum, str(t), align='middle', color='white', dim=0.23)
        
    t = Stats.countforteam(df,'SSub')
    if t > 0:
        if average:
            svg += text(XSTOSU+0.02, ysum, '%.1f'%(t/tot_games), align='middle', color='white', dim=0.23)
        else:
            svg += text(XSTOSU+0.02, ysum, str(t), align='middle', color='white', dim=0.23)
    
    
    # Valutazione di lega
    y = y1
    for player_name in players_by_number:
        if players_info[player_name]['time_on_field'] > 0:
            v = Stats.value(df, player_name)
            if average:
                svg += text(XVAL, y, '%.1f'%(v/players_info[player_name]['games']), align='middle')
            else:
                svg += text(XVAL, y, str(v), align='middle')
        y += hRiga
    t = Stats.value(df)
    if average:
        svg += text(XVAL, ysum, '%.1f'%(t/tot_games), align='middle', color='white', dim=0.23)        
    else:
        svg += text(XVAL, ysum, str(t), align='middle', color='white', dim=0.23)        
        
    # Valutazione OER
    y = y1
    for player_name in players_by_number:
        if players_info[player_name]['time_on_field'] > 0:
            svg += text(XOER, y, '%.2f'%Stats.oer(df, player_name), align='middle')
        y += hRiga
    t = Stats.oer(df)
    if t > 0: svg += text(XOER, ysum, '%.2f'%t, align='middle', color='white', dim=0.23)
        
    # Valutazione VIR
    y = y1
    for player_name in players_by_number:
        if players_info[player_name]['time_on_field'] > 0:
            svg += text(XVIR, y, '%.2f'%Stats.vir(df, player_name, players_info), align='middle')
        y += hRiga
    t = Stats.vir(df, players_info=players_info)
    if t > 0: svg += text(XVIR, ysum, '%.2f'%t, align='middle', color='white', dim=0.23)

    # Valutazione PlusMinus
    y = y1
    for player_name in players_by_number:
        if players_info[player_name]['time_on_field'] > 0:
            svg += text(XPLUSMIN, y, str(Stats.plusminus(player_name, players_info)), align='middle')
        y += hRiga
    t = Stats.plusminus(players_info=players_info)
    svg += text(XPLUSMIN, ysum, str(t), align='middle', color='white', dim=0.23)
        
    # Valutazione TrueShooting
    y = y1
    for player_name in players_by_number:
        if players_info[player_name]['time_on_field'] > 0:
            svg += text(XTRUE, y, '%.1f'%Stats.trueshooting(df, player_name), align='middle')
        y += hRiga
    t = Stats.trueshooting(df)
    if t > 0: svg += text(XTRUE, ysum, '%.1f'%t, align='middle', color='white', dim=0.23)
        
    
    # Bottom texts
    y1 = YRIGA0
    hRiga = 0.36
    hRigaNote = 3*hRiga/5
    yNote = y1 + 16*hRiga
    y2 = yNote + 0.3*hRigaNote
    
    svg += text(XLEFT,  y2-0.06, 'Allenatore: ' + game.team_data['trainer'])
    svg += text(XPUNTI, y2-0.06, 'Assistente: ' + game.team_data['assistant'])
    
    dimNote = 0.14
    svg += text(XRIGHT, y2-0.06, 'Rilevazioni statistiche realizzate con pyBasket', dim=dimNote, align='end')
    
    svg += text(XLEFT, yNote + 1.75*hRigaNote, 'Note sulle valutazioni:', dim=dimNote)
    svg += text(XLEFT, yNote + 2.75*hRigaNote, 'Valutazione di Lega = (TL+) - (TL-) + [(T2+) x 2 - (T2-)] + [(T3+) x 3) - (T3-)] + PR - PP + RO + RD + AS - FF + FS + SD - SS', dim=dimNote)
    svg += text(XLEFT, yNote + 3.75*hRigaNote, 'Valutazione OER = Coefficiente di Efficacia Offensiva =  Punti realizzati / Possessi      dove Possessi = T2 + T3 + (TL/2) + PP', dim=dimNote)
    svg += text(XLEFT, yNote + 4.75*hRigaNote, 'Valutazione VIR = Value Index Rating = [(Punti fatti + AS x 1,5 + PR + SD x 0,75 + RO x 1,25 + RD x 0,75 + T3+/2 + FS/2 - FF/2 - ((T3-) + (T2-)) x 0,75 - PP - (TL-)/2) / Minuti giocati]', dim=dimNote)
    svg += text(XLEFT, yNote + 5.75*hRigaNote, 'Valutazione +/- = + Punti segnati dalla squadra - Punti segnati dagli avversari quando il giocatore è in campo', dim=dimNote)
    svg += text(XLEFT, yNote + 6.75*hRigaNote, 'Valutazione TS% = Punti / 2*(NumeroTiriCampo + 0.44*NumeroTiriLiberi) - True Shooting Percentage', dim=dimNote)
    
    svg += '</svg>'
    return svg


###########################################################################################################################################################################
# Returns the game summary as a string
###########################################################################################################################################################################
def summary(df, game):
    home = game.game_data['home']
    
    # Result
    pt = Stats.points(df)
    po = Stats.points(df, team=Config.OPPO)
    if home:
        t1 = game.team_data['name'] + ' - ' + game.game_data['opponents'] + '  ' + str(pt) + '-' + str(po)
    else:
        t1 = game.game_data['opponents'] + ' - ' + game.team_data['name'] + '  ' + str(po) + '-' + str(pt)
        
    # DTS
    nquarters = df['quarter'].unique()
    if len(nquarters) > 4:
        t1 += 'd%dts'%(nquarters-4)
    
    # Points scored
    pt = []
    po = []
    for player_name in game.players_by_number:
        points = Stats.points(df, player_name)
        if game.players_info[player_name]['time_on_field'] <= 0.0:
            pt.append('%s ne'%player_name)
        else:
            if points > 0: pt.append('%s %d'%(player_name, points))
            else:          pt.append(player_name)
        
    for player_name in game.opponents_by_number:
        points = Stats.points(df, player_name, team=Config.OPPO)
        
        # Recover opponent points from the game if greater than the numbers calculated from the events
        if player_name in game.game_data['opponents_info']:
            p = game.game_data['opponents_info'][player_name]['points']
            if p > points: points = p
                
        if points > 0: po.append('%s %d'%(player_name,points))
        else:          po.append(player_name)
        
    if home:
        t2 = game.team_data['name']      + ': ' + ', '.join(pt) + '.\nAllenatore: ' + game.team_data['trainer']
        t3 = game.game_data['opponents'] + ': ' + ', '.join(po) + '.\nAllenatore: ' + game.game_data['trainer']
    else:
        t2 = game.game_data['opponents'] + ': ' + ', '.join(po) + '.\nAllenatore: ' + game.game_data['trainer']
        t3 = game.team_data['name']      + ': ' + ', '.join(pt) + '.\nAllenatore: ' + game.team_data['trainer']
       
    # Quarters
    t4 = 'Parziali: '
    t5 = 'Progressivi: '
    par = []
    pro = []
    ptt = 0
    pto = 0
    for q in sorted(df['quarter'].unique()):
        dfq = df[df['quarter']==q]
        pt = Stats.points(dfq)
        po = Stats.points(dfq, team=Config.OPPO)
        ptt += pt
        pto += po
        if home:
            par.append('%d-%d'%(pt,po))
            pro.append('%d-%d'%(ptt,pto))
        else:
            par.append('%d-%d'%(po,pt))
            pro.append('%d-%d'%(pto,ptt))
    
    t4 += ', '.join(par) + '.'
    t5 += ', '.join(pro) + '.'
    
    # 5 fouls
    t6 = ''
    ft = []
    fo = []
    for player_name in game.players_by_number:
        f = Stats.fouls(df, player_name)
        if f >= 5:                       
            ft.append(player_name)
        
    for player_name in game.opponents_by_number:
        f = Stats.fouls(df, player_name, team=Config.OPPO)
        if f >= 5:                       
            fo.append(player_name)
    
    if len(ft) == 0 and len(fo) == 0:
        t6 += 'Nessuno.'
    else:
        if home:
            if len(ft) > 0:
                t6 += ', '.join(ft) + ' (' + game.team_data['name'] + ')'
            if len(fo) > 0:
                if len(t6) > 0: t6 += '; '
                t6 += ', '.join(fo) + ' (' + game.game_data['opponents'] + ')'
        else:
            if len(fo) > 0:
                t6 += ', '.join(fo) + ' (' + game.game_data['opponents'] + ')'
            if len(ft) > 0:
                if len(t6) > 0: t6 += '; '
                t6 += ', '.join(ft) + ' (' + game.team_data['name'] + ')'

    return t1 + '\n\n' + t2 + '\n\n' + t3 + '\n\n' + t4 + '\n' + t5 + '\nUsciti per 5 falli: ' + t6



###########################################################################################################################################################################
# Returns the points chart as a Plotly Figure
###########################################################################################################################################################################
def pointsChart(df, game, height_in_pixels=600, template='plotly_dark'):

    d = datetime.datetime.today()

    def seconds2datetime(seconds):
        return datetime.datetime(d.year, d.month, d.day) + datetime.timedelta(seconds=seconds)
    
    pt   = []
    ptt  = []
    mt   = []
    post = []
    
    git  = []
    po   = []
    pot  = []
    mo   = []
    poso = []
    gio  = []

    tt = 0
    to = 0
    total_seconds = 0
    previous_total_seconds = 0
    num_change = 0
    diff = 0
    maxover  = 0
    punteggioover = ''
    secondsover = 0
    pointsover = 0
    maxunder = 0
    punteggiounder = ''
    secondsunder = 0
    pointsunder = 0
    
    # Vertical rectangles
    vrect_x0   = []
    vrect_x1   = []
    vrect_col  = []
    
    num_seconds_over   = 0.0
    num_seconds_under  = 0.0
    num_seconds_parity = 0.0
    
    for index, row in df[df['event'].isin([0,2,4])].iterrows():
        quarter = row['quarter']
        seconds = row['seconds']

        if quarter <= 4:  total_seconds = 600.0 - seconds
        else:             total_seconds = 300.0 - seconds
        for q in range(1,quarter):
            if q<= 4: total_seconds += 600.0
            else:     total_seconds += 300.0

        # If not at first scoring
        if index > 0:
            vrect_x0.append(previous_total_seconds)
            vrect_x1.append(total_seconds)
            if tt > to:
                vrect_col.append('green')
                num_seconds_over += total_seconds - previous_total_seconds
            elif tt < to:
                vrect_col.append('red')
                num_seconds_under += total_seconds - previous_total_seconds
            else:
                vrect_col.append('yellow')
                num_seconds_parity += total_seconds - previous_total_seconds
            
        if   row['event'] == 0: p = 1
        elif row['event'] == 2: p = 2
        else:                   p = 3
        
        if row['team'] == Config.TEAM:
            tt += p
            pt.append(tt)
            ptt.append(str(p))
            mt.append(round(total_seconds))
            if game.game_data['home']: punteggio = '%d-%d'%(tt,to)
            else:                      punteggio = '%d-%d'%(to,tt)
            git.append([punteggio,row['player'] + ' %dP'%p])
                
            if tt > to: post.append('top left')
            else:       post.append('bottom right')
        else:
            to += p
            po.append(to)
            pot.append(str(p))
            mo.append(round(total_seconds))
            if game.game_data['home']: punteggio = '%d-%d'%(tt,to)
            else:                      punteggio = '%d-%d'%(to,tt)
            gio.append([punteggio,row['player'] + ' %dP'%p])
            if to > tt: poso.append('top left')
            else:       poso.append('bottom right')
            
        newdiff = tt - to
        
        if newdiff > maxover:
            maxover = newdiff
            if game.game_data['home']:
                punteggioover = ' (%d - %d)'%(tt,to)
            else:
                punteggioover = ' (%d - %d)'%(to,tt)
            pointsover  = tt
            secondsover = total_seconds
        if -newdiff > maxunder:
            maxunder = -newdiff
            if game.game_data['home']:
                punteggiounder = ' (%d - %d)'%(tt,to)
            else:
                punteggiounder = ' (%d - %d)'%(to,tt)
            pointsunder  = to
            secondsunder = total_seconds
            
        if newdiff == 0: newdiff = diff
        #print(tt,to, diff,newdiff)
        if diff * newdiff < 0:
            #print(quarter,seconds, diff,newdiff)
            num_change += 1
        diff = newdiff
        
        previous_total_seconds = total_seconds

    # Adding last rectangle
    if int(total_seconds) % 300 > 0:
        quarter = max(df['quarter'])
        total_seconds = 0.0
        for q in range(1,quarter+1):
            if q<= 4: total_seconds += 600.0
            else:     total_seconds += 300.0
        vrect_x0.append(previous_total_seconds)
        vrect_x1.append(total_seconds)
        if tt > to:
            vrect_col.append('green')
            num_seconds_over += total_seconds - previous_total_seconds
        elif tt < to:
            vrect_col.append('red')
            num_seconds_under += total_seconds - previous_total_seconds
        else:
            vrect_col.append('yellow')
            num_seconds_parity += total_seconds - previous_total_seconds

    #print(num_seconds_over + num_seconds_under + num_seconds_parity,num_seconds_over,num_seconds_under,num_seconds_parity)
    
    smaxover = '-'
    if maxover > 0:
        smaxover = '+%d'%maxover + punteggioover
        
    smaxunder = '-'
    if maxunder > 0:
        smaxunder = '-%d'%maxunder + punteggiounder
        
    fig = go.Figure()
    
    mmax = total_seconds/60.0
    ppq = ['<b>'+x+'</b>' for x in game.pointsPerQuarter(showTotals=True)]
    
    line_color = 'rgb(90,90,90)'
    pmax = max(tt,to) + 7
    
    # Vertical line at the start of the game
    x = datetime.datetime(d.year, d.month, d.day, 0, 0, 0)
    fig.add_vline(x=x, line_width=2, line_dash="dash", line_color=line_color)
    
    if mmax >= 10:
        xt = datetime.datetime(d.year, d.month, d.day, 0, 5, 0)
        x  = datetime.datetime(d.year, d.month, d.day, 0, 10, 0)
        fig.add_vline(x=x, line_width=2, line_dash="dash", line_color=line_color)
        if len(ppq) > 0: fig.add_annotation(x=xt, y=pmax, text=ppq[0], showarrow=False)
    
    if mmax >= 20:
        xt = datetime.datetime(d.year, d.month, d.day, 0, 15, 0)
        x  = datetime.datetime(d.year, d.month, d.day, 0, 20, 0)
        fig.add_vline(x=x, line_width=2, line_dash="dash", line_color=line_color)
        if len(ppq) > 1: fig.add_annotation(x=xt, y=pmax, text=ppq[1], showarrow=False)
        
    if mmax >= 30:
        xt = datetime.datetime(d.year, d.month, d.day, 0, 25, 0)
        x  = datetime.datetime(d.year, d.month, d.day, 0, 30, 0)
        fig.add_vline(x=x, line_width=2, line_dash="dash", line_color=line_color)
        if len(ppq) > 2: fig.add_annotation(x=xt, y=pmax, text=ppq[2], showarrow=False)
        
    if mmax >= 40 or game.board.tb.gameover:
        xt = datetime.datetime(d.year, d.month, d.day, 0, 35, 0)
        x  = datetime.datetime(d.year, d.month, d.day, 0, 40, 0)
        fig.add_vline(x=x, line_width=2, line_dash="dash", line_color=line_color)
        if len(ppq) > 3: fig.add_annotation(x=xt, y=pmax, text=ppq[3], showarrow=False)
        
    if mmax >= 45 or game.board.tb.gameover:
        xt = datetime.datetime(d.year, d.month, d.day, 0, 42, 30)
        x  = datetime.datetime(d.year, d.month, d.day, 0, 45, 0)
        fig.add_vline(x=x, line_width=2, line_dash="dash", line_color=line_color)
        if len(ppq) > 4: fig.add_annotation(x=xt, y=pmax, text=ppq[4], showarrow=False)
        
    if mmax >= 50 or game.board.tb.gameover:
        xt = datetime.datetime(d.year, d.month, d.day, 0, 47, 30)
        x  = datetime.datetime(d.year, d.month, d.day, 0, 50, 0)
        fig.add_vline(x=x, line_width=2, line_dash="dash", line_color=line_color)
        if len(ppq) > 5: fig.add_annotation(x=xt, y=pmax, text=ppq[5], showarrow=False)
        
    if mmax >= 55 or game.board.tb.gameover:
        xt = datetime.datetime(d.year, d.month, d.day, 0, 52, 30)
        x  = datetime.datetime(d.year, d.month, d.day, 0, 55, 0)
        fig.add_vline(x=x, line_width=2, line_dash="dash", line_color=line_color)
        if len(ppq) > 6: fig.add_annotation(x=xt, y=pmax, text=ppq[6], showarrow=False)
        
    if mmax >= 60 or game.board.tb.gameover:
        xt = datetime.datetime(d.year, d.month, d.day, 0, 57, 30)
        x  = datetime.datetime(d.year, d.month, d.day, 1,  0, 0)
        fig.add_vline(x=x, line_width=2, line_dash="dash", line_color=line_color)
        if len(ppq) > 7: fig.add_annotation(x=xt, y=pmax, text=ppq[7], showarrow=False)
    
    
    # Vertical colored rects
    for x0,x1,col in zip(vrect_x0,vrect_x1,vrect_col):
        fig.add_vrect(x0=seconds2datetime(x0), x1=seconds2datetime(x1), line_width=0, fillcolor=col, opacity=0.1)
            
    # Lines for team
    fig.add_trace(go.Scatter(x=[seconds2datetime(x) for x in mt], y=pt, text=[str(x) for x in pt], customdata=git, textposition=post, line_shape="hv",
                             hovertemplate='<b>%{customdata[0]}</b> - %{customdata[1]} - %{x|%M\':%S\"}', mode='lines+markers+text', name=game.team_data['name'], line=dict(color='green'), marker=dict(size=15, color='green')))
    
    # Text (1,2,3) for team
    fig.add_trace(go.Scatter(x=[seconds2datetime(x) for x in mt], y=pt, text=ptt, customdata=git, showlegend=False, textposition="middle center", textfont=dict(family="arial",size=11,color="white"),
                             hoverinfo='none', mode='text', name='', marker=dict(size=0, color='white')))
    
    # Lines for opponents
    fig.add_trace(go.Scatter(x=[seconds2datetime(x) for x in mo], y=po, text=[str(x) for x in po], customdata=gio, textposition=poso, line_shape="hv",
                             hovertemplate='<b>%{customdata[0]}</b> - %{customdata[1]} - %{x|%M\':%S\"}', mode='lines+markers+text', name=game.game_data['opponents'], line=dict(color='red'), marker=dict(size=15, color='red')))
    
    # Text (1,2,3) for opponents
    fig.add_trace(go.Scatter(x=[seconds2datetime(x) for x in mo], y=po, text=pot, customdata=gio, showlegend=False, textposition="middle center", textfont=dict(family="arial",size=11,color="white"),
                             hoverinfo='none', mode='text', name='', marker=dict(size=0, color='white')))
    
    pup = ''
    peq = ''
    pdn = ''
    if total_seconds > 0.0:
        pup = '%.1f%%'%(100.0*num_seconds_over/total_seconds)
        peq = '%.1f%%'%(100.0*num_seconds_parity/total_seconds)
        pdn = '%.1f%%'%(100.0*num_seconds_under/total_seconds)
        percentages = 'Percentuale di tempo in vantaggio: %s    in parità: %s    in svantaggio: %s'%(pup,peq,pdn)
    else:
        percentages = ''

    # Add traces for legend
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers', marker=dict(size=20, color='green',  symbol='square', opacity=0.1), legendgroup='Vantaggio',  showlegend=True, name='Vantaggio (%s)'%pup))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers', marker=dict(size=20, color='yellow', symbol='square', opacity=0.1), legendgroup='Parità',     showlegend=True, name='Parità (%s)'%peq))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers', marker=dict(size=20, color='red',    symbol='square', opacity=0.1), legendgroup='Svantaggio', showlegend=True, name='Svantaggio (%s)'%pdn))


    fig.for_each_trace(lambda t: t.update(textfont_color=t.marker.color))

    title = "<span style='font-size:22px; font-weight: 700;'>"
    
    points_team = Stats.points(game.events_df)
    points_oppo = Stats.points(game.events_df, team=Config.OPPO)
    if game.game_data['home']:
        title += game.team_data['short'].upper() + ' - ' + game.game_data['opponents']
        ppp1 = points_team
        ppp2 = points_oppo
    else:
        title += game.game_data['opponents'] + ' - ' + game.team_data['short'].upper()
        ppp1 = points_oppo
        ppp2 = points_team        
        
    title +=  '&nbsp;&nbsp;&nbsp;&nbsp;' + str(ppp1) + ' - ' + str(ppp2) + '</span>'

    # Write the minutes on the xaxis
    dates_array = [datetime.datetime(d.year, d.month, d.day, 0, x, 0) for x in list(range(int(mmax+1.99999999)))]
    
    dmin = dates_array[0] - datetime.timedelta(seconds=30)
    dmax = dates_array[0] + datetime.timedelta(seconds=total_seconds+30)
    
    if secondsover > 0:
        x = int(secondsover)
        dtx = seconds2datetime(x)
        fig.add_annotation(x=dtx, y=pointsover, align='center', yshift=70, xshift=0, text="Massimo<br>vantaggio<br>"+smaxover, showarrow=False)
        fig.add_shape(type="line", x0=dtx, y0=pointsover+4, x1=dtx, y1=pointsover-maxover, line=dict(color="#000000", width=0.5, dash="dot"))
              
    if secondsunder > 0:
        x = int(secondsunder)
        dtx = seconds2datetime(x)
        fig.add_annotation(x=dtx, y=pointsunder, align='center', yshift=70, xshift=0, text="Massimo<br>svantaggio<br>"+smaxunder, showarrow=False)
        fig.add_shape(type="line", x0=dtx, y0=pointsunder+4, x1=dtx, y1=pointsunder-maxunder, line=dict(color="#000000", width=0.5, dash="dot"))
        
        
    # Graphical recap of quarters
    if total_seconds >= 20*60:
        ppq = game.pointsPerQuarter(showTotals=True)
        ds = 76
        x0 = seconds2datetime(60)
        x1 = x0 + datetime.timedelta(seconds=ds*len(ppq))
        y0 = max(tt,to)
        y1 = y0 - 14.5
        y = y0 - 9
        fig.add_shape(type="rect", x0=x0, x1=x1, y0=y0, y1=y1, line=dict(color="#000000", width=0.5), fillcolor="white")
        fig.add_shape(type="line", x0=x0+datetime.timedelta(seconds=ds/16), x1=x1-datetime.timedelta(seconds=ds/16), y0=y, y1=y, line=dict(color="#000000", width=0.5))
        x = x0 + datetime.timedelta(seconds=ds/2)
        diffs = []
        for q in ppq:
            if '(' in q: t = q.split('(')[0]
            else:        t = q
            n1 = int(t.split(': ')[1].split(' - ')[0])
            n2 = int(t.split(': ')[1].split(' - ')[1])
            if game.game_data['home']: d = n1 - n2
            else:                      d = n2 - n1
            diffs.append(d)
            
            fig.add_annotation(x=x, y=y0-2, text=t.replace(': ','<br>').replace(' ',''), showarrow=False, font=dict(size=10))
            
            x += datetime.timedelta(seconds=ds)
            
        diffmax = max([abs(x) for x in diffs])
        x = x0 + datetime.timedelta(seconds=ds/2)
        w = datetime.timedelta(seconds=ds*0.8)
        for d in diffs:            
            if d > 0:
                fillcolor = 'green'
                t = '+' + str(d)
            else:
                fillcolor = 'red'
                t = str(d)
            
            fig.add_shape(type="rect", x0=x-w/2, x1=x+w/2, y0=y, y1=y+d*5/diffmax, line=dict(color="#000000", width=0), fillcolor=fillcolor)
            if d != 0:
                if abs(d) > 0.25*diffmax:
                    fig.add_annotation(x=x, y=y+d*2/diffmax, text=t, showarrow=False, font=dict(size=11,color="#ffffff"))
                else:
                    fig.add_annotation(x=x, y=y+d*4/diffmax+(1.1*d/abs(d)), text=t, showarrow=False, font=dict(size=11,color="#000000"))
            x += datetime.timedelta(seconds=ds)
            

    r2 = '%d cambi in testa&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Massimo vantaggio: %s&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Massimo svantaggio: %s'%(num_change,smaxover,smaxunder)
    fig.update_layout(title=dict(text=title+'<br><span style="font-size: 15px;">%s</span><br><span style="font-size: 15px;">%s</span>'%(r2,percentages),
                                 y=0.972,x=0.02,xanchor='left',yanchor='top'),
                      #hovermode='x unified',
                      template=template,
                      height=height_in_pixels,
                      font_family="Arial",
                      font_size=13,
                      title_font_family="Arial",
                      xaxis_title='Minuti',
                      yaxis_title='Punti',
                      xaxis=dict(range=[dmin,dmax], tickmode='array', tickvals=dates_array, ticktext=['%d\''%x.minute for x in dates_array]),
                      yaxis=dict(range=[0,pmax+2]),
                      margin=dict(l=26,r=10,b=30,t=86,pad=0),
                      legend=dict(orientation="v", yanchor="top", y=0.28, xanchor="left", x=0.755, bordercolor="#000000", borderwidth=0.5))

    return fig


###########################################################################################################################################################################
# Returns the play by play description of the game. Returns a string formatted in HTML
###########################################################################################################################################################################
def play_by_play(df, game):
    home = game.game_data['home']

    quarters   = sorted(df['quarter'].unique())
    qstartsecs = [600.0 if x<=4 else 300.0 for x in quarters]
    starters   = [list(df[(df['team']==Config.TEAM)&(df['quarter']==q)&(df['event_name']=='Entr')&(df['seconds']==s)]['player'])[-5:] for q,s in zip(quarters,qstartsecs)]

    res = []

    last_quarter = 0
    points_team = 0
    points_oppo = 0

    maxplus_team = 0
    maxplus_oppo = 0

    maxtime_team = ''
    maxtime_oppo = ''

    maxpts_team = ''
    maxpts_oppo = ''

    events_for_player = {}
    events_for_opponents = {}

    for index, row in df.iterrows():
        quarter = row['quarter']
        qindex = quarter - 1
        seconds = row['seconds']
        fromstart = qstartsecs[qindex] - seconds

        if quarter <= 4:
            qstr = '%d.o quarto'%quarter
        else:
            qstr = '%d.o suppl.'%(quarter-4)

        time = '%02d\':%02d\"'%(fromstart//60, fromstart%60)

        event_id    = row['event']
        event_name  = row['event_name']
        player_name = row['player']
        team        = row['team']

        if not ((event_name=='Entr' and seconds==qstartsecs[qindex]) or (event_name=='Usci' and seconds==qstartsecs[qindex]) or (event_name=='Usci' and seconds==0.0)):
            if quarter > last_quarter:
                last_quarter = quarter
                res.append({'quarter': '',       # Empty line
                            'time':    '',
                            'text':    '',
                            'color':   '',
                            'weight': 700,
                            'points':  '',
                            'pcolor':  ''
                           })
                res.append({'quarter': qstr,     # First line for the quarter
                            'time':    '00\':00"',
                            'text':    'Inizio ' + qstr,
                            'color':   'black',
                            'weight': 700,
                            'points':  '',
                            'pcolor':  ''
                           })
                res.append({'quarter': qstr,     # Starters players for the quarter
                            'time':    '00\':00"',
                            'text':    'Quintetto: ' + ', '.join(starters[qindex]),
                            'color':   'black',
                            'weight': 700,
                            'points':  '',
                            'pcolor':  ''
                           })

            added = ''

            if team == Config.TEAM:
                if not player_name in events_for_player:
                    events_for_player[player_name] = {}

                ev = events_for_player[player_name]
                if not event_id in ev:
                    ev[event_id] = 0

                ev[event_id] = ev[event_id] + 1

                if event_id in [0,2,4]:
                    points_team += Config.EVENT_VALUE[event_id]
                    if (points_team - points_oppo) > maxplus_team:
                        maxplus_team = points_team - points_oppo
                        maxtime_team = qstr + ' ' + time
                        if home: maxpts_team = '%d - %-d'%(points_team,points_oppo)
                        else:    maxpts_team = '%d - %-d'%(points_oppo,points_team)
                    ok = ev[event_id]
                    if event_id+1 in ev: err = ev[event_id+1]
                    else:                err = 0

                    points_player = 0
                    if 0 in ev: points_player += ev[0] 
                    if 2 in ev: points_player += 2*ev[2]
                    if 4 in ev: points_player += 3*ev[4]
                    added = ' (%d/%d&nbsp;&nbsp;%.0f%%&nbsp;&nbsp;P. %d)'%(ok, ok+err, 100*ok/(ok+err), points_player)

                    weight = 700
                    color = '#008800'
                elif event_id in [1,3,5]:
                    err = ev[event_id]
                    if event_id-1 in ev: ok = ev[event_id-1]
                    else:                ok = 0

                    points_player = 0
                    if 0 in ev: points_player += ev[0] 
                    if 2 in ev: points_player += 2*ev[2]
                    if 4 in ev: points_player += 3*ev[4]
                    added = ' (%d/%d&nbsp;&nbsp;%.0f%%&nbsp;&nbsp;P. %d)'%(ok, ok+err, 100*ok/(ok+err), points_player)

                    weight = 700
                    color = '#aa0000'
                else:
                    if event_id not in [18, 19, 20]:
                        added = ' (%d)'%ev[event_id]

                    weight = 400
                    color = 'black'
            else:
                if not player_name in events_for_opponents:
                    events_for_opponents[player_name] = {}

                ev = events_for_opponents[player_name]
                if not event_id in ev:
                    ev[event_id] = 0

                ev[event_id] = ev[event_id] + 1

                if event_id in [0,2,4]:
                    points_oppo += Config.EVENT_VALUE[event_id]
                    if (points_oppo - points_team) > maxplus_oppo:
                        maxplus_oppo = points_oppo - points_team
                        maxtime_oppo = qstr + ' ' + time
                        if home: maxpts_oppo = '%d - %-d'%(points_team,points_oppo)
                        else:    maxpts_oppo = '%d - %-d'%(points_oppo,points_team)

                    poppo = 0
                    if 0 in ev: poppo += ev[0] 
                    if 2 in ev: poppo += 2*ev[2]
                    if 4 in ev: poppo += 3*ev[4]
                    added = ' (P. %d)'%poppo
                else:
                    added = ' (%d)'%ev[event_id]

                weight = 700
                color = '#0000aa'
                if player_name == 'Opponents':
                    player_name = 'Avversari'
                else:
                    player_name = 'Avversari (%s)'%player_name

            if points_team > points_oppo:
                pcolor = '#008800'
            elif points_team == points_oppo:
                pcolor = '#888800'
            else:
                pcolor = '#aa0000'

            if home:
                points = '%d - %-d'%(points_team,points_oppo)
            else:
                points = '%d - %-d'%(points_oppo,points_team)

            res.append({'quarter': qstr,
                        'time':    time,
                        'text':    player_name + ': ' + Config.EVENT_DESCRIPTION[event_id] + added,
                        'color':   color,
                        'weight':  weight,
                        'points':  points,
                        'pcolor':  pcolor
                       })

    # Empty line at the end
    res.append({'quarter': '',
                'time':    '',
                'text':    '',
                'color':   '',
                'weight': 700,
                'points':  '',
                'pcolor':  ''
               })

        
    def formatEvent(item):
        return '''
        <tr>
            <td class="quarto">%s</td>
            <td class="minuto">%s</td>
            <td class="evento" style="color: %s; font-weight: %d;">%s</td>
            <td class="punteggio" style="color: %s;">%s</td>
        </tr>'''%(item['quarter'], item['time'], item['color'], item['weight'], item['text'], item['pcolor'], item['points'])

    body = [formatEvent(x) for x in res]

    if game.game_data['home']:
        title = game.team_data['name'] + ' - ' + game.game_data['opponents'] + '&nbsp;&nbsp;&nbsp;' + str(points_team) + ' - ' + str(points_oppo)
    else:
        title = game.game_data['opponents'] + ' - ' + game.team_data['name']

    if maxplus_team > 0:
        maxplusminus1 = 'Massimo vantaggio:&nbsp;&nbsp;   +%d punti sul punteggio di %s (%s)'%(maxplus_team, maxpts_team, maxtime_team)
    else:
        maxplusminus1 = ''
        
    if maxplus_oppo > 0:
        maxplusminus2 = 'Massimo svantaggio:\t  -%d punti sul punteggio di %s (%s)'%(maxplus_oppo, maxpts_oppo, maxtime_oppo)
    else:
        maxplusminus2 = ''

    html = '''
<head>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,300..800;1,300..800&family=Roboto+Condensed:ital,wght@0,100..900;1,100..900&family=Roboto:ital,wght@0,100..900;1,100..900&display=swap" rel="stylesheet">    
</head>
<style>
.title {
    text-align: left;
    font-size: 25px !important;
    font-weight: 700 !important;
    line-height: 110%% !important;
    font-family: Roboto;
    color: black;
}

.maxplusminus {
    text-align: left;
    font-size: 16px;
    font-weight: 400;
    line-height: 85%%;
    font-family: Roboto;
}

.quarto {
    font-size: 18px;
    font-weight: 300;
    width: 15%%;
    line-height: 90%%;
    font-family: Roboto;
}

.minuto {
    font-size: 20px;
    font-weight: 300;
    width: 10%%;
    line-height: 90%%;
    font-family: Roboto;
}

.evento {
    font-size: 20px;
    font-weight: 600;
    width: 70%%;
    line-height: 90%%;
    font-family: Roboto;
}

.punteggio {
    font-size: 20px;
    font-weight: 700;
    width: 10%%;
    line-height: 90%%;
    font-family: Roboto;
}

.table_component {
    overflow: auto;
    width: 100%%;
    padding: 10px 0px 0px 10px;    
}

.table_component table {
    border: 0px solid #dededf;
    height: 100%%;
    width: 100%%;
    table-layout: fixed;
    border-collapse: collapse;
    border-spacing: 1px;
    text-align: left;
}

.table_component th {
    border: 0px solid #dededf;
    background-color: #ffffff;
    color: #000000;
    padding: 5px;
    font-family: Roboto;
}

.table_component td {
    border: 0px solid #dededf;
    background-color: #ffffff;
    color: #000000;
    padding: 5px;
    font-family: Roboto;
}
</style>
<div class="table_component" role="region" tabindex="0">
<p class="title">%s</p>
<p class="maxplusminus">%s</p>
<p class="maxplusminus">%s</p>
<p class="maxplusminus">  </p>
<table>
    <thead>
        <tr>
            <th class="quarto" style="font-size: 20px; font-weight: 700; color: #880000;">Quarto</th>
            <th class="minuto" style="font-weight: 700; color: #880000;">Minuto</th>
            <th class="evento" style="font-weight: 700; color: #880000;">Evento</th>
            <th class="punteggio" style="font-weight: 700; color: #880000;">Punteggio</th>
        </tr>
    </thead>
    <tbody>
%s
    </tbody>
</table>
</div>
'''%(title, maxplusminus1, maxplusminus2, '\n'.join(body))

    return html
