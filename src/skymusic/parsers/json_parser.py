import json, re
from src.skymusic.resources import Resources
from . import song_parser
from src.skymusic.parsers import music_theory

class JsonSongParser(song_parser.SongParser):
    """
    For parsing a text format into a Song object
    """

    def __init__(self, maker, instrument_type=Resources.DEFAULT_INSTRUMENT, silent_warnings=True):

        super().__init__(maker=maker, silent_warnings=silent_warnings)
        self.skyjson_chord_delay = Resources.SKYJSON_CHORD_DELAY #Delay in ms below which 2 notes are considered a chord
        self.music_theory = music_theory.MusicTheory(self)


    def analyze_tempo(self, times):
        
        def find_barycenter(t, y, i0, di):
           
            while len(t) < 2*di+1:
                di = di - 1
            if di < 0:
                return None
            
            dt = t[1] - t[0]
            tmin = t[0]
            nmax = 10
            
            n = 0
            iG = i0
            iG_old = iG - 10
            while (iG-iG_old) > 1 and n < nmax:            
                i1 = max([0,iG-di])
                i2 = min([len(t),iG+di])
                y_band = y[i1:i2+1]
                t_band = t[i1:i2+1]
                iG_old = iG
                tG = sum([y*t for (t,y) in zip(t_band, y_band)])/sum(y_band)
                iG = round((tG - tmin)/dt)
                n += 1                
            y[i1:i2+1] = [0]*len(y[i1:i2+1])          
            return tG 
        
        diffs = [times[i] - times[i-1] for i in range(1, len(times))]
        
        div_resol = 3
        hbin = self.skyjson_chord_delay / div_resol
        num_slots = 2 + int(max(diffs) / hbin)
        
        y = [0]*num_slots
        t = [i*hbin for i in range(num_slots)]
        
        for diff in diffs: #histogram starting from t=0
            y[1+int(diff/hbin)] += 1
            
        num_peaks = 3
        floor = max(y)/10
         
        tempos = []
        
        for i in range(num_peaks):   
            y0 = max(y)
            if y0 < floor:
                break
            i0 = y.index(y0)
            tG = find_barycenter(t, y, i0, div_resol)       
            tempos.append(tG)
        
        return tempos
        
        
    def load_dict(self, line):

        try:
            try:
                json_dict = json.loads(line)
            except json.JSONDecodeError:
               json_dict = json.loads(re.sub(r'\\{','{',line))

            if isinstance(json_dict, list):
                json_dict = json_dict[0]
        except (json.JSONDecodeError, TypeError, KeyError):
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

        tempos = [tempo for tempo in self.analyze_tempo(times) if tempo > 2*self.skyjson_chord_delay]
        
        if len(tempos) > 0:
            main_tempo = min(tempos)
        else:
            main_tempo = None
                        
        icons = [keys[0]]
        
        for i in range(1,len(times)):
            if times[i] - times[i-1] < self.skyjson_chord_delay:
                icons[-1] += keys[i] # Notes belong to the same chord
            else:
                n_pauses = max([0, round((times[i] - times[i-1])/main_tempo - 1)])
                if n_pauses > 0:
                    icons += [self.pause + (self.repeat_indicator + str(n_pauses) if n_pauses > 1 else '')]
                
                icons += [keys[i]]
        
        return icons
