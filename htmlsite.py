"""
Update the final site in HTML format
"""
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
import Config
import Stats
import Game
import ScoreBoard
import BoxScore
import ThrowMap

import importlib
importlib.reload(Config)
importlib.reload(Stats)
importlib.reload(Game)
importlib.reload(ScoreBoard)
importlib.reload(BoxScore)
importlib.reload(ThrowMap)

from ipywidgets import widgets, HTML

import pandas as pd
import glob
import os
from datetime import datetime
from PIL import Image


###########################################################################################################################################################################
# Update the HTML site
###########################################################################################################################################################################
def update(output, messages, ftp_server, dotest=False, test_file=None):
    
    with messages:
        print('Updating pybasket HTML site:')
        
    # Store a file to the FTP server
    def store(filepath):
        file = open(filepath,'rb')
        serverfilepath = filepath.replace('web/','daigio.it/pybasket/')
        ftp_server.storbinary('STOR %s'%serverfilepath, file)
        file.close()

    if dotest and os.path.isfile(test_file):
        allfiles = [test_file]
    else:
        allfiles = glob.glob('./data/*.game')

    phases = sorted(list(set([os.path.basename(x).split('-')[1] for x in allfiles if '-' in x and '.a-' in x])))

    allevents = []
    sb = ScoreBoard.ScoreBoard('./data/Urbania.team', scale=0.4, output=output)

    # Conversion to int without errors
    def toint(x):
        try:
            return int(x)
        except:
            return 999999

    players_info = {}

    html_head = '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <meta name="Robots" content="index,follow" />
        <meta name="author" content="Davide De Marchi" />
        <meta name="description" content="pyBasket" />
        <meta name="keywords" content="key, words" />
        <link rel="stylesheet" type="text/css" href="css/layout.css" media="screen" />
        <link rel="icon" href="images/basket.ico" />
        <title>Statistiche %s - %s - pyBasket</title>
        <style>
            body {font-family: Arial;}

            /* Style the horizontal tab */
            .tab {
              overflow: hidden;
              width: calc(90%% - 300px);
            }

            /* Style the buttons inside the tab */
            .tab button {
              background-color: inherit;
              float: left;
              border: none;
              outline: none;
              cursor: pointer;
              margin-top: 12px; 
              padding: 22px 12px;
              transition: 0.3s;
              font-size: 26px;
              text-align: center;
            }

            /* Change background color of buttons on hover */
            .tab button:hover {
              background-color: #ddd;
            }

            /* Create an active/current tablink class */
            .tab button.active {
              color: white;
              background-color: #b82020;
            }

            /* Style the tab content */
            .tabcontent {
              display: none;
              padding: 6px 12px;
            }

            #left {
                width: 270px;
                float: left;
            }
            #right {
                width: calc(90%% - 300px);
                float: left;
            }
            td:hover {
                cursor:pointer;
            }

            /* Style the vertical tab */
            .vtab {
                float: left;
                width: 100px;
            }

            /* Style the buttons inside the tab */
            .vtab button {
                display: block;
                background-color: inherit;
                color: black;
                padding: 22px 16px;
                width: 100%%;
                border: none;
                outline: none;
                cursor: pointer;
                transition: 0.3s;
                font-size: 18px;
                text-align: center;
            }

            /* Change background color of buttons on hover */
            .vtab button:hover {
                background-color: #ddd;
            }

            /* Create an active/current "tab button" class */
            .vtab button.active {
                color: white;
                background-color: #b82020;
            }

            /* Style the tab content */
            .vtabcontent {
                float: left;
                padding: 0px 12px;
                width: calc(100%% - 130px);
                border-left: none;
            }

            %s
            </style>
    </head>
    <body>
        <div id="content">
            <p id="top">Tabellini statistici e mappe di tiro di tutti i giocatori</p>
            <div id="logo">
                <h1><a href="index.html">%s</a></h1>
            </div>
            <div class="line"></div>
            <div id="pitch">
                <div id="left">
                    <h5>
                    Data di affiliazione: 1/7/1977<br />
                    Sede: Piazza Nicolò Pellipario - Urbania (PU)<br />
                    Telefono: +39 339 172 1198<br />
                    Mail: <a href="mailto:uspurbania@libero.it">uspurbania@libero.it</a><br />
                    Colori sociali: Bianco e Rosso<br />
                    </h5>
                </div>

                <div id="right">
                    <h2 id="curgame" style="width: 100%%; height: 50px; margin-top: 6px; line-height: 1.0; font-size: max(25px, min(32px, 1.5vw));">%s</h2>

                    <div class="tab" style="width: 100%%;">
                        <button style="width: min(150px, 32%%); margin-top: 0px;" class="tablinks" onclick="openContent(event, 'Partite', 'tabcontent', 'tablinks', '%s')" id="defaultOpen">Partite</button>
                        <button style="width: min(150px, 32%%); margin-top: 0px;" class="tablinks" onclick="openContent(event, 'Totali',  'tabcontent', 'tablinks', '%s')">Totali</button>
                        <button style="width: min(150px, 32%%); margin-top: 0px;" class="tablinks" onclick="openContent(event, 'Medie',   'tabcontent', 'tablinks', '%s')">Medie</button>
                    </div>
                </div>
            </div>

            <div id="Totali" class="tabcontent">
                <embed src="sheets/totali.svg"  width="100%%" height="900px"/>
            </div>

            <div id="Medie" class="tabcontent">
                <embed src="sheets/medie.svg"  width="100%%" height="900px"/>
            </div>
    '''



    html_vtabcontent = '''
            .vtabcontent%d   { float: left; padding: 0px 12px; width: calc(100%% - 130px); border-left: none; }
            .vtabcontsheet%d { float: left; padding: 0px 12px; width: calc(100%% - 130px); border-left: none; }
            .vtabcontmap%d   { float: left; padding: 0px 12px; width: calc(100%% - 180px); border-left: none; }'''

    html_function = '''
            document.getElementById("vdefaultOpen%d").click();
            document.getElementById("vdefaultOpenSheet%d").click();
            document.getElementById("vdefaultOpenMap%d").click();'''


    html_sheet_quarterA = '''                    <button class="vtabsheet%d" style="height: 90px;" onclick="openContent(event, '%s', 'vtabcontsheet%d', 'vtabsheet%d', '%s')">%s</button>'''
    html_sheet_quarterB = '''
                  <div id="%s" class="vtabcontsheet%d">
                    <embed src="sheets/%d_%d.svg"  width="100%%" height="900px"/>  
                  </div>'''

    html_sheet = '''
                  <div class="vtab">
                    <button class="vtabsheet%d" style="height: 90px; font-weight: 700;" onclick="openContent(event, 'Totale%d', 'vtabcontsheet%d', 'vtabsheet%d', '%s')" id="vdefaultOpenSheet%d">Totale</button>
