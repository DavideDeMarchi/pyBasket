"""Global configurations and constants"""
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


###########################################################################################################################################################################
# Constants
###########################################################################################################################################################################
TEAM = 'Team'
OPPO = 'Opponents'


###########################################################################################################################################################################
# List of all possible events
###########################################################################################################################################################################

# Short name of the event types
EVENT_NAME = {
     0: 'T1ok',
     1: 'T1err',
     2: 'T2ok',
     3: 'T2err',
     4: 'T3ok',
     5: 'T3err',
     6: 'ROff',
     7: 'RDif',
     8: 'PRec',
     9: 'PPer',
    10: 'Ass',
    11: 'SDat',
    12: 'SSub',
    13: 'FCom',
    14: 'FTec',
    15: 'FSub',
    16: 'Espu',
    17: 'Info',
    18: 'Entr',
    19: 'Usci',
    20: 'Time'
}


# Value of the event for the player evaluation
EVENT_VALUE = {
     0:  1,
     1: -1,
     2:  2,
     3: -1,
     4:  3,
     5: -1,
     6:  1,
     7:  1,
     8:  1,
     9: -1,
    10:  1,
    11:  1,
    12: -1,
    13: -1,
    14: -1,
    15:  1,
    16: -1,
    17:  0,
    18:  0,
    19:  0,
    20:  0
}


# Flag for Teams events (events that can be assigned to the team, like rebounds, technical fouls, etc.)
EVENT_TEAM = {
     0: False,
     1: False,
     2: False,
     3: False,
     4: False,
     5: False,
     6: True,
     7: True,
     8: True,
     9: True,
    10: False,
    11: False,
    12: False,
    13: False,
    14: True,
    15: False,
    16: False,
    17: False,
    18: False,
    19: False,
    20: False,
}


# Flag for countable events (those that must be accumulated)
EVENT_COUNTABLE = {
     0: True,
     1: True,
     2: True,
     3: True,
     4: True,
     5: True,
     6: True,
     7: True,
     8: True,
     9: True,
    10: True,
    11: True,
    12: True,
    13: True,
    14: True,
    15: True,
    16: True,
    17: True,
    18: False,
    19: False,
    20: False
}


# Long description of event types
EVENT_DESCRIPTION = {
     0: 'Tiro libero centrato',
     1: 'Tiro libero sbagliato',
     2: 'Tiro da 2 centrato',
     3: 'Tiro da 2 sbagliato',
     4: 'Tiro da 3 centrato',
     5: 'Tiro da 3 sbagliato',
     6: 'Rimbalzo offensivo',
     7: 'Rimbalzo difensivo',
     8: 'Palla recuperata',
     9: 'Palla Persa',
    10: 'Assist',
    11: 'Stoppata data',
    12: 'Stoppata subita',
    13: 'Fallo commesso',
    14: 'Fallo tecnico',
    15: 'Fallo subito',
    16: 'Espulsione',
    17: 'Infortunio',
    18: 'Entrata in campo',
    19: 'Uscita dal campo',
    20: 'Time-out'
}


# Full table of the event types
EVENTS = [
    {'id':  0, 'name': EVENT_NAME[0],  'value': EVENT_VALUE[0],  'team': EVENT_TEAM[0],  'row': 1, 'description': EVENT_DESCRIPTION[0]  },
    {'id':  1, 'name': EVENT_NAME[1],  'value': EVENT_VALUE[1],  'team': EVENT_TEAM[1],  'row': 1, 'description': EVENT_DESCRIPTION[1]  },
    {'id':  2, 'name': EVENT_NAME[2],  'value': EVENT_VALUE[2],  'team': EVENT_TEAM[2],  'row': 1, 'description': EVENT_DESCRIPTION[2]  },
    {'id':  3, 'name': EVENT_NAME[3],  'value': EVENT_VALUE[3],  'team': EVENT_TEAM[3],  'row': 1, 'description': EVENT_DESCRIPTION[3]  },
    {'id':  4, 'name': EVENT_NAME[4],  'value': EVENT_VALUE[4],  'team': EVENT_TEAM[4],  'row': 1, 'description': EVENT_DESCRIPTION[4]  },
    {'id':  5, 'name': EVENT_NAME[5],  'value': EVENT_VALUE[5],  'team': EVENT_TEAM[5],  'row': 1, 'description': EVENT_DESCRIPTION[5]  },
    {'id':  7, 'name': EVENT_NAME[7],  'value': EVENT_VALUE[7],  'team': EVENT_TEAM[7],  'row': 2, 'description': EVENT_DESCRIPTION[7]  },
    {'id':  6, 'name': EVENT_NAME[6],  'value': EVENT_VALUE[6],  'team': EVENT_TEAM[6],  'row': 2, 'description': EVENT_DESCRIPTION[6]  },
    {'id':  8, 'name': EVENT_NAME[8],  'value': EVENT_VALUE[8],  'team': EVENT_TEAM[8],  'row': 2, 'description': EVENT_DESCRIPTION[8]  },
    {'id':  9, 'name': EVENT_NAME[9],  'value': EVENT_VALUE[9],  'team': EVENT_TEAM[9],  'row': 2, 'description': EVENT_DESCRIPTION[9]  },
    {'id': 10, 'name': EVENT_NAME[10], 'value': EVENT_VALUE[10], 'team': EVENT_TEAM[10], 'row': 2, 'description': EVENT_DESCRIPTION[10] },
    {'id': 11, 'name': EVENT_NAME[11], 'value': EVENT_VALUE[11], 'team': EVENT_TEAM[11], 'row': 2, 'description': EVENT_DESCRIPTION[11] },
    {'id': 12, 'name': EVENT_NAME[12], 'value': EVENT_VALUE[12], 'team': EVENT_TEAM[12], 'row': 2, 'description': EVENT_DESCRIPTION[12] },
    {'id': 13, 'name': EVENT_NAME[13], 'value': EVENT_VALUE[13], 'team': EVENT_TEAM[13], 'row': 1, 'description': EVENT_DESCRIPTION[13] },
    {'id': 15, 'name': EVENT_NAME[15], 'value': EVENT_VALUE[15], 'team': EVENT_TEAM[15], 'row': 1, 'description': EVENT_DESCRIPTION[15] },
    {'id': 14, 'name': EVENT_NAME[14], 'value': EVENT_VALUE[14], 'team': EVENT_TEAM[14], 'row': 1, 'description': EVENT_DESCRIPTION[14] },
    {'id': 16, 'name': EVENT_NAME[16], 'value': EVENT_VALUE[16], 'team': EVENT_TEAM[16], 'row': 1, 'description': EVENT_DESCRIPTION[16] },
    {'id': 17, 'name': EVENT_NAME[17], 'value': EVENT_VALUE[17], 'team': EVENT_TEAM[17], 'row': 2, 'description': EVENT_DESCRIPTION[17] },
    {'id': 18, 'name': EVENT_NAME[18], 'value': EVENT_VALUE[18], 'team': EVENT_TEAM[18], 'row': 2, 'description': EVENT_DESCRIPTION[18] },
    {'id': 19, 'name': EVENT_NAME[19], 'value': EVENT_VALUE[19], 'team': EVENT_TEAM[19], 'row': 2, 'description': EVENT_DESCRIPTION[19] },
    {'id': 20, 'name': EVENT_NAME[20], 'value': EVENT_VALUE[20], 'team': EVENT_TEAM[20], 'row': 0, 'description': EVENT_DESCRIPTION[20] },
]
