import re

import noteparser


class Jianpu(noteparser.NoteParser):

    def __init__(self):

        super().__init__()

        self.CHROMATIC_SCALE_DICT = {'1': 0, '1#': 1, '2b': 1, '2': 2, '2#': 3, '3b': 3, '3': 4, '4': 5, '4#': 6,
                                     '5b': 6, '5': 7, '5#': 8, '6b': 8, '6': 9, '6#': 10, '7b': 10, '7': 11}

        # Compile regexes for notes to save before using
        self.note_name_with_octave_regex = re.compile(r'([1234567][b#]?[\\+\\-]+)')
        self.note_name_regex = re.compile(r'([1234567][b#]?)')
        self.single_note_name_regex = re.compile(r'\b[1234567][b#]?[\\+\\-]?\b')
        self.note_octave_regex = re.compile(r'[\\+\\-]+')
        self.not_note_name_regex = re.compile(r'[^1234567b#]+')
        self.not_octave_regex = re.compile(r'[^\\+\\-]+')

        self.inverse_position_map = {
            (0, 0): '1', (0, 1): '2', (0, 2): '3', (0, 3): '4', (0, 4): '5',
            (1, 0): '6', (1, 1): '7', (1, 2): '1+', (1, 3): '2+', (1, 4): '3+',
            (2, 0): '4+', (2, 1): '5+', (2, 2): '6+', (2, 3): '7+', (2, 4): '1++'
        }

    def get_note_octave(self, note):

        note_octave = re.search('(\\+)+', note)
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
