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
XPUNTI     =  4.68
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
def svg(df, game, team_logo_img=None, width=80):   # Dimensioning in vw/vh
    
    height = 2.005*FORM_FACTOR*width    # 2 means that 1vw = 2vh in general screens
    
    svgwidth  = IMAGE_WIDTH_IN_PIXELS  / 100.0    # 21.30
    svgheight = IMAGE_HEIGHT_IN_PIXELS / 100.0    # 10.90
    
    preserve = 'xMidYMid meet'    # Center the chart in the parent
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
    def text(x, y, s, dim=0.28, w=500, align='start', color='black'):
        return '<text x="%f" y="%f" fill="%s" stroke="none" font-size="%f" font-weight="%d" font-family="%s" text-anchor="%s" alignment-baseline="hanging">%s</text>' % (x, y, color, dim, w, font_name, align, s)
        
        
    # Top texts
    if game is not None:
        g = game.game_data
        #svg += '<line x1="2" y1="%f" x2="20" y2="%f" stroke="black" stroke-width="0.001"/>' % (YLUOGO, YLUOGO)

        hRigaTestata = 0.30
        dimSquadre   = 0.52
        dimParziali  = 0.25
        
        d = datetime.datetime.strptime(g['date'], "%d/%m/%Y")
        day = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica'][d.weekday()]
        svg += text(XSQUADRE, YLUOGO,                day + ' ' + g['date'] + ' Ore ' + g['time']);
        svg += text(X3P,      YLUOGO,                g['location']);
        svg += text(XSQUADRE, YLUOGO + hRigaTestata, 'Arbitri: ' + g['referee1'] + ',  ' + g['referee2']);
        
        svg += text(XRIGHT, YLUOGO,                g['season'], align='end');
        svg += text(XRIGHT, YLUOGO+1*hRigaTestata, g['championship'], align='end');
        svg += text(XRIGHT, YLUOGO+2*hRigaTestata, 'Girone ' + g['phase'], align='end');
        svg += text(XRIGHT, YLUOGO+3*hRigaTestata, str(g['round']) + '.a Giornata', align='end');
        
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
            dfq = df[df['quarter']==q]
            pqt = Stats.points(dfq)
            pqo = Stats.points(dfq, team=Config.OPPO)
            ptt += pqt
            pto += pqo
            
            svg += text(x, YSQUADRA1, name, dim=dimParziali, align='middle')
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
                    svg += text(x, YSQUADRA2+2*hParziali, str(pqt), dim=dimParziali, align='middle')
                else:
                    svg += text(x, YSQUADRA1+hParziali,   '%d (%d)'%(pqo,pto), dim=dimParziali, align='middle')
                    svg += text(x, YSQUADRA1+2*hParziali, '%d (%d)'%(pqt,ptt), dim=dimParziali, align='middle')
                    
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
    ysum = y1+13*hRiga-0.03
    
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
        pos = game.players_by_number.index(player_name)
        y = y1 + pos*hRiga
        svg += text(XSTARTERS, y, 'Q', align='middle', color='white')
        
    # Minuti in campo
    y = y1
    total_seconds = 0.0
    for player_name in game.players_by_number:
        seconds = game.players_info[player_name]['time_on_field']
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
            svg += text(XPUNTI, y, str(points), align='middle')
        y += hRiga
    t = Stats.points(df)
    if t > 0: svg += text(XPUNTI, ysum, str(t), align='middle', color='white')
        
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
    for player_name in game.players_by_number:
        if game.players_info[player_name]['time_on_field'] > 0:
            svg += text(XVAL, y, str(Stats.value(df, player_name)), align='middle')
        y += hRiga
    t = Stats.value(df)
    if t > 0: svg += text(XVAL, ysum, str(t), align='middle', color='white')
        
    # Valutazione OER
    y = y1
    for player_name in game.players_by_number:
        if game.players_info[player_name]['time_on_field'] > 0:
            svg += text(XOER, y, '%.2f'%Stats.oer(df, player_name), align='middle')
        y += hRiga
    t = Stats.oer(df)
    if t > 0: svg += text(XOER, ysum, '%.2f'%t, align='middle', color='white')
        
    # Valutazione VIR
    y = y1
    for player_name in game.players_by_number:
        if game.players_info[player_name]['time_on_field'] > 0:
            svg += text(XVIR, y, '%.2f'%Stats.vir(df, player_name, game.players_info), align='middle')
        y += hRiga
    t = Stats.vir(df, players_info=game.players_info)
    if t > 0: svg += text(XVIR, ysum, '%.2f'%t, align='middle', color='white')

    # Valutazione PlusMinus
    y = y1
    for player_name in game.players_by_number:
        if game.players_info[player_name]['time_on_field'] > 0:
            svg += text(XPLUSMIN, y, str(Stats.plusminus(player_name, game.players_info)), align='middle')
        y += hRiga
    t = Stats.plusminus(players_info=game.players_info)
    if t > 0: svg += text(XPLUSMIN, ysum, str(t), align='middle', color='white')
        
    # Valutazione TrueShooting
    y = y1
    for player_name in game.players_by_number:
        if game.players_info[player_name]['time_on_field'] > 0:
            svg += text(XTRUE, y, '%.1f'%Stats.trueshooting(df, player_name), align='middle')
        y += hRiga
    t = Stats.trueshooting(df)
    if t > 0: svg += text(XTRUE, ysum, '%.1f'%t, align='middle', color='white')
        
    
    # Bottom texts
    y1 = YRIGA0
    hRiga = 0.36
    hRigaNote = 3*hRiga/5
    yNote = y1 + 16*hRiga
    y2 = yNote + 0.3*hRigaNote
    
    svg += text(XLEFT,  y2-0.06, 'Allenatore: ' + game.team_data['trainer'])
    svg += text(XPUNTI, y2-0.06, 'Assistente: ' + game.team_data['assistant'])
    
    dimNote = 0.14
    svg += text(XRIGHT, y2-0.06, 'Rilevazioni statistiche realizzate con Basket Score', dim=dimNote, align='end')
    
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
        if game.players_info[player_name]['time_on_field'] <= 0.0: pt.append('%s ne'%player_name)
        else:                                                      pt.append('%s %d'%(player_name, Stats.points(df, player_name)))
        
    for player_name in game.opponents_by_number:
        points = Stats.points(df, player_name, team=Config.OPPO)
        if points > 0: po.append('%s %d'%(player_name,points))
        else:          po.append(player_name)
    
    if g['home']:
        svg += text(XLEFT, yNote + 8.1*hRigaNote,     game.team_data['name'].upper() + ': ', dim=dimSintesi)
        svg += text(XLEFT, yNote + 9.6*hRigaNote,   g['opponents'].upper() + ': ',         dim=dimSintesi)
        svg += text(XMINUTI-0.1, yNote + 8.1*hRigaNote,   ', '.join(pt), dim=dimSintesi)
        svg += text(XMINUTI-0.1, yNote + 9.6*hRigaNote, ', '.join(po), dim=dimSintesi)
    else:
        svg += text(XLEFT, yNote + 8.1*hRigaNote,     g['opponents'].upper() + ': ',         dim=dimSintesi)
        svg += text(XLEFT, yNote + 9.6*hRigaNote,   game.team_data['name'].upper() + ': ', dim=dimSintesi)
        svg += text(XMINUTI-0.1, yNote + 8.1*hRigaNote,   ', '.join(po), dim=dimSintesi)
        svg += text(XMINUTI-0.1, yNote + 9.6*hRigaNote, ', '.join(pt), dim=dimSintesi)
    
    svg += '</svg>'
    return svg