%s
                  </div>

                  <div id="Totale%d" class="vtabcontsheet%d">
                    <embed src="sheets/%d.svg"  width="100%%" height="900px"/>  
                  </div>
%s
    '''


    html_mappe_playerA = '''                    <button class="vtabmap%d" style="width: 150px; height: 44px; padding: 4px 8px;" onclick="openContent(event, '%s', 'vtabcontmap%d', 'vtabmap%d', '%s')">%s</button>'''
    html_mappe_playerB = '''
                  <div id="%s" class="vtabcontmap%d">
                    <img src="maps/%d_%s.png" height="700px" style="margin-left: 10px; vertical-align: top;">
                    <img src="players/%s.png" height="700px" style="margin-left: 10px; vertical-align: top;">
                  </div>'''

    html_mappe = '''
                  <div class="vtab" style="width: 150px;">
                    <button class="vtabmap%d" style="width: 150px; height: 44px; padding: 4px 8px; font-weight: 700;" onclick="openContent(event, 'Squadra%d', 'vtabcontmap%d', 'vtabmap%d', '%s')" id="vdefaultOpenMap%d">Squadra</button>
%s
                  </div>

                  <div id="Squadra%d" class="vtabcontmap%d">
                     <img src="maps/%d.png" height="700px" style="margin-left: 10px; vertical-align: top;">
                     <img src="players/Team.png" height="400px" style="margin-left: 10px; vertical-align: top;">
                  </div>
