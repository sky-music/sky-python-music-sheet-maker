from . import instrument_renderer
from src.skymusic.resources import Resources
from src.skymusic.parsers.noteparsers import skyjson as skyjson_parser


class SkyjsonInstrumentRenderer(instrument_renderer.InstrumentRenderer):
    
    def __init__(self, locale=None):
        super().__init__(locale)
        self.note_parser = skyjson_parser.SkyJson()

    def render_harp(self, instrument, time=0):

        json_chord = []

        if instrument.get_is_broken():
            json_chord = [{'time':int(time), 'key':'ERROR'}]
        elif instrument.get_is_silent():
            json_chord = [{'time':int(time), 'key':'.'}]
        else:
            chord_skygrid = instrument.get_chord_skygrid()
            
            dt = Resources.SKYJSON_CHORD_DELAY/(instrument.get_num_highlighted()+0)
            for k in chord_skygrid:  # Cycle over positions in a frame
                for f in chord_skygrid[k]:  # Cycle over triplets & quavers
                    if chord_skygrid[k][f]:  # Button is highlighted
                        json_chord += [{'time':int(time), 'key':self.note_parser.get_note_from_coordinate(k)}]
                        time = time + dt
                        
        return json_chord


    def render_voice(self, *args, **kwargs):    

        return NotImplemented
        
