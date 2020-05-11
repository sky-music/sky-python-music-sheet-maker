import re

from . import noteparser


class English(noteparser.NoteParser):

    def __init__(self):

        super().__init__()

        self.CHROMATIC_SCALE_DICT = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6,
                                     'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}

        oct_str = ''
        oct_int = self.get_default_starting_octave()
        if oct_int > 1:
            oct_str = str(oct_int)

        self.inverse_position_map = {
            (0, 0): 'C' + oct_str, (0, 1): 'D', (0, 2): 'E' + oct_str, (0, 3): 'F' + oct_str, (0, 4): 'G' + oct_str,
            (1, 0): 'A' + oct_str, (1, 1): 'B' + oct_str, (1, 2): 'C' + str(oct_int + 1),
            (1, 3): 'D' + str(oct_int + 1), (1, 4): 'E' + str(oct_int + 1),
            (2, 0): 'F' + str(oct_int + 1), (2, 1): 'G' + str(oct_int + 1), (2, 2): 'A' + str(oct_int + 2),
            (2, 3): 'B' + str(oct_int + 2), (2, 4): 'C' + str(oct_int + 2)
        }

        # Compile regexes for notes to save before using
        self.note_name_with_octave_regex = re.compile(r'([ABCDEFGabcdefg][b#]?\d)')
        self.note_name_regex = re.compile(r'([ABCDEFGabcdefg][b#]?)')
        self.single_note_name_regex = re.compile(r'(\b[ABCDEFGabcdefg][b#]?\d?\b)')
        self.note_octave_regex = re.compile(r'\d')
        self.not_note_name_regex = re.compile(r'[^ABCDEFGabcdefgb#]+')
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
