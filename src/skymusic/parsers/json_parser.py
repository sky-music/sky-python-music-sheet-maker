import json, re
from skymusic.resources import Resources
from . import song_parser
from skymusic.parsers import music_theory

class JsonSongParser(song_parser.SongParser):
    """
    For parsing a text format into a Song object
    """

    def __init__(self, maker, instrument_type=Resources.DEFAULT_INSTRUMENT, silent_warnings=True):

        super().__init__(maker=maker, silent_warnings=silent_warnings)
        self.skyjson_chord_delay = Resources.SKYJSON_CHORD_DELAY #Delay in ms below which 2 notes are considered a chord
        self.music_theory = music_theory.MusicTheory(self)

    def sanitize_lines(self, lines, join=False):
        '''Removes spaces in each string item (icon) of song_lines'''
        lines = list(filter(None,map(str.strip, lines)))
        if join:
            lines = [''.join(lines)]
        return lines

    def join_icons(self, icons):
        '''join icons in a string'''
        icons = self.sanitize_lines(icons,join=False)
        return self.icon_delimiter.join(icons)
                        
    def detect_json(self, song_lines):
        
        song_lines = self.sanitize_lines(song_lines)#join?
        if song_lines:
            c0 = song_lines[0][0]
            if c0 == '[' or c0 == '{':
                if self.load_dict(''.join(song_lines)):
                    return True
        return False
                             
    def load_dict(self, lines):
        
        try:
            try:
                json_dict = json.loads(lines)
            except json.JSONDecodeError:
               json_dict = json.loads(re.sub(r'\\{','{',lines))

            if isinstance(json_dict, list):
                json_dict = json_dict[0]
        except (json.JSONDecodeError, TypeError, KeyError, UnicodeDecodeError):
            json_dict = None
        
        if json_dict:
            try:
                is_encrypted = json_dict['isEncrypted']
            except KeyError:
                is_encrypted = False            
            if is_encrypted:
                print("\n***WARNING: cannot parse an encrypted JSON recording") 
                json_dict = None
        
        return json_dict

    def convert_to_old_format(self, columns, bpm):
        
        LAYERS_BINMAP = {'100':1, '001':2, '010':2, '011':2, '111':3, '110':3, '111':3,'0000':1, '0010':2, '0110':2, '0100':2, '1010':3, '1000':1, '1110':3, '1100':3, '0001':2,'0011':2, '0111':2,'0101':2, '1011':3, '1001':1, '1111':3, '1101':3}
        SILENCE = -1
        tempo_changers = [1, 1/2, 1/4, 1/8]
        bpm_ms = int(60000/bpm)
        elapsed_time0 = 100
        
        layered_notes = {}
        
        #Detects layer format: hex string or binary string
        #the loops ensure that we process non empty items
        for col in columns:
            if col[1]:
                for note in col[1]:
                    try:
                        LAYERS_BINMAP[note[1]]
                        is_hex = False
                    except KeyError:
                        is_hex = True
                    break
        
        layers = {str(k):[] for k in range(1,100)} # Layers start at 1 in SkyStudio and Specy's SkyMusic
        
        for col in columns:
            tempo_changer = tempo_changers[col[0]]
            
            if not col[1]: #no notes
                for layer in layers: layers[layer] += [SILENCE]
                    
            #note = [index, "layer"]
            for note in col[1]:          
                layer = str(int('0x'+note[1],16)) if is_hex else layers.get(note[1],1)
                layers[layer] += [note[0]]

        #old format is 3Key4, 2Key14
        #Layers start at 1
        #Notes start at 0
        for layer, note_indices in layers.items():
            elapsed_time = elapsed_time0
            note_dicts = []
            for notei in note_indices:
                if notei != SILENCE:
                    note_dicts += [{'time':elapsed_time, 'key':str(layer if is_hex else LAYERS_BINMAP[layer])+"Key"+str(notei)}]
                elapsed_time += round(bpm_ms*tempo_changer)
            
            if note_dicts:
                layered_notes[layer] = layered_notes.get(layer,[]) + note_dicts
        
        return layered_notes

    def sort_by_layer(self, songNotes):
        '''Builds layers and distribute old notes among them'''
        layered_notes = {}
        for note in songNotes:   
            layer = self.note_parser.get_layer(note['key'],default='1')
            layered_notes[layer] = layered_notes.get(layer,[]) + [note]
        
        return layered_notes
        

    def parse_json_midi(self, json_dict):
        
        raise NotImplementedError('***WARNING: your JSON file has been converted from a Midi file. This format is not supported. Please provide the original .mid file')
        return []

    def parse_metadata(self, song_lines, song):
        
        if len(song_lines) > 0:
            text = ''.join(song_lines)
        else:
            text = song_lines[0]
        json_dict = self.load_dict(text)
        changed = False
        
        meta_data = {}
        
        try:
            meta_data['title'] = json_dict['name']
            changed = True
        except KeyError:
            changed = False
        meta_data['artist'] = json_dict.get('author','')
        meta_data['transcript'] = ', '.join(filter(None,[json_dict.get('arrangedBy',''), json_dict.get('transcribedBy','')]))
        meta_data['song_key'] = json_dict.get('pitchLevel','')
        if not meta_data['song_key']:
            meta_data['song_key'] = json_dict.get('pitch','')
        
        return (changed, meta_data)

    def extract_note_interval(self, times):
        
        intervals = [interval for interval in self.music_theory.analyze_tempo(times, self.skyjson_chord_delay) if interval > 2*self.skyjson_chord_delay]
        
        if len(intervals) > 0:
            note_interval = intervals[0]
        else:
            note_interval = None
            
        return note_interval

    def parse_layers(self, line):
        
        json_dict = self.load_dict(line)
        
        if json_dict is None:
            return [line]
        
        # The existence of this field has already been assessed by MusicTheory
        bpm = json_dict.get('bpm',220)
        
        instruments = json_dict.get('instruments',[])
        instr_names = iter([instr.get("name","") for instr in instruments])
        
        if 'columns' in json_dict:
            layered_notes = self.convert_to_old_format(json_dict['columns'], bpm)
        elif 'songNotes' in json_dict:
            layered_notes = self.sort_by_layer(json_dict['songNotes'])
        elif 'tracks' in json_dict:
            layered_notes = [self.parse_json_midi(json_dict)]
        else:
            raise Exception('JSON file contains an invalid music sheet format.')
        
        layers = []
        for i, (layer_index, notes) in enumerate(layered_notes.items()):
            
            times = [note['time'] for note in notes]
            keys = [note['key'] for note in notes]
            
            # A Special trick to have the same number of digit for all numbers
            # Facilitates the splitting of glued chords into notes
            keys = [self.get_note_parser().sanitize_digits(key) for key in keys]
    
            note_interval = self.extract_note_interval(times)
            
            if note_interval is None:
                note_interval = 2*self.skyjson_chord_delay
            #keys=['01Key3','01Key8',]
            icons = []
            if keys:
                icons += [keys[0]]
            
                for i in range(1,len(times)):
                    if times[i] - times[i-1] < self.skyjson_chord_delay:
                        icons[-1] += keys[i] # Notes belong to the same chord
                    else:
                        n_pauses = max([0, round((times[i] - times[i-1])/note_interval - 1)])
                        if n_pauses > 0:
                            icons += [self.pause + (self.repeat_indicator + str(n_pauses) if n_pauses > 1 else '')]
                        
                        icons += [keys[i]]
            
            icons = self.join_icons(icons) # merge icons
            
            # self.icon_delimiter.join(icons)
            #merge icons into a string
            
            if len(layered_notes) > 1:
                try:
                    instr_name = next(instr_names)
                except StopIteration:
                    instr_name = ""
                if instr_name:
                    layers += [self.layer_delimiter + ' ##%s' % instr_name]
                else:
                    layers += [self.layer_delimiter + ' ##Layer %s' % layer_index]
            layers += [icons]
            
        return layers
