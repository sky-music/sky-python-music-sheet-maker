import json, re
from skymusic.resources import Resources
from . import song_parser
from skymusic.parsers import music_theory

class JsonSongParser(song_parser.SongParser):
    """
    For parsing a text format into a Song object
    """
    LAYERS_BINMAP = {'100':1, '001':2, '010':2, '011':2, '111':3, '110':3, '111':3,'0000':1, '0010':2, '0110':2, '0100':2, '1010':3, '1000':1, '1110':3, '1100':3, '0001':2,'0011':2, '0111':2,'0101':2, '1011':3, '1001':1, '1111':3, '1101':3}
    JOIN_LAYERS = True

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

    def parse_columns(self, columns, bpm, layer_names=[]):
        
        SILENCE = -1
        MAX_LAYERS = 100
        LAYER_START = 1 #Not 0
        tempo_changers = [1, 1/2, 1/4, 1/8]
        bpm_ms = int(60000/bpm)
        elapsed_time0 = 100
        TEMPO_IDX = 0 #tempo_changer position in column array
        CHORD_IDX = 1 #chord position in column array
        LAYER_IDX = 1 #layer string position in chord array
        NOTE_IDX = 0 #note number position in chord array
        
        #Creates a dictionary of mapping consecutive identical instruments names to the first one
        joint_layers = {}
        if JsonSongParser.JOIN_LAYERS:
            prev_name = ""
            j = 0
            for i, name in enumerate(layer_names):
                if name == prev_name and i>=1:
                    joint_layers[str(i+LAYER_START)] = str(j+LAYER_START)
                else:
                    j = i
                prev_name = name
        
        
        layered_notes = {}
 
        #Detects layer format: hex string or binary string
        #the loops ensure that we process non empty items
        for col in columns:
            if col[CHORD_IDX]:
                for note in col[CHORD_IDX]:
                    try:
                        self.LAYERS_BINMAP[note[LAYER_IDX]]
                        is_hex = False
                    except KeyError:
                        is_hex = True
                    break
        
        layers = {str(k):[] for k in range(LAYER_START,MAX_LAYERS-LAYER_START)} # Layers start at 1 in SkyStudio and Specy's SkyMusic
        #layers = {"1": [1,[6,11]], "2": [3,6,9], ...}

        #JSON structure:
        #column = [tempo_changer, chord]
        #chord = [note, note, note]
        #note = [index, "layer"]
            
        for col in columns:
            tempo_changer = tempo_changers[col[TEMPO_IDX]]
            
            if not col[CHORD_IDX]: #no notes
                for layer in layers: layers[layer].append([SILENCE])
            else:
                visited_layers = set()
                for i, note in enumerate(col[CHORD_IDX]):          
                    layer = str(int('0x'+note[LAYER_IDX],16)) if is_hex else layers.get(note[LAYER_IDX],1)              
                    
                    if layer in joint_layers: layer = joint_layers[layer]
                    
                    if layer in visited_layers:
                        layers[layer][-1].append(note[NOTE_IDX]) #Continues last chord
                    else:
                        layers[layer].append([note[NOTE_IDX]]) #Creates a chords
                    visited_layers.update(layer)

        #old format is 3Key4, 2Key14
        #Layers numbers start at LAYER_START=1
        #Notes start at 0
        #So first layer, first note is 1Key0
        for layer, chords in layers.items():
            elapsed_time = elapsed_time0
            note_dicts = []
            for chord in chords:
                for note in chord:
                    if note != SILENCE:
                        note_dicts += [{'time':elapsed_time, 'key':str(layer if is_hex else self.LAYERS_BINMAP[layer])+"Key"+str(note)}]
                elapsed_time += round(bpm_ms*tempo_changer) #Increment time at next chord
            
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

    def parse_recorded(self, notes):
        layered_notes = {}
        if not notes: return layered_notes
        try:
            layer = self.LAYERS_BINMAP[notes[0][2]]
            is_hex = False
        except KeyError:
            layer = int('0x'+notes[0][2],16)
            is_hex = True
        
        note_dicts = []
        for note in notes:
            note_dicts += [{'time':note[1], 'key':str(layer)+"Key"+str(note[0])}]
        
        layered_notes[layer] = note_dicts
        
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
        instr_names = [instr.get("name","") for instr in instruments]
        
        if 'columns' in json_dict:
            layered_notes = self.parse_columns(json_dict['columns'], bpm, instr_names)
        elif 'notes' in json_dict:
            layered_notes = self.parse_recorded(json_dict['notes'])
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
            
            instr_names = iter(instr_names)
            last_name = ""
            instr_name = last_name
            if layered_notes:
                try:
                    if JsonSongParser.JOIN_LAYERS:
                        while instr_name == last_name: instr_name = next(instr_names)
                        last_name = instr_name
                    else:
                        instr_name = next(instr_names)
                except StopIteration:
                    instr_name = ""
                if instr_name:
                    layers += [self.layer_delimiter + ' ##%s' % instr_name]
                else:
                    layers += [self.layer_delimiter + ' ##Layer %s' % layer_index]
            layers += [icons]
            
        return layers
