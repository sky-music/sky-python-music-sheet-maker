from . import instrument_renderer
from src.skymusic.resources import Resources

class AsciiInstrumentRenderer(instrument_renderer.InstrumentRenderer):
    
    def __init__(self, locale=None):
        super().__init__(locale)


    def render_harp(self, instrument, note_parser=None):

        ascii_chord = ''

        if instrument.get_is_broken():
            ascii_chord = Resources.BROKEN_CHORD
        elif instrument.get_is_silent():
            ascii_chord = Resources.PAUSE
        else:
            chord_skygrid = instrument.get_chord_skygrid()
            for k in chord_skygrid:  # Cycle over positions in a frame
                for f in chord_skygrid[k]:  # Cycle over triplets & quavers
                    if chord_skygrid[k][f]:  # Button is highlighted
                        ascii_chord += note_parser.get_note_from_coordinate(k) + Resources.QUAVER_DELIMITER
            ascii_chord = ascii_chord.rstrip(Resources.QUAVER_DELIMITER)
            
        return ascii_chord


    def render_voice(self, instrument, render_mode):
        chord_render = f"{Resources.LYRIC_DELIMITER}{instrument.get_lyric()}"  # Lyrics marked as comments in output text files
        return chord_render

