from . import instrument_renderer
from skymusic.resources import Resources
from skymusic.parsers.noteparsers import skyjson as skyjson_parser


class SkyjsonInstrumentRenderer(instrument_renderer.InstrumentRenderer):
    
    def __init__(self, locale=None):
        super().__init__(locale)
        self.note_parser = skyjson_parser.SkyJson()

    def render_harp(self, instrument, time=0):

        json_render = []

        if instrument.get_is_broken():
            json_render = [{'time':int(time), 'key':'ERROR'}]
        elif instrument.get_is_silent():
            json_render = [{'time':int(time), 'key':'.'}]
        else:
            
            dt = Resources.SKYJSON_CHORD_DELAY/max([instrument.get_num_highlighted(),5])
            
            for frame in range(instrument.get_frame_count()):
                skygrid = instrument.get_skygrid(frame)                
                if skygrid:                
                    for coord in skygrid:  # Cycle over positions in a frame
                        if skygrid[coord][frame]:  # Button is highlighted
                            json_render += [{'time':int(time), 'key':self.note_parser.get_note_from_coordinate(coord)}]
                    time = time + dt
                        
        return json_render

    def render_voice(self, *args, **kwargs):   
        return NotImplemented
        
    def render_ruler(self, *args, **kwargs):   
        return NotImplemented
        
    def render_layer(self,*args,**kwargs):
        #TODO: handle layers: either here or in the song_parser
        return self.render_ruler(*args,**kwargs)
            
