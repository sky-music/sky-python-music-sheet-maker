# -*- coding: utf-8 -*-
import re
from collections import OrderedDict
from . import noteparser


class Jianpu(noteparser.NoteParser):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.CHROMATIC_SCALE_DICT = {'1': 0, '1#': 1, '2b': 1, '2': 2, '2#': 3, '3b': 3, '3': 4, '4': 5, '4#': 6,
                                     '5b': 6, '5': 7, '5#': 8, '6b': 8, '6': 9, '6#': 10, '7b': 10, '7': 11}
        
        self.INVERSE_CHROMATIC_SCALE_DICT = {self.CHROMATIC_SCALE_DICT[k]:k for k in reversed(OrderedDict(self.CHROMATIC_SCALE_DICT))}

        # Compile regexes for notes to save before using
        self.note_name_with_octave_regex = re.compile(r'([1234567][b#♭♯]?[\+\-]+)')
        self.note_name_regex = re.compile(r'([1234567][b#♭♯]?)')
        self.single_note_name_regex = re.compile(r'\b[1234567][b#♭♯]?[\+\-]?\b')
        self.note_octave_regex = re.compile(r'[\+\-]+')
        self.not_note_name_regex = re.compile(r'[^1234567b#♭♯]+')
        self.not_octave_regex = re.compile(r'[^\+\-]+')
        
        self.MAJOR_NOTES = ['1', '2', '3', '4', '5', '6', '7']
        self.inverse_position_map = {}
        for i in range(self.get_row_count()):
            for j in range(self.get_column_count()):
                (quotient, remainder) = divmod(i*self.get_column_count()+j, len(self.MAJOR_NOTES))
                note_name = self.MAJOR_NOTES[remainder]
                oct_str = '+' * quotient if quotient > 0 else ''
                self.inverse_position_map[(i,j)] = note_name + oct_str

    def get_note_octave(self, note):

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

    def get_note_from_coordinate(self, coord):

        try:
            note = self.inverse_position_map[coord]
        except KeyError:
            note = 'X'

        return note
