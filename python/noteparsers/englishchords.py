#import re

from . import english

class EnglishChords(english.English):

    def __init__(self):

        super().__init__()

        oct_str = ''
        oct_int = self.get_default_starting_octave()
        if oct_int > 1:
            oct_str = str(oct_int)
        oct_str2 = str(oct_int + 1)

        self.english_chords = {
            'C': 'C' + oct_str + 'E' + oct_str + 'G' + oct_str, 'D': 'D' + oct_str + 'A' + oct_str,
            'F': 'F' + oct_str + 'A' + oct_str + 'C' + oct_str2, 'G': 'G' + oct_str + 'B' + oct_str + 'D' + oct_str2,
            'Dm': 'D' + oct_str + 'F' + oct_str + 'A' + oct_str, 'Em': 'E' + oct_str + 'G' + oct_str + 'B' + oct_str,
            'Am': 'A' + oct_str + 'C' + oct_str2 + 'E' + oct_str2, 'Bm': 'B' + oct_str + 'D' + oct_str2,
            'Bdim': 'B' + oct_str + 'D' + oct_str2 + 'F' + oct_str2,
            'A+': 'A' + oct_str + 'C' + oct_str2 + 'F' + oct_str2,
            'Csus2': 'C' + oct_str + 'D' + oct_str + 'G' + oct_str,
            'Dsus2': 'C' + oct_str + 'E' + oct_str + 'A' + oct_str,
            'Fsus2': 'F' + oct_str + 'G' + oct_str + 'C' + oct_str2,
            'Gsus2': 'G' + oct_str + 'A' + oct_str + 'D' + oct_str2,
            'Asus2': 'A' + oct_str + 'B' + oct_str + 'E' + oct_str2,
            'Csus' + oct_str: 'C' + oct_str + 'F' + oct_str + 'G' + oct_str,
            'Dsus' + oct_str: 'D' + oct_str + 'G' + oct_str + 'A' + oct_str,
            'Esus' + oct_str: 'E' + oct_str + 'A' + oct_str + 'B' + oct_str,
            'Gsus' + oct_str: 'G' + oct_str + 'C' + oct_str2 + 'D' + oct_str2,
            'Asus' + oct_str: 'A' + oct_str + 'D' + oct_str2 + 'E' + oct_str2,
            'D7sus' + oct_str: 'D' + oct_str + 'G' + oct_str + 'A' + oct_str + 'C' + oct_str2,
            'E7sus' + oct_str: 'E' + oct_str + 'A' + oct_str + 'B' + oct_str + 'D' + oct_str2,
            'G7sus' + oct_str: 'G' + oct_str + 'C' + oct_str2 + 'D' + oct_str2 + 'F' + oct_str2,
            'A7sus' + oct_str: 'A' + oct_str + 'D' + oct_str2 + 'E' + oct_str2 + 'G' + oct_str2,
            'C6': 'C' + oct_str + 'E' + oct_str + 'G' + oct_str + 'A' + oct_str,
            'F6': 'F' + oct_str + 'A' + oct_str + 'C' + oct_str2 + 'D' + oct_str2,
            'G6': 'G' + oct_str + 'B' + oct_str + 'D' + oct_str2 + 'E' + oct_str2,
            'G7': 'G' + oct_str + 'B' + oct_str + 'D' + oct_str2 + 'F' + oct_str2,
            'G9': 'G' + oct_str + 'B' + oct_str + 'D' + oct_str2 + 'F' + oct_str2 + 'A' + oct_str2,
            'Cmaj7': 'C' + oct_str + 'E' + oct_str + 'G' + oct_str + 'B' + oct_str,
            'Fmaj7': 'F' + oct_str + 'A' + oct_str + 'C' + oct_str2 + 'E' + oct_str2,
            'Cmaj9': 'C' + oct_str + 'E' + oct_str + 'G' + oct_str + 'D' + oct_str2,
            'Fmaj9': 'F' + oct_str + 'A' + oct_str + 'C' + oct_str2 + 'E' + oct_str2 + 'G' + oct_str2,
            'Cmaj11': 'C' + oct_str + 'E' + oct_str + 'G' + oct_str + 'D' + oct_str2 + 'F' + oct_str2,
            'Dm6': 'D' + oct_str + 'F' + oct_str + 'A' + oct_str + 'B' + oct_str,
            'Dm7': 'D' + oct_str + 'F' + oct_str + 'A' + oct_str + 'C' + oct_str2,
            'Em7': 'E' + oct_str + 'G' + oct_str + 'B' + oct_str + 'D' + oct_str2,
            'Am7': 'A' + oct_str + 'C' + oct_str2 + 'E' + oct_str2 + 'G' + oct_str2,
            'Dm9': 'D' + oct_str + 'F' + oct_str + 'A' + oct_str + 'C' + oct_str2 + 'E' + oct_str2,
            'Am9': 'A' + oct_str + 'C' + oct_str2 + 'E' + oct_str2 + 'G' + oct_str2 + 'B' + oct_str2,
            'Dm11': 'D' + oct_str + 'F' + oct_str + 'A' + oct_str + 'C' + oct_str2 + 'E' + oct_str2 + 'G' + oct_str2,
            'Am11': 'D' + oct_str + 'A' + oct_str + 'C' + oct_str2 + 'E' + oct_str2 + 'G' + oct_str2 + 'B' + oct_str2,
            'Cmaj': 'C' + oct_str + 'E' + oct_str + 'G' + oct_str, 'Dmaj': 'D' + oct_str + 'A' + oct_str,
            'Fmaj': 'F' + oct_str + 'A' + oct_str + 'C' + oct_str2,
            'Gmaj': 'G' + oct_str + 'B' + oct_str + 'D' + oct_str2,
            'Aaug': 'A' + oct_str + 'C' + oct_str2 + 'F' + oct_str2,
            'Csus': 'C' + oct_str + 'F' + oct_str + 'G' + oct_str,
            'Dsus': 'D' + oct_str + 'G' + oct_str + 'A' + oct_str,
            'Esus': 'E' + oct_str + 'A' + oct_str + 'B' + oct_str,
            'Gsus': 'G' + oct_str + 'C' + oct_str2 + 'D' + oct_str2,
            'Asus': 'A' + oct_str + 'D' + oct_str2 + 'E' + oct_str2,
            'D7sus': 'D' + oct_str + 'G' + oct_str + 'A' + oct_str + 'C' + oct_str2,
            'E7sus': 'E' + oct_str + 'A' + oct_str + 'B' + oct_str + 'D' + oct_str2,
            'G7sus': 'G' + oct_str + 'C' + oct_str2 + 'D' + oct_str2 + 'F' + oct_str2,
            'A7sus': 'A' + oct_str + 'D' + oct_str2 + 'E' + oct_str2 + 'G' + oct_str2
        }
        # use EnglishNoteParser as a helper parser for the individual notes
        self.helper_parser = english.English()

    def decode_chord(self, chord):
        """
            Splits a chord abbreviated name into individual note names
        """
        chord = self.sanitize_chord_name(chord)
        try:
            return self.english_chords[chord]
        except:
            return chord

    def sanitize_chord_name(self, chord):
        chord = chord.lower().capitalize()
        return chord

    def calculate_coordinate_for_note(self, note, song_key='C', note_shift=0, is_finding_key=False):

        return self.helper_parser.calculate_coordinate_for_note(note, song_key, note_shift, is_finding_key)
