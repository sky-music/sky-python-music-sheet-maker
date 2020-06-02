import re

from . import noteparser

class SkyJson(noteparser.NoteParser):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.position_map = {
            '.': (-1, -1),
            'Key00': (0, 0), 'Key01': (0, 1), 'Key02': (0, 2), 'Key03': (0, 3), 'Key04': (0, 4),
            'Key05': (1, 0), 'Key06': (1, 1), 'Key07': (1, 2), 'Key08': (1, 3), 'Key09': (1, 4),
            'Key10': (2, 0), 'Key11': (2, 1), 'Key12': (2, 2), 'Key13': (2, 3), 'Key14': (2, 4)
        }

        self.inverse_position_map = {
            (-1, -1): '.',
            (0, 0): '1Key0', (0, 1): '1Key1', (0, 2): '1Key2', (0, 3): '1Key3', (0, 4): '1Key4',
            (1, 0): '1Key5', (1, 1): '1Key6', (1, 2): '1Key7', (1, 3): '1Key8', (1, 4): '1Key9',
            (2, 0): '1Key10', (2, 1): '1Key11', (2, 2): '1Key12', (2, 3): '1Key13', (2, 4): '1Key14'
        }


        self.note_name_with_octave_regex = re.compile(r'\d{2}(Key\d{2})', re.IGNORECASE)
        self.note_name_regex = self.note_name_with_octave_regex
        self.single_note_name_regex = re.compile(r'\b\d{2}(Key\d{2}\b)', re.IGNORECASE)
        self.note_octave_regex = re.compile(r'\b\d\d')
        self.not_note_name_regex = re.compile(r'[^Key\d]+', re.IGNORECASE) #not accurate
        self.not_octave_regex = re.compile(r'[^\d]+') #not accurate

    def calculate_coordinate_for_note(self, note, song_key='C', note_shift=0, is_finding_key=False):
        """
        Returns a tuple containing the row index and the column index of the note's position.
        """
        note = self.sanitize_note_name(note)

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

        note_name = note_name.lower().capitalize()
        
        return note_name

    def sanitize_digits(self, note):
        
        sanitized_note = re.sub(r'\b(\d)([^\d])', r'0\g<1>\g<2>', note)

        sanitized_note = re.sub(r'([^\d])(\d)\b', r'\g<1>0\g<2>', sanitized_note)
        
        return sanitized_note