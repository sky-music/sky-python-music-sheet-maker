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

            for frame in range(instrument.get_frame_count()): #Cycle over triplets & quavers
                skygrid = instrument.get_skygrid(frame)
                
                if skygrid:
                    for coord in skygrid:  # Cycle over (row, col) positions in an icon
                        if skygrid[coord][frame]:  # Button is highlighted
                            ascii_render += note_parser.get_note_from_coordinate(coord)
                    if frame > 0:
                        ascii_render += Resources.QUAVER_DELIMITER
            ascii_render = ascii_render.rstrip(Resources.QUAVER_DELIMITER)
            
        return ascii_render

    def render_voice(self, instrument, render_mode):
        voice_render = f"{Resources.LYRIC_DELIMITER}{instrument.get_lyric()}"  # Lyrics marked as comments in output text files
        return voice_render

