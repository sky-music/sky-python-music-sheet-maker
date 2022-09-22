# -*- coding: utf-8 -*-
import re
from collections import OrderedDict
from . import doremi

class DoremiJP(doremi.Doremi):

    # Compile regexes for notes to save before using
    note_name_with_octave_regex = re.compile(r'([ドレミフソラシ][ァ]?[b#♭♯]?\d)')
    note_name_regex = re.compile(r'([ドレミフソラシ][ァ]?[b#♭♯]?)')
    single_note_name_regex = re.compile(r'\b[ドレミフソラシ][ァ]?[b#♭♯]?\d?\b')
    note_octave_regex = re.compile(r'\d')
    not_note_name_regex = re.compile(r'[^ドレミフソラシァb#♭♯]+')
    not_octave_regex = re.compile(r'[^\d]+')

    CHROMATIC_SCALE = {'ド': 0, 'ド#': 1, 'レb': 1, 'レ': 2, 'レ#': 3, 'ミb': 3, 'ミ': 4, 'ファ': 5, 'ファ#': 6, 'ソb': 6, 'ソ': 7, 'ソ#': 8, 'ラb': 8, 'ラ': 9, 'ラ#': 10, 'シb': 10, 'シ': 11, }
    
    MAJOR_NOTES = ['ド', 'レ', 'ミ', 'ファ', 'ソ', 'ラ', 'シ']
    
    # I have to use a function because names in class scope are not accessible to list comprehension: they are resolved in the innermost enclosing function scope, while list comprehension have a local namespace.
    def inv_scale(scale):
        return {scale[k]:k for k in reversed(OrderedDict(scale))}

    INVERSE_CHROMATIC_SCALE = inv_scale(CHROMATIC_SCALE)

    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)

        
