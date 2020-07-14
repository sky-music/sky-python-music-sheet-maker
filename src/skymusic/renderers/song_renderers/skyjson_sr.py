import io
import json
from . import song_renderer
from src.skymusic.renderers.instrument_renderers.skyjson_ir import SkyjsonInstrumentRenderer
from src.skymusic.resources import Resources

class SkyjsonSongRenderer(song_renderer.SongRenderer):

    def __init__(self, locale=None, song_bpm=Resources.DEFAULT_BPM):
        
        super().__init__(locale)
        if isinstance(song_bpm, (int, float)):
            self.song_bpm = song_bpm  # Beats per minute
        else:
            self.song_bpm = Resources.DEFAULT_BPM

    def write_buffers(self, song):

        meta = song.get_meta()
        dt = (60000/self.song_bpm) / 4
        
        json_buffer = io.StringIO()

        instrument_renderer = SkyjsonInstrumentRenderer(self.locale)
        
        json_dict = {'name': meta['title'][1], 'author': meta['artist'][1], 'arrangedBy':'', 'transcribedBy': meta['transcript'][1], 'permission':'', 'isComposed': True, 'bpm': int(self.song_bpm), 'pitchLevel':0, 'bitsPerPage': 16, 'songNotes': []}
    
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

        json_buffer.seek(0)
                
        json.dump(json_dict, json_buffer)
        
        return [json_buffer]

