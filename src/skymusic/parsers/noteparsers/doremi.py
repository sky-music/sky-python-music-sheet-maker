# -*- coding: utf-8 -*-
import re
from collections import OrderedDict
from . import noteparser


class Doremi(noteparser.NoteParser):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.CHROMATIC_SCALE_DICT = {'do': 0, 'do#': 1, 'reb': 1, 're': 2, 're#': 3, 'mib': 3, 'mi': 4, 'fa': 5,
                                     'fa#': 6, 'solb': 6, 'sob': 6, 'sol': 7, 'so': 7, 'sol#': 8, 'so#': 8, 'lab': 8,
                                     'la': 9, 'la#': 10, 'sib': 10, 'tib': 10, 'si': 11, 'ti': 11}
        self.INVERSE_CHROMATIC_SCALE_DICT = {self.CHROMATIC_SCALE_DICT[k]:k for k in reversed(OrderedDict(self.CHROMATIC_SCALE_DICT))}

        oct_int = self.get_default_starting_octave()
        
        self.MAJOR_NOTES = ['do', 're', 'mi', 'fa', 'sol', 'la', 'si']
        self.inverse_position_map = {}
        for i in range(self.get_row_count()):
            for j in range(self.get_column_count()):
                (quotient, remainder) = divmod(i*self.get_column_count()+j, len(self.MAJOR_NOTES))
                note_name = self.MAJOR_NOTES[remainder]
                oct_str = str(oct_int + quotient) if (oct_int + quotient) > 1 else ''
                self.inverse_position_map[(i,j)] = note_name + oct_str

        # Compile regexes for notes to save before using
        self.note_name_with_octave_regex = re.compile(r'([DRMFSLTdrmfslt][OEIAoeia][Ll]?[b#♭♯]?\d)')
        self.note_name_regex = re.compile(r'([DRMFSLTdrmfslt][OEIAoeia][Ll]?[b#♭♯]?)')
        self.single_note_name_regex = re.compile(r'\b[DRMFSLTdrmfslt][OEIAoeia][Ll]?[b#♭♯]?\d?\b')
        self.note_octave_regex = re.compile(r'\d')
        self.not_note_name_regex = re.compile(r'[^DRMFSLTOEIAdrmfsltoeiab#♭♯]+')
        self.not_octave_regex = re.compile(r'[^\d]+')

    def sanitize_note_name(self, note_name):

        # make sure the first letter of the note is uppercase, for doremi note's dictionary keys
        note_name = note_name.lower()
        return note_name

    def get_note_from_coordinate(self, coord):

        try:
            note = self.inverse_position_map[coord]
        except KeyError:
            note = 'X'

        return note
