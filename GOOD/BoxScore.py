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
#font_name = 'Roboto'
#font_url  = 'https://fonts.googleapis.com/css?family=%s:400,100,100italic,300,300italic,400italic,500,500italic,700,700italic,900,900italic' % (font_name)

font_name = 'Open Sans'
font_url  = 'https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,300..800;1,300..800&family=Roboto+Condensed:ital,wght@0,100..900;1,100..900&display=swap'


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
XQUINTETTO =  4.00

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
def svg(df, game=None, team_logo_img=None, width=80):   # Dimensioning in vw/vh
    
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
    svg += '<rect x="0" y="0" width="%f" height="%f" %s %s></rect>' % (svgwidth,svgheight, white, xsmall)
    
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
        svg += text(XSQUADRE, YLUOGO,                day + ' ' + g['date'] + ' Ore ' + g['time'] + '&nbsp;&nbsp;&nbsp;&nbsp;' + g['location']);
        svg += text(XSQUADRE, YLUOGO + hRigaTestata, 'Arbitri: ' + g['referee1'] + ',  ' + g['referee2']);
        
        svg += text(XRIGHT, YLUOGO,                g['season'], align='end');
        svg += text(XRIGHT, YLUOGO+1*hRigaTestata, g['championship'], align='end');
        svg += text(XRIGHT, YLUOGO+2*hRigaTestata, 'Girone ' + g['phase'], align='end');
        svg += text(XRIGHT, YLUOGO+3*hRigaTestata, g['round'] + ' Giornata', align='end');
        
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
    
    svg += text(XLEFT, y2-0.06, 'Allenatore: ' + game.team_data['trainer'] + '&nbsp;&nbsp;&nbsp;Assistente: ' + game.team_data['assistant'])
    
    dimNote = 0.14
    svg += text(XRIGHT, y2-0.06, 'Rilevazioni statistiche realizzate con Basket Score', dim=dimNote, align='end')
    
    svg += text(XLEFT, yNote + 1.75*hRigaNote, 'Note sulle valutazioni:', dim=dimNote)
    svg += text(XLEFT, yNote + 2.75*hRigaNote, 'Valutazione di Lega = (TL+) - (TL-) + [(T2+) x 2 - (T2-)] + [(T3+) x 3) - (T3-)] + PR - PP + RO + RD + AS - FF + FS + SD - SS', dim=dimNote)
    svg += text(XLEFT, yNote + 3.75*hRigaNote, 'Valutazione OER = Coefficiente di Efficacia Offensiva =  Punti realizzati / Possessi      dove Possessi = T2 + T3 + (TL/2) + PP', dim=dimNote)
    svg += text(XLEFT, yNote + 4.75*hRigaNote, 'Valutazione VIR = Value Index Rating = [(Punti fatti + AS x 1,5 + PR + SD x 0,75 + RO x 1,25 + RD x 0,75 + T3+/2 + FS/2 - FF/2 - ((T3-) + (T2-)) x 0,75 - PP - (TL-)/2) / Minuti giocati]', dim=dimNote)
    svg += text(XLEFT, yNote + 5.75*hRigaNote, 'Valutazione +/- = + Punti segnati dalla squadra - Punti segnati dagli avversari quando il giocatore è in campo', dim=dimNote)
    svg += text(XLEFT, yNote + 6.75*hRigaNote, 'Valutazione TS% = Punti / 2*(NumeroTiriCampo + 0.44*NumeroTiriLiberi) - True Shooting Percentage', dim=dimNote)
    
    
    # Sintesi dei punti
    dimSintesi = 0.22
    
    pt = []
    po = []
    for player_name in game.players_by_number:
        if game.players_info[player_name]['time_on_field'] <= 0.0: pt.append('%s n.e.'%player_name)
        else:                                                      pt.append('%s %d'%(player_name, Stats.points(df, player_name)))
        
    for player_name in game.opponents_by_number:
        points = Stats.points(df, player_name, team=Config.OPPO)
        if points > 0: po.append('%s %d'%(player_name,points))
        else:          po.append(player_name)
    
    if g['home']:
        svg += text(XLEFT, yNote + 8*hRigaNote,     game.team_data['name'].upper() + ': ', dim=dimSintesi)
        svg += text(XLEFT, yNote + 9.4*hRigaNote,   g['opponents'].upper() + ': ',         dim=dimSintesi)
        svg += text(XMINUTI-0.1, yNote + 8*hRigaNote,   ', '.join(pt), dim=dimSintesi)
        svg += text(XMINUTI-0.1, yNote + 9.4*hRigaNote, ', '.join(po), dim=dimSintesi)
    else:
        svg += text(XLEFT, yNote + 8*hRigaNote,     g['opponents'].upper() + ': ',         dim=dimSintesi)
        svg += text(XLEFT, yNote + 9.4*hRigaNote,   game.team_data['name'].upper() + ': ', dim=dimSintesi)
        svg += text(XMINUTI-0.1, yNote + 8*hRigaNote,   ', '.join(po), dim=dimSintesi)
        svg += text(XMINUTI-0.1, yNote + 9.4*hRigaNote, ', '.join(pt), dim=dimSintesi)
    
    svg += '</svg>'
    return svg

