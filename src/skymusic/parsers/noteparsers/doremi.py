# -*- coding: utf-8 -*-
import re
from collections import OrderedDict
from . import noteparser


class Doremi(noteparser.NoteParser):

    MAJOR_NOTES = ['do', 're', 'mi', 'fa', 'sol', 'la', 'si']
    
    # Compile regexes for notes to save before using
    note_name_with_octave_regex = re.compile(r'([DRMFSLTdrmfslt][OEIAoeia][Ll]?[b#♭♯]?\d)')
    note_name_regex = re.compile(r'([DRMFSLTdrmfslt][OEIAoeia][Ll]?[b#♭♯]?)')
    single_note_name_regex = re.compile(r'\b[DRMFSLTdrmfslt][OEIAoeia][Ll]?[b#♭♯]?\d?\b')
    note_octave_regex = re.compile(r'\d')
    not_note_name_regex = re.compile(r'[^DRMFSLTOEIAdrmfsltoeiab#♭♯]+')
    not_octave_regex = re.compile(r'[^\d]+')    

    CHROMATIC_SCALE = {'do': 0, 'do#': 1, 'reb': 1, 're': 2, 're#': 3, 'mib': 3, 'mi': 4, 'fa': 5,'fa#': 6, 'solb': 6, 'sob': 6, 'sol': 7, 'so': 7, 'sol#': 8, 'so#': 8, 'lab': 8, 'la': 9, 'la#': 10, 'sib': 10, 'tib': 10, 'si': 11, 'ti': 11}

    # I have to use a function because names in class scope are not accessible to list comprehension: they are resolved in the innermost enclosing function scope, while list comprehension have a local namespace.
    def inv_scale(scale):
        return {scale[k]:k for k in reversed(OrderedDict(scale))}

    INVERSE_CHROMATIC_SCALE = inv_scale(CHROMATIC_SCALE)

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.__set_coord_maps__(self.shape)

    def __set_coord_maps__(self, shape=None):
        '''Creates the correspondance dict between the (row,col) coordinates and the doremi notation'''
        if shape is None: shape=self.shape
        oct_int = self.get_default_starting_octave()
        self.inv_coord_map = {(-1,-1):'.'}
        for i in range(shape[0]):
            for j in range(shape[1]):
                (quotient, remainder) = divmod(i*self.get_num_columns()+j, len(self.MAJOR_NOTES))
                note_name = self.MAJOR_NOTES[remainder]
                oct_str = str(oct_int + quotient) if (oct_int + quotient) > 1 else ''
                self.inv_coord_map[(i,j)] = note_name + oct_str       
                

    def sanitize_note_name(self, note_name):

        # make sure the first letter of the note is uppercase, for doremi note's dictionary keys
        note_name = note_name.lower()
        return note_name

    def get_note_from_coord(self, coord):

        try:
            note = self.inv_coord_map[coord]
        except KeyError:
            note = 'X'

        return note
