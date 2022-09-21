# -*- coding: utf-8 -*-
import re
import os

from . import skyabc15

class SkyKeyboard(skyabc15.SkyABC15):

    """
    harp_coord_map = {'.': (-1, -1),
                                 'A': (0, 0), 'Z': (0, 1), 'E': (0, 2), 'R': (0, 3), 'T': (0, 4),
                                 'Q': (1, 0), 'S': (1, 1), 'D': (1, 2), 'F': (1, 3), 'G': (1, 4),
                                 'W': (2, 0), 'X': (2, 1), 'C': (2, 2), 'V': (2, 3), 'B': (2, 4)} # Valid as long as no instrument is larger than this
                                 
    harp_coord_map = {'.': (-1, -1),
                                 'Q': (0, 0), 'W': (0, 1), 'E': (0, 2), 'R': (0, 3), 'T': (0, 4),
                                 'A': (1, 0), 'S': (1, 1), 'D': (1, 2), 'F': (1, 3), 'G': (1, 4),
                                 'Z': (2, 0), 'X': (2, 1), 'C': (2, 2), 'V': (2, 3), 'B': (2, 4)} # Valid as long as no instrument is larger than this                                 
    """

    QWERTY = ("QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM")
    AZERTY = ("AZERTYUIOP", "QSDFGHJKLM", "WXCVBN")
    max_rows = len(QWERTY)
    max_cols = max((len(row) for row in QWERTY))
    
    coord_map = {'.': (-1, -1)}

    def __init__(self, *args, **kwargs):

        try:
            locale = kwargs['locale']
            french = re.match('fr', locale)
        except KeyError:
            french = re.match('fr', str(os.getenv('LANG')))

        if french:
            self.KEYBOARD = self.AZERTY
        else:
            self.KEYBOARD = self.QWERTY
        
        super().__init__(*args, **kwargs)
        #this call will call set_coord_map
        
        #self.__set_coord_maps__(self.shape)
            
        regex = re.sub(r'[^A-Z]','',''.join(self.coord_map.keys()))
        regex += regex.lower()
        #Cannot set these regex as class properties because we need to know the locale first
        self.note_name_with_octave_regex = re.compile(r'([' + regex + r'])')
        self.note_name_regex = self.note_name_with_octave_regex
        self.single_note_name_regex = re.compile(r'(\b[' + regex + r']\b)')
        self.not_note_name_regex = re.compile(r'[^' + regex + r']+')
        self.not_octave_regex = re.compile(r'.')

    def __set_coord_maps__(self, shape=None):
        '''Creates the correspondance dict between the (row,col) coordinates and the keyboard keys'''
        if shape is None: shape=self.shape
        
        self.coord_map = self.__class__.coord_map.copy()
        self.inv_coord_map = self.__class__.inv_coord_map.copy()
        
        for row in range(0,shape[0]):
            for col in range(0, shape[1]):
                try:
                    self.coord_map[self.KEYBOARD[row][col]] = (row, col)
                    self.inv_coord_map[(row,col)] = self.KEYBOARD[row][col]
                except IndexError:
                    pass
        
    def set_shape(self, shape):
        self.shape = shape
        self.__set_coord_maps__(shape)
        
    def get_coord_map(self, inverse=False):
        return self.inv_coord_map if inverse else self.coord_map                                                                        