%s
    '''


    html_singlegame = '''
            <!-- PARTITA %d -->
            <div id="p%d" class="tabcontent">
                <div class="vtab">
                  <button class="vtablinks%d" style="height: 90px;" onclick="openContent(event, 'Tabellino%d', 'vtabcontent%d', 'vtablinks%d', '%s')" id="vdefaultOpen%d">Tabellino</button>
                  <button class="vtablinks%d" style="height: 90px;" onclick="openContent(event, 'Cronaca%d',   'vtabcontent%d', 'vtablinks%d', '%s')">Cronaca</button>
                  <button class="vtablinks%d" style="height: 90px;" onclick="openContent(event, 'Mappe%d',     'vtabcontent%d', 'vtablinks%d', '%s')">Mappe</button>
                  <button class="vtablinks%d" style="height: 90px;" onclick="openContent(event, 'Grafico%d',   'vtabcontent%d', 'vtablinks%d', '%s')">Grafico</button>
                  <button class="vtablinks%d" style="height: 90px;" onclick="openContent(event, 'Sintesi%d',   'vtabcontent%d', 'vtablinks%d', '%s')">Sintesi</button>
                  <button class="vtablinks%d" style="height: 90px;" onclick="openContent(event, 'Video%d',     'vtabcontent%d', 'vtablinks%d', '%s')">Video</button>
                </div>

                <div id="Tabellino%d" class="vtabcontent%d">
%s
                </div>

                <div id="Cronaca%d" class="vtabcontent%d">
%s
                </div>

                <div id="Mappe%d" class="vtabcontent%d">
%s            
                </div>

                <div id="Grafico%d" class="vtabcontent%d">
                    <img src="charts/%d.png" width="100%%">
                </div>

                <div id="Sintesi%d" class="vtabcontent%d">
