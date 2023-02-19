from . import instrument_renderer
from skymusic.resources import Resources
from skymusic.parsers.noteparsers import skyjson as skyjson_parser


class SkyjsonInstrumentRenderer(instrument_renderer.InstrumentRenderer):
    
    def __init__(self, locale=None):
        super().__init__(locale)
        self.note_parser = skyjson_parser.SkyJson()

    def render_harp(self, *args, **kwargs):

        version = kwargs.pop('version', 'old')
        
        if version == 'old':
            return self.__render_old_harp__(*args, **kwargs)
        elif version == 'new':
            return self.__render_new_harp__(*args, **kwargs)
        else:
            raise KeyError(version)

    def __render_old_harp__(self, instrument,layer=1, time=0):

        json_render = []
        if instrument.get_is_broken():
            json_render = [{'time':int(time), 'key':'ERROR'}]
        elif instrument.get_is_silent():
            json_render = [{'time':int(time), 'key':'.'}]
        else:
            
            dt = Resources.SKYJSON_CHORD_DELAY/max([instrument.get_num_highlighted(),5])
            
            for frame in instrument.get_highlighted_frames():
                coords = instrument.get_highlighted_coords(frame)
                if coords:
                    json_render += [{'time':int(time), 'key':self.note_parser.get_note_from_coord(coord,layer)} for coord in coords]
                    time = time + dt
                        
        return json_render

    def __render_new_harp__(self, instrument, layer_index=0):
        '''Split the instrument chord into a list of notes, along with the provided layer_index'''
        notes = []
        if not instrument:
            notes = []
        elif instrument.get_is_broken():
            notes = []
        elif instrument.get_is_silent():
            notes = []
        else:
            for frame in instrument.get_highlighted_frames():
                coords = instrument.get_highlighted_coords(frame)              
                if coords:      
                    notes += [self.note_parser.get_note_from_coord(coord,layer_index, version='new') for coord in coords]
       
        return notes

    def render_voice(self, *args, **kwargs):   
        return NotImplemented
        
    def render_ruler(self, *args, **kwargs):   
        return NotImplemented
        
    def render_layer(self,*args,**kwargs):
        #TODO: handle layers: either here or in the song_parser # Done?
        return self.render_ruler(*args,**kwargs)
            
