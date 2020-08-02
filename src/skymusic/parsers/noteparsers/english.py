# -*- coding: utf-8 -*-
import re

from . import noteparser


class English(noteparser.NoteParser):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.CHROMATIC_SCALE_DICT = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6,
                                     'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}

        oct_int = self.get_default_starting_octave()
        
        self.MAJOR_NOTES = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        self.inverse_position_map = {}
        for i in range(self.get_row_count()):
            for j in range(self.get_column_count()):
                (quotient, remainder) = divmod(i*self.get_column_count()+j, len(self.MAJOR_NOTES))
                note_name = self.MAJOR_NOTES[remainder]
                oct_str = str(oct_int + quotient) if (oct_int + quotient) > 1 else ''
                self.inverse_position_map[(i,j)] = note_name + oct_str

        # Compile regexes for notes to save before using
        self.note_name_with_octave_regex = re.compile(r'([ABCDEFGabcdefg][b#♭♯]?\d)')
        self.note_name_regex = re.compile(r'([ABCDEFGabcdefg][b#♭♯]?)')
        self.single_note_name_regex = re.compile(r'(\b[ABCDEFGabcdefg][b#♭♯]?\d?\b)')
        self.note_octave_regex = re.compile(r'\d')
        self.not_note_name_regex = re.compile(r'[^ABCDEFGabcdefgb#♭♯]+')
        self.not_octave_regex = re.compile(r'[^\d]+')

    def sanitize_note_name(self, note_name):
        # make sure the first letter of the note is uppercase, for english note's dictionary keys
        note_name = note_name.capitalize()
        return note_name

    def get_note_from_coordinate(self, coord):

        try:
            note = self.inverse_position_map[coord]
        except KeyError:
            note = 'X'

        return note
