import io
import json
from . import song_renderer
from src.skymusic.renderers.instrument_renderers.skyjson_ir import SkyjsonInstrumentRenderer


class SkyjsonSongRenderer(song_renderer.SongRenderer):

    def __init__(self, locale=None, song_bpm=120):
        
        super().__init__(locale)
        self.song_bpm = song_bpm

    def write_buffers(self, song):

        meta = song.get_meta()
        dt = (60000/self.song_bpm) / 4
        
        #print('%%DEBUG')
        #print(dt)
    
        json_buffer = io.StringIO()

        instrument_renderer = SkyjsonInstrumentRenderer(self.locale)
        
        json_dict = {'name': meta['title'][1], 'songNotes': []}
    
        instrument_index = 0
        time = 0
        for line in song.get_lines():
            if len(line) > 0:
                if line[0].get_type().lower().strip() != 'voice':
                    for instrument in line:
                        instrument.set_index(instrument_index)
                        repeat = instrument.get_repeat()
                        for r in range(repeat):
                            time += dt
                            if not instrument.get_is_silent():
                                json_dict['songNotes'] += instrument_renderer.render(instrument, time)
  
                        instrument_index += 1
                
        json.dump([json_dict], json_buffer)

        return [json_buffer]

