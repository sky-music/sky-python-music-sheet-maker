from . import instrument_renderer
from skymusic.resources import Resources

class AsciiInstrumentRenderer(instrument_renderer.InstrumentRenderer):
    
    def __init__(self, locale=None):
        super().__init__(locale)


    def render_harp(self, instrument, note_parser=None):

        ascii_render = ''
        
        if instrument.get_is_broken():
            ascii_render = Resources.BROKEN_HARP
        elif instrument.get_is_silent():
            ascii_render = Resources.PAUSE
        else:
            skygrid = instrument.get_skygrid()
            
            for pos in skygrid:  # Cycle over (row, col) positions in an icon
                for f in skygrid[pos]:  # Cycle over triplets & quavers
                    if skygrid[pos][f]:  # Button is highlighted
                        ascii_render += note_parser.get_note_from_coordinate(pos)
                    if f > 0:
                        ascii_render += Resources.QUAVER_DELIMITER
            ascii_render = ascii_render.rstrip(Resources.QUAVER_DELIMITER)
            
        return ascii_render

    def render_voice(self, instrument, render_mode):
        voice_render = f"{Resources.LYRIC_DELIMITER}{instrument.get_lyric()}"  # Lyrics marked as comments in output text files
        return voice_render