%s
                </div>

                <div id="Video%d" class="vtabcontent%d">
                    <video id="video%d" width="100%%" controls>
                        <source src="%s" type="video/mp4">
                      Your browser does not support the video tag.
                    </video>
                </div>
            </div>
    '''

    html_games = '''
            <!-- LISTA PARTITE -->
            <div id="Partite" class="tabcontent">
              <h4>
                <ul>
                  <table style="font-size: max(14px, 1.2vw);">
    '''


    html_game1 = '''
                    <tr onclick="openContent(event, 'p%d', 'tabcontent', 'tablinks', '%s')">
                        <td align="right" width="3%%"><font color="#BB1010">%d.a&nbsp</font></td>
                        <td width="5%%"><font color="#BB1010">%s&nbsp</font></td>
                        <td width="2%%"><font color="#BB1010">%s&nbsp</font></td>
                        <td width="5%%"><font color="#BB1010">%s&nbsp</font></td>
                        <td width="5%%"><font color="#BB1010">%s&nbsp&nbsp</font></td>
                        <td width="70%%"><font color="%s"><b>%s</b></font></td>
                        <td align="left" width="10%%"><font color="%s"><b>%s</b></font></td></tr>'''

    html_game2 = '''
                    <tr onclick="openContent(event, 'p%d', 'tabcontent', 'tablinks', '%s')">
                        <td colspan="2" width="8%%"></td>
                        <td colspan="3" width="12%%" valign=top style="font-size: max(10px, 1.0vw);">%s</td>
                        <td width="70%%" style="font-size: max(10px, 1.0vw);">%s</td>
                        <td width="10%%"></td></tr>
                    <tr onclick="openContent(event, 'p%d', 'tabcontent', 'tablinks', '%s')">
                        <td colspan="2" width="8%%"></td>
                        <td colspan="3" width="12%%" valign=top style="font-size: max(10px, 1.0vw);">%s</td>
                        <td width="70%%" style="font-size: max(10px, 1.0vw);">%s</td>
                        <td width="10%%"></td></tr>
                    <tr><td height="10"></td></tr>
    '''

    html_tail = '''
                  </table>
                </ul>
              </h4>
            </div>

    <br>
            <div id="footer">
                <p>&copy; Copyright (C) 2011-2026 pyBasket</p>
            </div>
        </div>

        <script>
            function openContent(evt, name, class1, class2, curgame) {
                var i, tabcontent, tablinks, velem;

                if ( curgame.length > 0 )
                  document.getElementById('curgame').innerHTML = curgame;

                // Pause all videos
                for (i = 1; i < %d; i++){
                  vid = document.getElementById("video" + i); 
                  vid.pause();
                }

                tabcontent = document.getElementsByClassName(class1);
                for (i = 0; i < tabcontent.length; i++) {
                  tabcontent[i].style.display = "none";
                }
                tablinks = document.getElementsByClassName(class2);
                for (i = 0; i < tablinks.length; i++) {
                   tablinks[i].className = tablinks[i].className.replace(" active", "");
                }
                document.getElementById(name).style.display = "block";
                evt.currentTarget.className += " active";
            }

            // Get the element with id="defaultOpen" and click on it
            document.getElementById("defaultOpen").click();

            %s
        </script>
    </body>
    </html>
    '''

    colWin  = '#008800'
    colLost = '#AA0000'
    colNone = '#777777'

    htmlfile = open('web/index.html', 'w')

    sss = ''
    for i in range(1,len(allfiles)+1):
        sss += html_vtabcontent%(i,i,i)


    fff = ''
    for i in range(1,len(allfiles)+1):
        fff += html_function%(i,i,i)


    championship_name = sb.game.team_data['championship'] + ' - ' + sb.game.team_data['season']
    htmlfile.write(html_head%(sb.game.team_data['season'], sb.game.team_data['name'], sss, sb.game.team_data['name'], championship_name, championship_name, championship_name, championship_name))

    partite = ''

    
    # Store css and images
    store('web/css/layout.css')
    store('web/images/basket.ico')
    store('web/images/bg.gif')
    store('web/images/redbg.gif')
    store('web/images/logo.png')

    
    # Save players images
    for player_name in ['Team', 'Unknown'] + list(sb.game.team_data['players'].keys()):
        try:
            img = Image.open('./images/%s.jpg'%player_name)
        except:
            img = Image.open('./images/Unknown.jpg')
        iw,ih = img.size
        img = img.resize((round(iw*(520.0/ih)), 520))
        img.save('web/players/%s.png'%player_name, format='png')
        store('web/players/%s.png'%player_name)


    # Cycle on all games
    progressive = 1
    for phase in phases:

        # File of the phase
        files = [x for x in allfiles if phase in x and os.path.basename(x).split('-')[1] == phase]

        # Sort on increasing phase + round
        rounds = [toint(os.path.basename(x).split('.')[0]) for x in files]
        files  = [file for r, file in sorted(zip(rounds, files))]

        for file in files:
            sb.game.loadGame(file)
            g = sb.game.game_data

            points_team = Stats.points(sb.game.events_df)
            points_oppo = Stats.points(sb.game.events_df, team=Config.OPPO)
            if g['home']:
                game_name = sb.game.team_data['name'] + ' - ' + g['opponents'] + '  ' + str(points_team) + '-' + str(points_oppo)
            else:
                game_name = g['opponents'] + ' - ' + sb.game.team_data['name'] + '  ' + str(points_oppo) + '-' + str(points_team)

            with messages:
                print('%2d.a'%(int(g['round'])), '%-7s'%(str(g['phase'])), game_name)


            # Save Box Score in SVG format
            svg = BoxScore.svg(sb.game.events_df, game=sb.game, width=65.0)
            with open('web/sheets/%d.svg'%progressive, 'w') as outfile:
                outfile.write(svg)
            store('web/sheets/%d.svg'%progressive)

            # Save Box Score for every quarter (only if the game is terminated)
            quartersA = []
            quartersB = []
            if g['status']['gameover']:
                for quarter in range(1,g['status']['quarter']+1):
                    df = sb.game.events_df.copy()
                    svg = BoxScore.svg(df, game=sb.game, width=65.0, quarter=quarter)
                    with open('web/sheets/%d_%d.svg'%(progressive,quarter), 'w') as outfile:
                        outfile.write(svg)
                    store('web/sheets/%d_%d.svg'%(progressive,quarter))

                    qlabel = 'Q%d%d'%(progressive,quarter)
                    if quarter < 5:
                        qname = 'Q%d'%quarter
                    else:
                        qname = 'S%d'%(quarter-4)

                    quartersA.append(html_sheet_quarterA%(progressive, qlabel, progressive, progressive, '', qname))
                    quartersB.append(html_sheet_quarterB%(qlabel, progressive, progressive, quarter))

            game_sheet = html_sheet%(progressive,progressive,progressive,progressive, '', progressive, '\n'.join(quartersA), progressive, progressive, progressive, '\n'.join(quartersB) )


            # Save Points Chart in PNG format
            fig = BoxScore.pointsChart(sb.game.events_df, game=sb.game, template='plotly_white')
            bbb = fig.to_image('png', width=2000, height=700)
            with open('web/charts/%d.png'%progressive, 'wb') as pngfile:
                pngfile.write(bbb)
            store('web/charts/%d.png'%progressive)

            
            # Save Play-By-Play directly in the HTML
            pbp = BoxScore.play_by_play(sb.game.events_df, game=sb.game)
            pbphtml = '<div style="max-width: 100%%; overflow: hidden; background-color: #ffffff;">%s</div>'%(pbp)
            with open('web/playbyplay/%d.html'%progressive, 'w') as pbpfile:
                pbpfile.write(pbphtml)
            store('web/playbyplay/%d.html'%progressive)


            # Mappe di tiro
            m = ThrowMap.ThrowMap(board=sb, scale=0.85, field_left=True, output=output)
            m.updateThrows(sb.game.events_df, player_name=None, background=True)
            m.imgBackground.save('web/maps/%d.png'%progressive, format='png')
            store('web/maps/%d.png'%progressive)

            playerA = []
            playerB = []
            for player_name in sb.game.players_by_name:
                m.updateThrows(sb.game.events_df, player_name=player_name, background=True)
                m.imgBackground.save('web/maps/%d_%s.png'%(progressive,player_name), format='png')
                store('web/maps/%d_%s.png'%(progressive,player_name))

                plabel = 'P%d%s'%(progressive,player_name)
                playerA.append(html_mappe_playerA%(progressive, plabel, progressive, progressive, '', player_name))
                
                image_name = player_name
                if player_name not in sb.game.team_data['players']:
                    image_name = 'Unknown'
                playerB.append(html_mappe_playerB%(plabel, progressive, progressive, player_name, image_name))

            game_mappe = html_mappe%(progressive,progressive,progressive,progressive, '', progressive, '\n'.join(playerA), progressive, progressive, progressive, '\n'.join(playerB) )


            # Game summary
            summary = '''                    <p style="font-size: 1.4em; font-weight: 600; margin-left: 30px; color: black;">
                    %s
                    </p>''' % (BoxScore.summary(sb.game.events_df, game=sb.game).replace('\n','</br>'))


            # Video file name
            ddd = datetime.strptime(g['date'], '%d/%m/%Y').strftime('%Y_%m_%d')
            if g['home']:
                t1 = 'URBANIA'
                t2 = g['abbreviation']
            else:
                t1 = g['abbreviation']
                t2 = 'URBANIA'
            videofile = 'https://www.daigio.it/videos/' + ddd + '_' + t1 + '-' + t2 + '.mp4'


            htmlfile.write(html_singlegame%(progressive,
                                            progressive,
                                            progressive,progressive,progressive,progressive,'',progressive,
                                            progressive,progressive,progressive,progressive,'',
                                            progressive,progressive,progressive,progressive,'',
                                            progressive,progressive,progressive,progressive,'',
                                            progressive,progressive,progressive,progressive,'',
                                            progressive,progressive,progressive,progressive,'',
                                            progressive,progressive,
                                            game_sheet,
                                            progressive,progressive,
                                            '                    <iframe src="playbyplay/%d.html" width="100%%" height="900px" style="margin-left: 16px; border:none;"></iframe>'%progressive,
                                            progressive,progressive,
                                            game_mappe,
                                            progressive,progressive,progressive,
                                            progressive,progressive,
                                            summary,
                                            progressive,progressive,progressive, videofile))

            # Accumulate minutes and plusminus
            for player in sb.game.players_info.keys():
                pi = sb.game.players_info[player]
                if player in players_info:
                    players_info[player]['time_on_field'] += pi['time_on_field']
                    players_info[player]['plusminus']     += pi['plusminus']
                else:
                    players_info[player] = pi

            # Append all events
            df = sb.game.events_df
            if df.shape[0] > 0:
                name = file.replace('./data/','').replace('.game','')
                elems = name.split('-')
                ro = int(elems[0].replace('.a',''))
                ph = elems[1]
                op = elems[2]
                df['game_number'] = progressive
                df['round'] = ro
                df['phase'] = ph
                df['opponents'] = op
                df['home'] = sb.game.game_data['home']
                allevents.append(df)

            # Generate text for html
            pt = []
            po = []
            for player_name in sb.game.players_by_number:
                points = Stats.points(df, player_name)
                if sb.game.players_info[player_name]['time_on_field'] <= 0.0:
                    pt.append('%s ne'%player_name)
                else:
                    if points > 0: pt.append('%s %d'%(player_name, points))
                    else:          pt.append(player_name)

            for player_name in sb.game.opponents_by_number:
                points = Stats.points(df, player_name, team=Config.OPPO)
                if points > 0: po.append('%s %d'%(player_name,points))
                else:          po.append(player_name)

            fint = Stats.points(df)
            fino = Stats.points(df, team=Config.OPPO)
            if g['home']:
                t1 = sb.game.team_data['name']
                t2 = g['opponents']
                r1 = t1 + ' - ' + t2
                r2 = str(fint) + '-' + str(fino)
                p1 = ', '.join(pt)
                p2 = ', '.join(po)
            else:
                t1 = g['opponents']
                t2 = sb.game.team_data['name']
                r1 = t1 + ' - ' + t2
                r2 = str(fino) + '-' + str(fint)
                p1 = ', '.join(po)
                p2 = ', '.join(pt)

            showpoints = True
            if fint > fino:
                col = colWin
            elif fint < fino:
                col = colLost
            else:
                col = colNone
                showpoints = False
                r2 = ''

            d = datetime.strptime(g['date'], "%d/%m/%Y")
            day = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica'][d.weekday()]
            partite += html_game1%(progressive, game_name, g['round'], g['phase'], day, g['date'], g['time'], col, r1, col, r2)

            if showpoints:
                partite += html_game2%(progressive, game_name, t1, p1, progressive, game_name, t2, p2)

            progressive += 1


    htmlfile.write(html_games)
    htmlfile.write(partite)
    htmlfile.write(html_tail%(progressive, fff))
    htmlfile.close()

    store('web/index.html')

    df = pd.concat(allevents)
    df.reset_index(drop=True, inplace=True)

    # Totali e medie
    svg = BoxScore.totalsvg(df, game=sb.game, average=False, players_info=players_info, width=55.0)
    with open('web/sheets/totali.svg', 'w') as file:
        file.write(svg)
    store('web/sheets/totali.svg')

    svg = BoxScore.totalsvg(df, game=sb.game, average=True, players_info=players_info, width=55.0)
    with open('web/sheets/medie.svg', 'w') as file:
        file.write(svg)
    store('web/sheets/medie.svg')
    
    
    with messages:
        print('Done!')
        display(HTML('<a href="https://www.daigio.it/pybasket/" target="_blank">Visit pybasket site!</a>'))
