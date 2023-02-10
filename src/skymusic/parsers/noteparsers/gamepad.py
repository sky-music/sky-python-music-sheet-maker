# -*- coding: utf-8 -*-
import re
from . import noteparser

class Gamepad(noteparser.NoteParser):
    """
    A parser class for gamepad buttons layouts of Playstation and Switch.
    A modes.GamepadLayout object must be supplied to init to choose the layout
    Do not declare this parser in skymusic.modes as it will never be used to input music notes, only for rendering sheets
    """
    coord_map = {'.': (-1, -1)}
    inv_coord_map = {(-1, -1): '.'}
    
    @classmethod
    def inv_map(cls, coord_map):
        return {coord_map[k]:k for k in coord_map}

    def __init__(self, *args, **kwargs):
        try:
            self.layout_key = kwargs.pop('layout')
        except KeyError:
            self.layout_key = None
        
        super().__init__(*args, **kwargs)
        
        if not self.layout_key:
            self.layout_key = self.INV_COORD_MAPS[self.shape].keys()[0]
        
        self.__set_coord_maps__(self.shape)

    def __set_coord_maps__(self, shape=None):
        '''Creates the correspondance dict between the (row,col) coordinates and the Gamepad buttons'''
        if shape is None: shape=self.shape
        
        self.coord_map = self.__class__.coord_map.copy()
        self.inv_coord_map = self.__class__.inv_coord_map.copy()
        self.inv_coord_map.update(self.INV_COORD_MAPS[self.shape][self.layout_key])
        self.coord_map.update(self.COORD_MAPS[self.shape][self.layout_key])

    def sanitize_note_name(self, note_name):
        # make sure the first letter of the note is uppercase, for english note's dictionary keys
        note_name = note_name.capitalize()
        return note_name

    def get_note_from_position(self, coord):
        try:
            note = self.inv_coord_map[coord]
        except KeyError:
            note = 'X'
        return note
        

class Playstation(Gamepad):
    
    INV_COORD_MAPS = {
            (3,5):
                {'PS1':
                    {(0,0): 'LD', (0,1): 'LU', (0,2): 'RD', (0,3): 'RU', (0,4): 'L2',
                    (1,0): 'R2', (1,1): 'L1', (1,2): 'R1', (1,3): 'D', (1,4): 'X',
                    (2,0): 'L', (2,1): 'S', (2,2): 'U', (2,3): 'T', (2,4): 'R'},
                'PS2':
                    {(0,0): 'LD', (0,1): 'R2', (0,2): 'D', (0,3): 'X', (0,4): 'L',
                    (1,0): 'S', (1,1): 'U', (1,2): 'T', (1,3): 'R', (1,4): 'C',
                    (2,0): 'L1', (2,1): 'R1', (2,2): 'LL', (2,3): 'RL', (2,4): 'LR'},
                'PS3':
                    {(0,0): 'LD', (0,1): 'LU', (0,2): 'RD', (0,3): 'RU', (0,4): 'D',
                    (1,0): 'X', (1,1): 'L', (1,2): 'S', (1,3): 'U', (1,4): 'T',
                    (2,0): 'R', (2,1): 'C', (2,2): 'L1', (2,3): 'R1', (2,4): 'L2'},       
                'PS4':
                    {(0,0): 'LD', (0,1): 'LL', (0,2): 'D', (0,3): 'R', (0,4): 'U',
                    (1,0): 'L1', (1,1): 'L2', (1,2): 'RD', (1,3): 'RR', (1,4): 'RU',
                    (2,0): 'X', (2,1): 'C', (2,2): 'T', (2,3): 'R1', (2,4): 'R2'}
                },
            (2,4):
                {'PS1':
                    {(0,0): 'U', (0,1): 'T', (0,2): 'L', (0,3): 'S',
                    (1,0): 'D', (1,1): 'X', (1,2): 'L2', (1,3): 'R2'
                    },
                }
            }
    COORD_MAPS = {shape:{k:Gamepad.inv_map(layout) for (k,layout) in layouts.items()} for shape,layouts in INV_COORD_MAPS.items()}
    
    _ALL_BUTTONS = []
    for shape in INV_COORD_MAPS:
        for layout in INV_COORD_MAPS[shape].values(): _ALL_BUTTONS += list(layout.values())
    _ALL_BUTTONS = list(set(_ALL_BUTTONS))
    
    # Compile regexes for notes to save before using
    regex = r'|'.join(_ALL_BUTTONS)
    note_name_with_octave_regex = re.compile(r'('+regex+r')')
    note_name_regex = note_name_with_octave_regex
    single_note_name_regex = re.compile(r'\b(' + regex + r')\b')
    not_note_name_regex = re.compile(r'[^' + regex + r']+')
    not_octave_regex = re.compile(r'.')    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
class Switch(Gamepad):
    
    INV_COORD_MAPS = {
            (3,5):
                {'SW1':
                    {(0,0): 'ZL', (0,1): 'ZR', (0,2): 'DD', (0,3): 'B', (0,4): 'DL', (1,0): 'Y', (1,1): 'DU', (1,2): 'X', (1,3): 'DR', (1,4): 'A', (2,0): 'L', (2,1): 'R', (2,2): 'LL', (2,3): 'RL', (2,4): 'LR'},
                'SW2': # Identical to SW1
                    {(0,0): 'ZL', (0,1): 'ZR', (0,2): 'DD', (0,3): 'B', (0,4): 'DL', (1,0): 'Y', (1,1): 'DU', (1,2): 'X', (1,3): 'DR', (1,4): 'A', (2,0): 'L', (2,1): 'R', (2,2): 'LL', (2,3): 'RL', (2,4): 'LR'},
                'SW3':
                    {(0,0): 'DD', (0,1): 'DL',(0,2): 'DU', (0,3): 'LD', (0,4): 'LL', (1,0): 'DL', ((1,1)): 'ZL', (1,2): 'RD', (1,3): 'RR', (1,4): 'RU', (2,0): 'B', (2,1): 'A', (2,2): 'X', (2,3): 'R', (2,4): 'ZR'},   
                },
            (2,4):
                {'SW1':
                    {(0,0): 'U', (0,1): 'X', (0,2): 'L', (0,3): 'Y',
                    (1,0): 'D', (1,1): 'B', (1,2): 'ZL', (1,3): 'ZR'
                    }
                }
            }
    
    COORD_MAPS = {shape:{k:Gamepad.inv_map(layout) for (k,layout) in layouts.items()} for shape,layouts in INV_COORD_MAPS.items()}
    
    _ALL_BUTTONS = []
    for shape in INV_COORD_MAPS:
        for layout in INV_COORD_MAPS[shape].values(): _ALL_BUTTONS += list(layout.values())
    _ALL_BUTTONS = list(set(_ALL_BUTTONS))
    
    # Compile regexes for notes to save before using
    regex = r'|'.join(_ALL_BUTTONS)
    note_name_with_octave_regex = re.compile(r'('+regex+r')')
    note_name_regex = note_name_with_octave_regex
    single_note_name_regex = re.compile(r'\b(' + regex + r')\b')
    not_note_name_regex = re.compile(r'[^' + regex + r']+')
    not_octave_regex = re.compile(r'.')    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
          
