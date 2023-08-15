import io, json, importlib
from . import song_renderer
from skymusic import Lang, instruments
from skymusic.renderers.instrument_renderers.skyjson_ir import SkyjsonInstrumentRenderer
from skymusic.resources import Resources

class SkyjsonSongRenderer(song_renderer.SongRenderer):

    def __init__(self, locale=None, song_bpm=Resources.DEFAULT_BPM):

        super().__init__(locale)
        if isinstance(song_bpm, (int, float)):
            self.song_bpm = song_bpm  # Beats per minute
        else:
            self.song_bpm = Resources.DEFAULT_BPM

    def write_buffers(self, song):

        meta = song.get_meta()

        json_buffer = io.StringIO()

        instrument_renderer = SkyjsonInstrumentRenderer(self.locale)

        json_dict = {'name': meta['title'][1], 'author': meta['artist'][1],
                     'arrangedBy':'', 'transcribedBy': meta['transcript'][1],
                     'permission':'', 'type': 'composed',
                     'pitch': song.get_music_key(),
                     'bpm': int(self.song_bpm), 
                     'data':{"isComposed":True,"isComposedVersion":True,"appName":"Sky"},
                     'version':2,
                     'pitchLevel':0, 'bitsPerPage': 16,
                     'isEncrypted': False, 
                     'instruments': []}
        
        layers = self.build_layers(song.get_lines())
        # { 6:{'name':'Layer 9', 'instruments':[<skymusic.instruments.Harp object at 0x114682278>,....}, {7:{...} }
        
        instruments = [{'name': layers[layer]['name'], 'volume':100,'pitch':'','visible':True} for layer in layers]
        
        songNotes = self.render_old_format(layers)
        
        columns = self.render_to_new_format(layers)
        json_dict.update({'instruments':instruments, 'columns': columns, 'songNotes': songNotes})
        
        json_buffer.seek(0)
        json.dump([json_dict], json_buffer)
        return [json_buffer]
    
    def build_layers(self, song_lines):
        '''Builds a dictionary of layers, indexed by an integer, each layer value being a list of Instruments'''
        layers = {1: {'name':'','instruments':[]}}
        layer_index = 0 # Layers start at 1 in SkyStudio and Specy's SkyMusic, 0 is used for off bounds
        for line in song_lines:
            if len(line) > 0:
                linetype = line[0].get_type().lower().strip()
                if linetype == 'layer':
                    layer_index += 1
                    layers[layer_index] = {'name':line[0].get_text(), 'instruments':[]}
                elif line[0].get_is_tonal():
                    if layer_index == 0: layer_index += 1
                    layers[layer_index]['instruments'] += line
        
        return layers         
    
    def render_old_format(self, layers):
        
        dt = (60000/self.song_bpm)
        songNotes = []
        instrument_index = 0
        time = 0
        
        instrument_renderer = SkyjsonInstrumentRenderer(self.locale)
        
        for layer_index,layer in layers.items():
            for instrument in layer['instruments']:
                instrument.set_index(instrument_index)
                repeat = instrument.get_repeat()
                for r in range(repeat):
                    time += dt
                    if not instrument.get_is_silent():
                        songNotes += instrument_renderer.render(instrument, layer_index, time, version='old')

                instrument_index += 1
                
        return songNotes
        
    
    def render_to_new_format(self, layers):
        '''Render Sky-Music JSON columns from our layers dictionary'''
        # layers = {0: {name, instrs}, 1: {name, instrs}
        # instrs = [instr, instr...]
        #columns = [0, notes], [0, notes]
        # notes = [ [key,"hex_layer"],... ]
        # notes are sorted by order of appearence
        # a silence everywhere is an empty note list []
        instrument_renderer = SkyjsonInstrumentRenderer(self.locale)
        ncols = max([len(layer['instruments']) for layer_index, layer in layers.items()])
        for layer in layers: layers[layer]['instruments'] += [None]*(ncols-len(layers[layer]['instruments']))
        
        tempo_changer = 0 #means no change
        
        columns = []
        for col in range(ncols):
            notes = []
            for layer_index in layers:
                instrument = layers[layer_index]['instruments'][col]
                if instrument is not None: notes += instrument_renderer.render(instrument, layer_index, version='new')
            columns.append([tempo_changer, notes])
        
        return columns
        

    def generate_url(self, json_buffer, api_key=Resources.skyjson_api_key):
        # clears the sys.meta_path cache to reload packages(directory), does not really apply to top-level libraries
        importlib.invalidate_caches()
        try:
            import requests
        except (ImportError, ModuleNotFoundError):
            print("\n***WARNING: 'requests' package not installed: could not generate temp link to sky-music.herokuapp.com")
        
        else:
            json_buffer.seek(0)
            json_dict = json.load(json_buffer)
            json_dict = {'API_KEY': api_key, 'song': json_dict}
    
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            try:
                rep = requests.post(url=Resources.skyjson_api_url, json=json_dict, headers=headers, timeout=5)
                url = rep.text
    
            except (requests.ConnectionError, requests.HTTPError, requests.exceptions.ReadTimeout) as err:
                print('\n*** WARNING:'+Lang.get_string("warnings/skyjson_url_connection", self.locale)+':')
                print(err)
                url = None
    
            return url

