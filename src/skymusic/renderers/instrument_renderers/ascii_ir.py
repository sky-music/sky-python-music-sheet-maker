from . import instrument_renderer
from skymusic.resources import Resources

class AsciiInstrumentRenderer(instrument_renderer.InstrumentRenderer):
    
    def __init__(self, locale=None):
        super().__init__(locale)


    def render_harp(self, instrument, note_parser=None):

        ascii_render = ''
        
        if instrument.get_is_broken():
            ascii_render = Resources.DELIMITERS['broken_harp']
        elif instrument.get_is_silent():
            ascii_render = Resources.DELIMITERS['pause']
        else:

            for frame in range(instrument.get_frame_count()): #Cycle over triplets & quavers
                skygrid = instrument.get_skygrid(frame)
                
                if skygrid:
                    for coord in skygrid:  # Cycle over (row, col) positions in an icon
                        if skygrid[coord][frame]:  # Button is highlighted
                            ascii_render += note_parser.get_note_from_coordinate(coord)
                    if frame > 0:
                        ascii_render += Resources.DELIMITERS['quaver']
            ascii_render = ascii_render.rstrip(Resources.DELIMITERS['quaver'])
            
        return ascii_render

    def render_voice(self, instrument, note_parser=None):
        
        text = instrument.get_lyric()
        emphasis = instrument.emphasis
        start = ''
        end = ''
        if emphasis:
            if emphasis[0] == 'h':
                start = '#'*int(emphasis[1])
                end = ''
            elif emphasis == 'i':
                start = '*'
                end = '*'
            elif emphasis == 'b':
                start = '**'
                end = '**'
                
        voice_render = Resources.DELIMITERS['lyric']+start+text+end  # Lyrics marked as comments in output text files
            
        return voice_render


    def render_ruler(self, ruler, note_parser=None):
        
        return str(ruler)
