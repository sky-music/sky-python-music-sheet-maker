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

    def sanitize_lines(self, song_lines, join=False):
        
        song_lines = list(filter(None,map(str.strip, song_lines)))
        if join:
            song_lines = [''.join(song_lines)]
        return song_lines
        
    def detect_json(self, song_lines):
        
        song_lines = self.sanitize_lines(song_lines)
        if song_lines:
            c0 = song_lines[0][0]
            if c0 == '[' or c0 == '{':
                if self.load_dict(''.join(song_lines)):
                    return True
        return False
                             
    def load_dict(self, line):

        try:
            try:
                json_dict = json.loads(line)
            except json.JSONDecodeError:
               json_dict = json.loads(re.sub(r'\\{','{',line))

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
                print("***WARNING: cannot parse an encrypted JSON recording") 
                json_dict = None
        
        return json_dict

    def convert_to_old_format(self, columns, bpm):
        
        layers = {'100':1, '001':2, '010':2, '011':2, '111':3, '110':3, '111':3}
        tempo_changers = [1, 1/2, 1/4, 1/8]
        bpm_ms = int(60000/bpm)
        elapsed_time = 100
        
        songNotes = []
        
        for col in columns:
            songNotes += [{'time':elapsed_time, 'key':str(layers.get(note[1],1))+"Key"+str(note[0])} for note in col[1]]
            elapsed_time += int(bpm_ms*tempo_changers[col[0]])
        
        return songNotes

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

    def split_line(self, line):
        
        json_dict = self.load_dict(line)
        
        if json_dict is None:
            return line
        
        # The existence of this field has already been assessed by MusicTheory
        try:
            notes = json_dict['songNotes']
        except KeyError:
            if 'columns' in json_dict:
                notes = self.convert_to_old_format(json_dict['columns'], json_dict['bpm'])
            elif 'tracks' in json_dict:
                
                notes = self.parse_json_midi(json_dict)
            else:
                raise Exception('JSON file contains an invalid music sheet format.')
        
        times = [note['time'] for note in notes]
        keys = [note['key'] for note in notes]

        # A Special trick to have the same number of digit for all numbers
        # Facilitates the splitting of glued chords into notes
        keys = [self.get_note_parser().sanitize_digits(key) for key in keys]

        note_interval = self.extract_note_interval(times)
        if note_interval is None:
            note_interval = 2*self.skyjson_chord_delay
        
        if not keys: return []
        icons = [keys[0]]
        
        for i in range(1,len(times)):
            if times[i] - times[i-1] < self.skyjson_chord_delay:
                icons[-1] += keys[i] # Notes belong to the same chord
            else:
                n_pauses = max([0, round((times[i] - times[i-1])/note_interval - 1)])
                if n_pauses > 0:
                    icons += [self.pause + (self.repeat_indicator + str(n_pauses) if n_pauses > 1 else '')]
                
                icons += [keys[i]]
        
        return icons
