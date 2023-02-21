#import json, re
import os
from skymusic.resources import Resources
from io import BytesIO
from skymusic.parsers import music_theory
from skymusic.modes import InputMode
try:
    import mido
    no_mido_module = False
except (ImportError, ModuleNotFoundError):
    no_mido_module = True

class MidiSongParser:
    """
    For parsing a text format into a Song object
    """

    def __init__(self, maker, silent_warnings=True):
        self.maker = maker
        self.silent_warnings = silent_warnings
        try:
            shape = maker.get_song_parser().get_instrument_type().get_shape()
        except AttributeError:
            shape = None
        self.note_parser = InputMode.MIDI.get_note_parser(shape=shape)
        self.music_theory = music_theory.MusicTheory(self)
        
        root_note = self.note_parser.convert_chromatic_position_into_note_name(0)
        root_note = self.note_parser.english_note_name(root_note)
        self.root_pitch = Resources.MIDI_PITCHES[root_note]
        
        self.layer_delimiter = Resources.DELIMITERS['layer']
        self.icon_delimiter = Resources.DELIMITERS['icon']
        
    def detect_midi(self, song_line, strict=False):
        if isinstance(song_line, (list,tuple)):
            midi_bytes = song_line[0]
        else:
            midi_bytes = song_line
        try:
            if midi_bytes.startswith(b'MThd'):
                return True
            else:
                return False #Non-midi binary file
        except TypeError:
            if not strict and midi_bytes.startswith('MThd'): #Accepting string
                return True
            else:
                return False
        except AttributeError: #Neither string or bytes, skipping
            return False
    
    def extract_note_interval(self, track, min_interval):
        
        times = []
        t = 0
        '''
        for i, msg in enumerate(track):
            try:
                t += msg.time
            except AttributeError:
                pass
            if msg.type == 'note_on':
                t2 = 0
                for msg2 in track[i:]:
                    try:
                        t2 += msg2.time
                    except AttributeError:
                        pass
                    if msg2.type == 'note_off':
                        if msg2.note == msg.note:
                            times.append(t+t2)
                            break
        '''
        i = 0
        for msg in track:
            if i > 128:
                break
            if msg.type == 'note_on':
                if msg.velocity != 0: #reject  silences
                    times.append(t)
                    i += 1
            try:
                t += msg.time
            except AttributeError:
                pass
                
        if len(times) == 0:
            return None
        
        intervals = [interval for interval in self.music_theory.analyze_tempo(times, min_interval) if interval > 2*min_interval]
        
        if len(intervals) > 0:
            note_interval = intervals[0]
        else:
            note_interval = None
            
        return note_interval
    
    def has_notes(self, track):
        
        return any([not msg.is_meta for msg in track])

    def extract_key(self, track):
        
        for msg in track:
            if msg.type == 'key_signature':
                return msg.key
        
        return None
 
    def extract_first_key(self, midi_file):
        
        if midi_file:
            for track in midi_file.tracks:
                track_key = self.extract_key(track)
                if track_key:
                    return track_key
        
        return None

    def extract_copyright(self, midi_file):
        
        copyright = ''
        if midi_file.tracks:
            for msg in midi_file.tracks[0]:
                if msg.type == 'copyright':
                    copyright = msg.text
                    
        return copyright
                                         
                                                            
    def extract_lowest_octave(self, track):
        
        lowest = 128
        for msg in track:
            if msg.type == 'note_on':
                if msg.note < lowest:
                    lowest = msg.note
                    
        lowest_octave = int((lowest - self.root_pitch) / 12)
        
        return lowest_octave

    def parse_track_info(self, track):
        
        track_info = ""
        if track.name:
            track_info += '## Track name: ' + track.name
        
        if self.has_notes(track):
            track_key = self.extract_key(track)
            if track_key:
                track_info += ', musical key= ' + track_key
        
        return track_info
    
    def parse_first_meta(self, midi_file):
        
        metadata = []
        #TODO : extract copyright
        basename = ''
        if midi_file.filename:
            (basename,_) = os.path.splitext(midi_file.filename)
        metadata.append(Resources.DELIMITERS['metadata'] + 'Title:' + basename.capitalize())
        
        artist = self.extract_copyright(midi_file)
        metadata.append(Resources.DELIMITERS['metadata'] + 'Artist: ' + artist)
        metadata.append(Resources.DELIMITERS['metadata'] + 'Transcript writer:' + '')
        
        first_key = self.extract_first_key(midi_file)
        
        if first_key:
            metadata.append(Resources.DELIMITERS['metadata'] + 'Musical key: ' + first_key)
        
        return metadata


    def parse_note_msg(self, note_msg, base_octave):
        
        if note_msg.velocity == 0:
            if note_msg.time == 0:
                return ''
            else:
                return Resources.DELIMITERS['pause']

        octave = int((note_msg.note - self.root_pitch) / 12)
        semi = (note_msg.note - self.root_pitch) % 12
        
        try:
            note = self.note_parser.convert_chromatic_position_into_note_name(semi)
        except KeyError:
            note = Resources.DELIMITERS['broken_harp']
            
        return note + str(octave-base_octave+Resources.PARSING_START_OCTAVE)
    
    def parse_notes(self, track, note_interval):
        
        base_octave = self.extract_lowest_octave(track)
        
        notes = ['']
        t = 0
        prev_t = -note_interval
        prev_prev_t = prev_t
        for msg in track:
            try:
                t += msg.time
            except AttributeError:
                pass
            if msg.type == 'note_on':
                
                dt = t - prev_t
                
                notes += [Resources.DELIMITERS['pause']]*int(dt/note_interval - 1) #parses implicit silences
                
                note = self.parse_note_msg(msg, base_octave)
                
                if note == Resources.DELIMITERS['pause']:
                    if dt > 0.5*note_interval:
                        notes.append(note)
                      
                elif note:
                    
                    if notes[-1] == Resources.DELIMITERS['pause']:
                        if (t - prev_prev_t < note_interval):
                            del(notes[-1])
                        notes.append(note)
                    else:
                        if dt == 0: #chord
                            notes[-1] += note
                        elif (dt <= 0.45*note_interval) and (notes[-1] != Resources.DELIMITERS['pause']):
                            notes[-1] += Resources.DELIMITERS['quaver'] + note
                        else:
                            notes.append(note)
                  
                if note:
                    prev_prev_t = prev_t
                    prev_t = t
                      
        return self.icon_delimiter.join(filter(None,notes))

    def sanitize_midi_lines(self, midi_lines):
        
        try:
            midi_bytes = b''.join(midi_lines)
        except TypeError:
            midi_bytes = ''.join(midi_lines).encode()

        return midi_bytes                                                      

    def create_MidiFile(self, midi_lines):
        
        if no_mido_module:
            print("\n***ERROR: MIDI could not be imported because mido module was not found.")
            return None
        
        midi_bytes = self.sanitize_midi_lines(midi_lines)
        
        buffer = BytesIO()
        buffer.write(midi_bytes)
        buffer.seek(0)
        
        try:
            mid = mido.MidiFile(file=buffer)
        except (IOError, EOFError):
            print("\n***ERROR: mido could not detect your file as being midi.")
            return None
        
        return mid 

    def find_key(self, midi_lines):
        
        mid = self.create_MidiFile(midi_lines)
        song_key = self.extract_first_key(mid)
        
        return [song_key] if song_key else []
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               
    
    def collect_notes(self, midi_lines):
        '''Only used by Music Theory'''
        mid = self.create_MidiFile(midi_lines)
        
        if mid:
            song = []
            for track in mid.tracks:
                for msg in track:
                    if msg.type == 'note_on':
                        note = self.parse_note_msg(msg, 1)
                        if note:
                            song.append(note)
            
            return [self.icon_delimiter.join(song)]
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
    def parse_midi(self, midi_lines):
        
        if no_mido_module: return []
        mid = self.create_MidiFile(midi_lines)
        if not mid: return []
        song = self.parse_first_meta(mid)
        
        for i, track in enumerate(mid.tracks):
            
            track_info = self.parse_track_info(track)
            
            note_interval = self.extract_note_interval(track, 1)
            
            if note_interval is not None:          
                notes = self.parse_notes(track, note_interval)
            else:
                notes = ''
            
            if (track_info and not notes) and len(mid.tracks) > 2:
                song += [self.layer_delimiter]
                
            song += [track_info] + [notes]
            
        song = list(filter(None,song))
        return song
