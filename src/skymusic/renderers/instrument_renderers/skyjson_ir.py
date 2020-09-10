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
            skygrid = instrument.get_skygrid()
            
            dt = Resources.SKYJSON_CHORD_DELAY/max([instrument.get_num_highlighted(),5])
            for k in skygrid:  # Cycle over positions in a frame
                for f in skygrid[k]:  # Cycle over triplets & quavers
                    if skygrid[k][f]:  # Button is highlighted
                        json_render += [{'time':int(time), 'key':self.note_parser.get_note_from_coordinate(k)}]
                        time = time + dt
                        
        return json_render


    def render_voice(self, *args, **kwargs):    

        return NotImplemented
        
