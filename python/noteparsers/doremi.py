import re

from . import noteparser


class Doremi(noteparser.NoteParser):

    def __init__(self):

        super().__init__()

        self.CHROMATIC_SCALE_DICT = {'do': 0, 'do#': 1, 'reb': 1, 're': 2, 're#': 3, 'mib': 3, 'mi': 4, 'fa': 5,
                                     'fa#': 6, 'solb': 6, 'sob': 6, 'sol': 7, 'so': 7, 'sol#': 8, 'so#': 8, 'lab': 8,
                                     'la': 9, 'la#': 10, 'sib': 10, 'tib': 10, 'si': 11, 'ti': 11}

        oct_str = ''
        oct_int = self.get_default_starting_octave()
        if oct_int > 1:
            oct_str = str(oct_int)

        self.inverse_position_map = {
            (0, 0): 'do' + oct_str, (0, 1): 're' + oct_str, (0, 2): 'mi' + oct_str, (0, 3): 'fa' + oct_str,
            (0, 4): 'sol' + oct_str,
            (1, 0): 'la' + oct_str, (1, 1): 'si' + oct_str, (1, 2): 'do' + str(oct_int + 1),
            (1, 3): 're' + str(oct_int + 1), (1, 4): 'mi' + str(oct_int + 1),
            (2, 0): 'fa' + str(oct_int + 1), (2, 1): 'sol' + str(oct_int + 1), (2, 2): 'la' + str(oct_int + 2),
            (2, 3): 'si' + str(oct_int + 2), (2, 4): 'do' + str(oct_int + 2)
        }

        # Compile regexes for notes to save before using
        self.note_name_with_octave_regex = re.compile(r'([DRMFSLTdrmfslt][OEIAoeia][Ll]?[b#]?\d)')
        self.note_name_regex = re.compile(r'([DRMFSLTdrmfslt][OEIAoeia][Ll]?[b#]?)')
        self.single_note_name_regex = re.compile(r'\b[DRMFSLTdrmfslt][OEIAoeia][Ll]?[b#]?\d?\b')
        self.note_octave_regex = re.compile(r'\d')
        self.not_note_name_regex = re.compile(r'[^DRMFSLTOEIAdrmfsltoeiab#]+')
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