###########################################################################################################################################################################
# Returns the BoxScore in html format (full screen) as a string
###########################################################################################################################################################################
def html(df, game, team_logo_img=None):
    return '<html><body><div style="text-align:center;">%s</div></body></html>'%svg(df, game=game, team_logo_img=team_logo_img, width=90.0)


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
def pointsChart(df, game, height_in_pixels=450):
    pt  = [0]
    mt  = [0]
    post= ['top center']
    
    git = ['']
    po  = [0]
    mo  = [0]
    poso= ['bottom center']
    gio = ['']

    tt = 0
    to = 0
    for index, row in df[df['event'].isin([0,2,4])].iterrows():
        quarter = row['quarter']
        seconds = row['seconds']

        if quarter <= 4:  total_seconds = 600.0 - seconds
        else:             total_seconds = 300.0 - seconds
        for q in range(1,quarter):
            if q<= 4: total_seconds += 600.0
            else:     total_seconds += 300.0

        if   row['event'] == 0: p = 1
        elif row['event'] == 2: p = 2
        else:                   p = 3
        if  row['team'] == Config.TEAM:
            tt += p
            pt.append(tt)
            mt.append(round(total_seconds))
            git.append(row['player'] + ' %dP'%p)
            if tt > to:
                if p == 1:
                    post.append('middle right')
                else:
                    post.append('top center')
            else:
                if p == 1:
                    post.append('middle right')
                else:
                    post.append('bottom center')
        else:
            to += p
            po.append(to)
            mo.append(round(total_seconds))
            gio.append(row['player'] + ' %dP'%p)
            if to > tt:
                if p == 1:
                    poso.append('middle left')
                else:
                    poso.append('top center')
            else:
                if p == 1:
                    poso.append('middle left')
                else:
                    poso.append('bottom center')

    pointsTeam = Stats.points(df)
    pointsOppo = Stats.points(df, team=Config.OPPO)
    
    d = datetime.datetime.today()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[datetime.datetime(d.year, d.month, d.day, 0, x//60, x%60) for x in mt], y=pt, text=[str(x) for x in pt], customdata=git, textposition=post,    
                             hovertemplate='%{y} - %{customdata} - %{x|%M\':%S\"}', mode='lines+markers+text', name=game.team_data['name'], line=dict(color='green'), marker=dict(color='green')))
    fig.add_trace(go.Scatter(x=[datetime.datetime(d.year, d.month, d.day, 0, x//60, x%60) for x in mo], y=po, text=[str(x) for x in po], customdata=gio, textposition=poso,
                             hovertemplate='%{y} - %{customdata} - %{x|%M\':%S\"}', mode='lines+markers+text', name=game.game_data['opponents'], line=dict(color='red'), marker=dict(color='red')))
    
    fig.for_each_trace(lambda t: t.update(textfont_color=t.marker.color))

    if game.game_data['home']:
        title = game.team_data['name'] + ' - ' + game.game_data['opponents']
    else:
        title = game.game_data['opponents'] + ' - ' + game.team_data['name']

    # Write the minutes on the xaxis
    mmax = max(max(mt),max(mo)) / 60.0
    dates_array = [datetime.datetime(d.year, d.month, d.day, 0, x, 0) for x in list(range(int(mmax+1.99999999)))]
    
    dmin = dates_array[0]  - datetime.timedelta(seconds=6)
    dmax = dates_array[-1] + datetime.timedelta(seconds=6)
    
    fig.update_layout(title=dict(text=title,y=0.97,x=0.02,xanchor='left',yanchor='top'),
                      template='plotly_dark',
                      height=height_in_pixels,
                      font_family="Arial",
                      font_size=12,
                      title_font_family="Arial",
                      xaxis_title='Minuti',
                      yaxis_title='Punti',
                      xaxis = dict(range=[dmin,dmax], tickmode='array', tickvals=dates_array, ticktext=['%d\''%x.minute for x in dates_array]),
                      margin=dict(l=20,r=10,b=30,t=30,pad=0))

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

        if not (event_name=='Entr' or seconds==qstartsecs[qindex]):
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
                            'time':    time,
                            'text':    'Inizio ' + qstr,
                            'color':   'black',
                            'weight': 700,
                            'points':  '',
                            'pcolor':  ''
                           })
                res.append({'quarter': qstr,     # Starters players for the quarter
                            'time':    time,
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
        title = game.team_data['name'] + ' - ' + game.game_data['opponents'] + '&nbsp;&nbsp;&nbsp;' + str(points_team) + ' : ' + str(points_oppo)
    else:
        title = game.game_data['opponents'] + ' - ' + game.team_data['name']

    maxplusminus1 = 'Massimo vantaggio:&nbsp;&nbsp;   +%d punti sul punteggio di %s (%s)'%(maxplus_team, maxpts_team, maxtime_team)
    maxplusminus2 = 'Massimo svantaggio:\t  -%d punti sul punteggio di %s (%s)'%(maxplus_oppo, maxpts_oppo, maxtime_oppo)

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
