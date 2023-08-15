# -*- coding: utf-8 -*-
import re
from collections import OrderedDict
from . import noteparser

class English(noteparser.NoteParser):

    MAJOR_NOTES = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
    #self.MAJOR_NOTES = list(OrderedDict({k:None for k in [k.strip('#').strip('b') for k in self.CHROMATIC_SCALE.keys()]}).keys())    

    CHROMATIC_SCALE = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6,
                                     'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}
    # I have to use a function because names in class scope are not accessible to list comprehension: they are resolved in the innermost enclosing function scope, while list comprehension have a local namespace.
    def inv_scale(scale):
        return {scale[k]:k for k in reversed(OrderedDict(scale))}

    INVERSE_CHROMATIC_SCALE = inv_scale(CHROMATIC_SCALE)

    # Compile regexes for notes to save before using
    note_name_with_octave_regex = re.compile(r'([ABCDEFGabcdefg][b#♭♯]?\d)')
    note_name_regex = re.compile(r'([ABCDEFGabcdefg][b#♭♯]?)')
    single_note_name_regex = re.compile(r'(\b[ABCDEFGabcdefg][b#♭♯]?\d?\b)')
    note_octave_regex = re.compile(r'\d')
    not_note_name_regex = re.compile(r'[^ABCDEFGabcdefgb#♭♯]+')
    not_octave_regex = re.compile(r'[^\d]+')

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.__set_coord_maps__(self.shape)

    def __set_coord_maps__(self, shape=None):
        '''Creates the correspondance dict between the (row,col) coordinates and the Western CDEFGAB notes'''
        if shape is None: shape=self.shape
        self.inv_coord_map = {(-1, -1): '.'}
        oct_int = self.get_default_starting_octave()
        for i in range(0,shape[0]):
            for j in range(0,shape[1]):
                (quotient, remainder) = divmod(i*self.get_num_columns()+j, len(self.MAJOR_NOTES))
                note_name = self.MAJOR_NOTES[remainder]
                oct_str = str(oct_int + quotient) if (oct_int + quotient) > 1 else ''
                self.inv_coord_map[(i,j)] = note_name + oct_str

    def sanitize_note_name(self, note_name):
        # make sure the first letter of the note is uppercase, for english note's dictionary keys
        note_name = note_name.capitalize()
        return note_name

    def get_note_from_coord(self, coord):

        try:
            note = self.inv_coord_map[coord]
        except KeyError:
            note = 'X'

        return note

