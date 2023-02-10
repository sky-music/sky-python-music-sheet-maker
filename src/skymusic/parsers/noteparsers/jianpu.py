# -*- coding: utf-8 -*-
import re
from collections import OrderedDict
from . import noteparser

class Jianpu(noteparser.NoteParser):

    CHROMATIC_SCALE = {'1': 0, '1#': 1, '2b': 1, '2': 2, '2#': 3, '3b': 3, '3': 4, '4': 5, '4#': 6, '5b': 6, '5': 7, '5#': 8, '6b': 8, '6': 9, '6#': 10, '7b': 10, '7': 11}
    
    # I have to use a function because names in class scope are not accessible to list comprehension: they are resolved in the innermost enclosing function scope, while list comprehension have a local namespace.
    def inv_scale(scale):
        return {scale[k]:k for k in reversed(OrderedDict(scale))}

    INVERSE_CHROMATIC_SCALE = inv_scale(CHROMATIC_SCALE)
    
    # Compile regexes for notes to save before using
    #(?<!\*)
    note_name_with_octave_regex = re.compile(r'([1234567][b#♭♯]?[\+\-]+)')
    note_name_regex = re.compile(r'([1234567][b#♭♯]?)')
    single_note_name_regex = re.compile(r'\b[1234567][b#♭♯]?[\+\-]?\b')
    note_octave_regex = re.compile(r'[\+\-]+')
    not_note_name_regex = re.compile(r'[^1234567b#♭♯]+')
    not_octave_regex = re.compile(r'[^\+\-]+')
    
    MAJOR_NOTES = ['1', '2', '3', '4', '5', '6', '7']

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.__set_coord_maps__(self.shape)

    def __set_coord_maps__(self, shape=None):
        '''Creates the correspondance dict between the (row,col) coordinates and the jianpu numbers'''
        if shape is None: shape=self.shape
        self.inv_coord_map = {(-1,-1): '.'}
        for i in range(0,shape[0]):
            for j in range(0,shape[1]):
                (quotient, remainder) = divmod(i*self.get_num_columns()+j, len(self.MAJOR_NOTES))
                note_name = self.MAJOR_NOTES[remainder]
                oct_str = '+' * quotient if quotient > 0 else ''
                self.inv_coord_map[(i,j)] = note_name + oct_str

    def get_note_octave(self, note):
        '''Extracts octave symbol from note string'''
        note_octave = re.search(r'(\+)+', note)
        if note_octave is not None:
            note_octave = self.get_default_starting_octave() + len(note_octave.group(0))
            return note_octave
        else:
            note_octave = re.search('(-)+', note)
            if note_octave is not None:
                note_octave = self.get_default_starting_octave() - len(note_octave.group(0))
                return note_octave
            else:
                # no octave (+ or -) found
                note_octave = self.get_default_starting_octave()
                return note_octave

    def get_note_from_position(self, coord):
        '''Gets note symbol from note coordinates (row, col)'''
        try:
            note = self.inv_coord_map[coord]
        except KeyError:
            note = 'X'

        return note

