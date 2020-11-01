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


    def parse_metadata(self, line, song):
        
        json_dict = self.load_dict(line)
        changed = False
        
        meta_data = {}
        
        try:
            meta_data['title'] = json_dict['name']
            meta_data['artist'] = json_dict['author']
            meta_data['transcript'] = ', '.join(filter(None,[json_dict['arrangedBy'], json_dict['transcribedBy']]))
            meta_data['song_key'] = json_dict['pitchLevel']
            changed = True
        except KeyError:
            changed = False
        
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
        notes = json_dict['songNotes']
        
        times = [note['time'] for note in notes]
        keys = [note['key'] for note in notes]

        # A Special trick to have the same number of digit for all numbers
        # Facilitates the splitting of glued chords into notes
        keys = [self.get_note_parser().sanitize_digits(key) for key in keys]

        note_interval = self.extract_note_interval(times)
        if note_interval is None:
            note_interval = 2*self.skyjson_chord_delay
                        
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
