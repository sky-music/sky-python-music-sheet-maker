from . import english

class EnglishChords(english.English):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        
        oct_int = self.get_default_starting_octave()
        if oct_int > 1:
            x = str(oct_int)
        else:
            x = ""
        y = str(oct_int + 1)

        self.chords = {
            'C': f"C{x}E{x}G{x}", 'D': f"D{x}A{x}", 'F': f"F{x}A{x}C{y}", 'G': f"G{x}B{x}D{y}",
            'Dm': f"D{x}F{x}A{x}", 'Em': f"E{x}G{x}B{x}", 'Am': f"A{x}C{y}E{y}", 'Bm': f"B{x}D{y}",
            'Bdim': f"B{x}D{y}F{y}", 'A+': f"A{x}C{y}F{y}",
            'Csus2': f"C{x}D{x}G{x}", 'Dsus2': f"C{x}E{x}A{x}", 'Fsus2': f"F{x}G{x}C{y}",
            'Gsus2': f"G{x}A{x}D{y}", 'Asus2': f"A{x}B{x}E{y}",
            'Csus{x}': f"C{x}F{x}G{x}", 'Dsus{x}': f"D{x}G{x}A{x}",
            'Esus{x}': f"E{x}A{x}B{x}", 'Gsus{x}': f"G{x}C{y}D{y}", 'Asus{x}': f"A{x}D{y}E{y}",
            'D7sus{x}': f"D{x}G{x}A{x}C{y}", 'E7sus{x}': f"E{x}A{x}B{x}D{y}",
            'G7sus{x}': f"G{x}C{y}D{y}F{y}", 'A7sus{x}': f"A{x}D{y}E{y}G{y}",
            'C6': f"C{x}E{x}G{x}A{x}", 'F6': f"F{x}A{x}C{y}D{y}", 'Fmaj6': f"F{x}A{x}C{y}D{y}", 'G6': f"G{x}B{x}D{y}E{y}",
            'G7': f"G{x}B{x}D{y}F{y}", 'G9': f"G{x}B{x}D{y}F{y}A{y}",
            'Cmaj7': f"C{x}E{x}G{x}B{x}", 'Fmaj7': f"F{x}A{x}C{y}E{y}",
            'Cmaj9': f"C{x}E{x}G{x}B{x}D{y}", 'Fmaj9': f"F{x}A{x}C{y}E{y}G{y}",
            'Cmaj11': f"C{x}E{x}G{x}B{x}D{y}F{y}", 'Dm6': f"D{x}F{x}A{x}B{x}",
            'Dm7': f"D{x}F{x}A{x}C{y}", 'Em7': f"E{x}G{x}B{x}D{y}", 'Am7': f"A{x}C{y}E{y}G{y}",
            'Dm9': f"D{x}F{x}A{x}C{y}E{y}", 'Am9': f"A{x}C{y}E{y}G{y}B{y}",
            'Dm11': f"D{x}F{x}A{x}C{y}E{y}G{y}", 'Am11': f"D{x}A{x}C{y}E{y}G{y}B{y}",
            'Cmaj': f"C{x}E{x}G{x}", 'Dmaj': f"D{x}A{x}", 'Fmaj': f"F{x}A{x}C{y}", 'Gmaj': f"G{x}B{x}D{y}",
            'Aaug': f"A{x}C{y}F{y}", 'Csus': f"C{x}F{x}G{x}", 'Dsus': f"D{x}G{x}A{x}",
            'Esus': f"E{x}A{x}B{x}", 'Gsus': f"G{x}C{y}D{y}", 'Asus': f"A{x}D{y}E{y}",
            'D7sus': f"D{x}G{x}A{x}C{y}", 'E7sus': f"E{x}A{x}B{x}D{y}", 'G7sus': f"G{x}C{y}D{y}F{y}",
            'A7sus': f"A{x}D{y}E{y}G{y}"
        }
        # use EnglishNoteParser as a helper parser for the individual notes
        self.helper_parser = english.English()

    def decode_chord(self, chord):
        """
            Splits a chord abbreviated name into individual note names
        """
        chord = self.sanitize_chord_name(chord)
        try:
            return self.chords[chord]
        except:
            return chord

    def sanitize_chord_name(self, chord):
        chord = chord.lower().capitalize()
        return chord

    def calculate_coordinate_for_note(self, note, song_key='C', note_shift=0, is_finding_key=False):

        return self.helper_parser.calculate_coordinate_for_note(note, song_key, note_shift, is_finding_key)
