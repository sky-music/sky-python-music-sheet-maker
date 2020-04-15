import re
from . import doremi


class DoremiJP(doremi.Doremi):

    def __init__(self):
        super().__init__()

        self.CHROMATIC_SCALE_DICT = {'ド': 0, 'ド#': 1, 'レb': 1, 'レ': 2, 'レ#': 3, 'ミb': 3, 'ミ': 4, 'ファ': 5,
                                     'ファ#': 6, 'ソb': 6, 'ソ': 7, 'ソ#': 8, 'ラb': 8, 'ラ': 9, 'ラ#': 10, 'シb': 10, 'シ': 11,
                                     }

        # Compile regexes for notes to save before using
        self.note_name_with_octave_regex = re.compile(r'([ドレミフソラシ][ァ]?[b#]?\d)')
        self.note_name_regex = re.compile(r'([ドレミフソラシ][ァ]?[b#]?)')
        self.single_note_name_regex = re.compile(r'\b[ドレミフソラシ][ァ]?[b#]?\d?\b')
        self.note_octave_regex = re.compile(r'\d')
        self.not_note_name_regex = re.compile(r'[^ドレミフソラシァb#]+')
        self.not_octave_regex = re.compile(r'[^\d]+')
