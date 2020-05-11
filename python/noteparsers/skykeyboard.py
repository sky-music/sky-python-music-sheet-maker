import re
import os

from . import skyabc15

class SkyKeyboard(skyabc15.SkyABC15):

    def __init__(self):

        super().__init__()

        if (os.getenv('LANG') == 'fr') or (os.getenv('LANG') == 'be'):
            self.position_map = {'.': (-1, -1), 'A': (0, 0), 'Z': (0, 1), 'E': (0, 2), 'R': (0, 3), 'T': (0, 4),
                                 'Q': (1, 0), 'S': (1, 1), 'D': (1, 2), 'F': (1, 3), 'G': (1, 4), 'W': (2, 0),
                                 'X': (2, 1), 'C': (2, 2), 'V': (2, 3), 'B': (2, 4)}
            regex = "AZERTQSDFGWXCVB"
        else:
            self.position_map = {'.': (-1, -1), 'Q': (0, 0), 'W': (0, 1), 'E': (0, 2), 'R': (0, 3), 'T': (0, 4),
                                 'A': (1, 0), 'S': (1, 1), 'D': (1, 2), 'F': (1, 3), 'G': (1, 4), 'Z': (2, 0),
                                 'X': (2, 1), 'C': (2, 2), 'V': (2, 3), 'B': (2, 4)}
            regex = "QWERTASDFGZXCVB"

        regex += regex.lower()
        self.note_name_with_octave_regex = re.compile(r'([' + regex + r'])')
        self.note_name_regex = self.note_name_with_octave_regex
        self.single_note_name_regex = re.compile(r'(\b[' + regex + r']\b)')
        self.not_note_name_regex = re.compile(r'[^' + regex + r']+')
        self.not_octave_regex = re.compile(r'.')
