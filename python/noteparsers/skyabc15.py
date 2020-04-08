import re

from . import noteparser

class SkyABC15(noteparser.NoteParser):

    def __init__(self):

        super().__init__()

        self.position_map = {
            '.': (-1, -1),
            'A1': (0, 0), 'A2': (0, 1), 'A3': (0, 2), 'A4': (0, 3), 'A5': (0, 4),
            'B1': (1, 0), 'B2': (1, 1), 'B3': (1, 2), 'B4': (1, 3), 'B5': (1, 4),
            'C1': (2, 0), 'C2': (2, 1), 'C3': (2, 2), 'C4': (2, 3), 'C5': (2, 4)
        }

        self.inverse_position_map = {
            (-1, -1): '.',
            (0, 0): 'A1', (0, 1): 'A2', (0, 2): 'A3', (0, 3): 'A4', (0, 4): 'A5',
            (1, 0): 'B1', (1, 1): 'B2', (1, 2): 'B3', (1, 3): 'B4', (1, 4): 'B5',
            (2, 0): 'C1', (2, 1): 'C2', (2, 2): 'C3', (2, 3): 'C4', (2, 4): 'C5'
        }

        self.note_name_with_octave_regex = re.compile(r'([ABCabc][1-5])')
        self.note_name_regex = self.note_name_with_octave_regex
        self.single_note_name_regex = re.compile(r'(\b[ABCabc][1-5]\b)')
        self.not_note_name_regex = re.compile(r'[^ABCabc]+')
        self.not_octave_regex = re.compile(r'[^123]+')

    def calculate_coordinate_for_note(self, note, song_key='C', note_shift=0, is_finding_key=False):
        """
        Returns a tuple containing the row index and the column index of the note's position.
        """
        note = note.upper()

        if note in self.position_map.keys():  # Note Shift (ie transposition in Sky)
            pos = self.position_map[note]  # tuple
            if (pos[0] < 0) and (pos[1] < 0):  # Special character
                return pos
            else:
                idx = pos[0] * self.columns + pos[1]
                idx = idx + note_shift
                pos = (int(idx / self.columns), idx - self.columns * int(idx / self.columns))
                if (0, 0) <= pos <= (2, 4):
                    return pos
                else:
                    raise KeyError('Note ' + str(note) + ' was not in range of the Sky keyboard.')
        else:
            raise KeyError('Note ' + str(note) + ' was not found in the position_map dictionary.')

    def get_note_from_coordinate(self, coord):

        try:
            note = self.inverse_position_map[coord]
        except KeyError:
            note = 'X'

        return note

    def sanitize_note_name(self, note_name):

        # make sure the first letter of the note is uppercase, for sky note's dictionary keys
        note_name = note_name.capitalize()
        return note_name
