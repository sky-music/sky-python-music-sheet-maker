#import json, re
import os
from skymusic.resources import Resources
#from . import song_parser
from io import BytesIO
from mido import MidiFile
from skymusic.parsers import music_theory

class MidiSongParser:
    """
    For parsing a text format into a Song object
    """

    def __init__(self):
        from skymusic.parsers.noteparsers.english import English
        self.music_theory = music_theory.MusicTheory(self)
        self.inverse_map = English().INVERSE_CHROMATIC_SCALE_DICT
    
    def detect_midi(self, song_line, strict=False):
        if isinstance(song_line, (list,tuple)):
            midi_bytes = song_line[0]
        else:
            midi_bytes = song_line
        try:
            if midi_bytes.startswith(b'MThd'):
                return True
            else:
                if not strict and midi_bytes.startswith('MThd'):
                    return True
                else:
                    return False
        except (AttributeError, TypeError):
            return False
    
    def parse_meta(self, track):
        
        metadata = []
        if track.name:
            metadata.append('Track name:' + track.name)
        for msg in track:
            if msg.type == 'key_signature':
                metadata.append(Resources.METADATA_DELIMITER + 'Track key: ' + msg.key)
        
        return '\n'.join(metadata)
    
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
        
        for msg in track:
            if msg.type == 'note_on':
                if msg.velocity != 0: #reject  silences
                    times.append(t)
            try:
                t += msg.time
            except AttributeError:
                pass
                
        if len(times) == 0:
            return None
        
        #print('%%note_on DIFFS')
        #diffs = [times[i] - times[i-1] for i in range(1, len(times))]
        #print(diffs)
        
        intervals = [interval for interval in self.music_theory.analyze_tempo(times, min_interval) if interval > 2*min_interval]
        
        if len(intervals) > 0:
            note_interval = intervals[0]
        else:
            note_interval = None
            
        return note_interval
    

    def extract_key(self, track):
        
        keys = [msg for msg in track if msg.type == 'key_signature']
        if keys:
            return keys[0].key
        else:
            return None
 
    def extract_first_key(self, midi_file):
        
        for track in midi_file.tracks:
            track_key = self.extract_key(track)
            if track_key:
                return track_key
        
        return None
                    
    def extract_lowest_octave(self, track):
        
        lowest = 128
        for msg in track:
            if msg.type == 'note_on':
                if msg.note < lowest:
                    lowest = msg.note
                    
        root_pitch = Resources.MIDI_PITCHES['C']
        lowest_octave = int((lowest - root_pitch) / 12)
        
        return lowest_octave

    def parse_note_msg(self, note_msg, base_octave):
        
        if note_msg.velocity == 0:
            if note_msg.time == 0:
                return ''
            else:
                return Resources.PAUSE

        root_pitch = Resources.MIDI_PITCHES['C']
        octave = int((note_msg.note - root_pitch) / 12)
        semi = (note_msg.note - root_pitch) % 12
        
        try:
            note = self.inverse_map[semi]
        except KeyError:
            note = Resources.BROKEN_HARP
            
        return note + str(octave-base_octave+Resources.PARSING_START_OCTAVE)
    
    def parse_notes(self, track, note_interval):
        
        base_octave = self.extract_lowest_octave(track)
        
        notes = []
        t = 0
        prev_t = -note_interval
        for msg in track:
            try:
                t += msg.time
            except AttributeError:
                pass
            if msg.type == 'note_on':
                
                dt = t - prev_t
                prev_t = t
                
                notes += [Resources.PAUSE]*int(dt/note_interval - 1) #parses implicit silences
                
                note = self.parse_note_msg(msg, base_octave)
                
                print(msg)
                print(f"dt={dt:.1f}, note={note}\n")  
                
                if note == Resources.PAUSE:
                    if dt > 0.5*note_interval:
                        notes.append(note)
                        
                elif note:
                    if dt == 0: #chord
                        notes[-1] += note
                    elif (dt <= 0.5*note_interval) and (notes[-1] != Resources.PAUSE):
                        notes[-1] += Resources.QUAVER_DELIMITER + note
                    else:
                        notes.append(note)
                
        return ' '.join(notes)                

    def sanitize_midi_lines(self, midi_lines):
        
        try:
            midi_bytes = b''.join(midi_lines)
        except TypeError:
            midi_bytes = ''.join(midi_lines).encode()

        return midi_bytes                                                      

    def create_MidiFile(self, midi_lines):
        
        midi_bytes = self.sanitize_midi_lines(midi_lines)
        
        buffer = BytesIO()
        buffer.write(midi_bytes)
        buffer.seek(0)
        mid = MidiFile(file=buffer)
        
        return mid 

    def get_song_key(self, midi_lines):
        
        mid = self.create_MidiFile(midi_lines)
        
        first_key = self.extract_first_key(mid)
        
        first_key = 'C' #DEBUG TODO
        
        return first_key                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
    def parse_midi(self, midi_lines):
        
        mid = self.create_MidiFile(midi_lines)
        
        song = ''
        song_key = self.extract_first_key(mid)
        
        if song_key:
            song += Resources.METADATA_DELIMITER + song_key + '\n'
        
        for i, track in enumerate(mid.tracks):
            
            metadata = self.parse_meta(track)
            
            note_interval = self.extract_note_interval(track, 1)
            
            if note_interval is not None:          
                notes = self.parse_notes(track, note_interval)
            else:
                notes = ''
         
            song += '\n'.join(filter(None,[metadata, notes])) + '\n'
            
        song = song.strip().split(os.linesep)
        print('%%%DEBUG')
        print(song)
        return song
