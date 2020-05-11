import re

from . import noteparser

class SkyJson(noteparser.NoteParser):

    def __init__(self):

        super().__init__()

        self.position_map = {
            '.': (-1, -1),
            'Key0': (0, 0), 'Key1': (0, 1), 'Key2': (0, 2), 'Key3': (0, 3), 'Key4': (0, 4),
            'Key5': (1, 0), 'Key6': (1, 1), 'Key7': (1, 2), 'Key8': (1, 3), 'Key9': (1, 4),
            'Key10': (2, 0), 'Key11': (2, 1), 'Key12': (2, 2), 'Key13': (2, 3), 'Key14': (2, 4)
        }

        self.inverse_position_map = {
            (-1, -1): '.',
            (0, 0): 'Key0', (0, 1): 'Key1', (0, 2): 'Key2', (0, 3): 'Key3', (0, 4): 'Key4',
            (1, 0): 'Key5', (1, 1): 'Key6', (1, 2): 'Key7', (1, 3): 'Key8', (1, 4): 'Key9',
            (2, 0): 'Key10', (2, 1): 'Key11', (2, 2): 'Key12', (2, 3): 'Key13', (2, 4): 'Key14'
        }

        self.note_name_with_octave_regex = re.compile(r'(Key\d\d?)')
        self.note_name_regex = self.note_name_with_octave_regex
        self.single_note_name_regex = re.compile(r'(\bKey\d\d?\b)')
        self.not_note_name_regex = re.compile(r'[^Key\d]+')
        self.not_octave_regex = re.compile(r'[^\d]+')

    def calculate_coordinate_for_note(self, note, song_key='C', note_shift=0, is_finding_key=False):
        """
        Returns a tuple containing the row index and the column index of the note's position.
        """
        note = note.lower().capitalize()

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
        note_name = note_name.lower().capitalize()
        return note_name
