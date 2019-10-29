#!/usr/bin/env python3
from textwrap import wrap
import re
import os
from modes import InputMode
from instruments import Harp, Voice


### Parser

class Parser:

    def __init__(self):
        
        if (os.getenv('LANG') == 'fr') or (os.getenv('LANG') == 'be'):
            self.keyboard_position_map = {'A': (0, 0), 'Z': (0, 1), 'E': (0, 2), 'R': (0, 3), 'T': (0, 4), 'Q': (1, 0), 'S': (1, 1), 'D': (1, 2), 'F': (1, 3), 'G': (1, 4), 'W': (2, 0), 'X': (2, 1), 'C': (2, 2), 'V': (2, 3), 'B': (2, 4)}
            self.keyboard_layout="AZERT QSDFG WXCVB"
        else:
            self.keyboard_position_map = {'Q': (0, 0), 'W': (0, 1), 'E': (0, 2), 'R': (0, 3), 'T': (0, 4), 'A': (1, 0), 'S': (1, 1), 'D': (1, 2), 'F': (1, 3), 'G': (1, 4), 'Z': (2, 0), 'X': (2, 1), 'C': (2, 2), 'V': (2, 3), 'B': (2, 4)}
            self.keyboard_layout="QWERT ASDFG ZXCVB"
        self.sky_position_map = {
                'A1': (0, 0), 'A2': (0, 1), 'A3': (0, 2), 'A4': (0, 3), 'A5': (0, 4),
                'B1': (1, 0), 'B2': (1, 1), 'B3': (1, 2), 'B4': (1, 3), 'B5': (1, 4),
                'C1': (2, 0), 'C2': (2, 1), 'C3': (2, 2), 'C4': (2, 3), 'C5': (2, 4)
                }
        self.western_position_map = {
                'F0': (-4, 0), 'G0': (-4, 1), 'A0': (-4, 2), 'B0': (-4, 3), 'C1': (-4, 4),
                'D1': (-4, 0), 'E1': (-4, 1), 'F1': (-4, 2), 'G1': (-4, 3), 'A1': (-4, 4),
                'B1': (-3, 0), 'C2': (-3, 1), 'D2': (-3, 2), 'E2': (-3, 3), 'F2': (-3, 4),
                'G2': (-2, 0), 'A2': (-2, 1), 'B2': (-2, 2), 'C3': (-2, 3), 'D3': (-2, 4),
                'E3': (-1, 0), 'F3': (-1, 1), 'G3': (-1, 2), 'A3': (-1, 3), 'B3': (-1, 4),
                'C4': (0, 0), 'D4': (0, 1), 'E4': (0, 2), 'F4': (0, 3), 'G4': (0, 4),
                'A4': (1, 0), 'B4': (1, 1), 'C5': (1, 2), 'D5': (1, 3), 'E5': (1, 4),
                'F5': (2, 0), 'G5': (2, 1), 'A5': (2, 2), 'B5': (2, 3), 'C6': (2, 4),
                'D6': (3, 0), 'E6': (3, 1), 'F6': (3, 2), 'G6': (3, 3), 'A6': (3, 4),
                'B6': (4, 0), 'C7': (4, 1), 'D7': (4, 2), 'E7': (4, 3), 'F7': (4, 4)
                }
        self.jianpu_position_map = {
                '2---': (-4, 0), '3---': (-4, 1), '4---': (-4, 2), '5---': (-4, 3), '6---': (-4, 4),
                '7---': (-3, 0), '1--': (-3, 1), '2--': (-3, 2), '3--': (-3, 3), '4--': (-3, 4),
                '5--': (-2, 0), '6--': (-2, 1), '7--': (-2, 2), '1-': (-2, 3), '2-': (-2, 4),
                '3-': (-1, 0), '4-': (-1, 1), '5-': (-1, 2), '6-': (-1, 3), '7-': (-1, 4),
                '1': (0, 0), '2': (0, 1), '3': (0, 2), '4': (0, 3), '5': (0, 4),
                '6': (1, 0), '7': (1, 1), '1+': (1, 2), '2+': (1, 3), '3+': (1, 4),
                '4+': (2, 0), '5+': (2, 1), '6+': (2, 2), '7+': (2, 3), '1++': (2, 4),
                '2++': (3, 0), '3++': (3, 1), '4++': (3, 2), '5++': (3, 3), '6++': (3, 4),
                '7++': (4, 0), '1+++': (4, 1), '2+++': (4, 2), '3+++': (4, 3), '4+++': (4, 4)
                }
        self.Cmajor = [['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'],
                      ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']]   
        self.onemajor = [['1', '2b', '2', '3b', '3', '4', '5b', '5', '6b', '6', '7b', '7'],
                      ['1', '1#', '2', '2#', '3', '4', '4#', '5', '5#', '6', '6#', '7']]  
        self.intervals = [0, 2, 4, 5, 7, 9, 11]
        
        self.jianpu2western_map = {
                '1': 'C', '2' : 'D', '3': 'E', '4': 'F', '5': 'G', '6': 'A', '7': 'B', 
                'C':'C', 'D':'D', 'E':'E', 'F':'F', 'G':'G', 'A':'A', 'B':'B'
                }
        
    def get_westernkeys(self):
        return self.Cmajor
    
    def get_jianpukeys(self):
        return self.onemajor

    def get_intervals(self):
        return self.intervals

    def get_keyboard_position_map(self):
        return self.keyboard_position_map

    def get_sky_position_map(self):
        return self.sky_position_map

    def get_western_position_map(self):
        return self.western_position_map
    
    def get_jianpu_position_map(self):
        return self.jianpu_position_map

    def jianpu2western(self,notes):
         try:
            return [self.jianpu2western_map[note] for note in notes]
         except KeyError:
            return notes
    
    def find_key(self, song_lines, comment_delimiter='#', input_mode=InputMode.WESTERNFILE):
        '''
        Finds musical key from notes in a song file
        '''               
        if input_mode in [InputMode.WESTERNFILE, InputMode.WESTERN]:    
            scale = self.get_westernkeys().copy()
            isNoteRegExp = '([A-G])'
            notNoteRegExp = '[^A-Gb#]'
        elif input_mode in [InputMode.JIANPUFILE, InputMode.JIANPU]: 
            scale = self.get_jianpukeys().copy()
            isNoteRegExp = '([1-7])'  
            notNoteRegExp = '[^1-7b#]'
        else:
            return ['']
        indices = self.get_intervals()
        possible_keys = scale[0].copy()       
                                                   
        for line in song_lines: 
            if len(line)>0 and any([key!='' for key in possible_keys]):
                if line[0] != comment_delimiter:     
                    notes = re.sub(isNoteRegExp,' \\1',re.sub(notNoteRegExp,'',line)).split() # Clean-up, adds space and split
                    for i in range(len(possible_keys)):
                        if possible_keys[i]!='':
                            key_scale = [[scale[0][j] for j in indices], [scale[1][j] for j in indices]]
                            if not all([(note in key_scale[0]) or (note in key_scale[1]) for note in notes]):
                                possible_keys[i]=''
                        scale[0] = scale[0][1::] + scale[0][:1:] # circ shift
                        scale[1] = scale[1][1::] + scale[1][:1:] # circ shift

        possible_keys = [key for key in possible_keys if key != ''] # return reduced set of possible keys
        return self.jianpu2western(possible_keys)
                       
    def parse_icon(self, icon, delimiter, input_mode):
        return icon.split(delimiter)
    
    def parse_line(self, line, icon_delimiter=' ', blank_icon='.', quaver_delimiter='-', comment_delimiter='#', input_mode=0, note_shift=0):
        '''
        Returns instrument_line: a list of chord 'skygrid' (1 chord = 1 dict)
        ''' 
        instrument_line = []
        line = line.rstrip().lstrip().replace(icon_delimiter+icon_delimiter,icon_delimiter) # clean-up
        if len(line)>0:
            if line[0] == comment_delimiter:
                lyrics = line.split(comment_delimiter)
                for lyric in lyrics:
                    if len(lyric)>0:
                        voice = Voice()
                        voice.set_chord_skygrid(lyric.rstrip().lstrip())
                        instrument_line.append(voice)
            else:
                icons=line.split(icon_delimiter)
                 #TODO: Implement logic for parsing line vs single icon.        
                for icon in icons:
                    chords = self.parse_icon(icon, quaver_delimiter, input_mode)
                    results = self.parse_chords(chords, blank_icon, input_mode, note_shift)
                    chord_skygrid = results[0]
                    harp_is_highlighted = results[1]
                    repeat = results[2]
        
                    harp = Harp()
                    harp.set_repeat(repeat)
                    harp.set_is_highlighted(harp_is_highlighted)
                    harp.set_chord_skygrid(chord_skygrid)
        
                    instrument_line.append(harp)

        return instrument_line

    def map_note_to_position(self, note, blank_icon='.', input_mode=0, note_shift=0):
        '''
        Returns a tuple containing the row index and the column index of the note's position.
        '''
        if input_mode == InputMode.SKYKEYBOARD:
            position_map = self.get_keyboard_position_map()
        elif input_mode == InputMode.SKY or input_mode == InputMode.SKYFILE:
            position_map = self.get_sky_position_map()
        elif input_mode == InputMode.WESTERN or input_mode == InputMode.WESTERNFILE:
            position_map = self.get_western_position_map()
        elif input_mode == InputMode.JIANPU or input_mode == InputMode.JIANPUFILE:
            position_map = self.get_jianpu_position_map()
        else:
            position_map = self.get_keyboard_position_map()
        note = note.upper()
               
        if note in position_map.keys():           
            pos=position_map[note] #tuple
            idx=pos[0]*5+pos[1]
            idxshift=idx+note_shift
            pos=(int(idxshift/5),idxshift-5*int(idxshift/5))
            if pos>=(0,0) and pos<=(2,4):
                return pos
            else:
                raise KeyError
        #elif letter == BLANK_ICON:
        #    print(letter)
        #    raise BlankIconError
        elif note == blank_icon:
            #TODO: Implement support for breaks/empty harps
            #Define a custom InvalidLetterException
            raise KeyError
        else:
            raise KeyError

    def parse_chords(self, chords, blank_icon='.', input_mode=0, note_shift=0):
        
        is_empty = True
        chord_skygrid = {}
        for chord_idx, chord in enumerate(chords):
            # Create a skygrid of the harp's chords
            # For each chord, set the highlighted state of each note accordingly (whether True or False)
            try:
                repeat = int(re.split('x', chord)[1])
                chord = re.split('x', chord)[0]
            except:
                repeat = 0    
            
            if input_mode in [InputMode.SKY, InputMode.SKYFILE, InputMode.WESTERN, InputMode.WESTERNFILE]:
                chord = re.sub('([A-G])', ' \\1', chord).split()
            if input_mode in [InputMode.JIANPU, InputMode.JIANPUFILE]:
                chord = re.sub('([1-9])', ' \\1', chord).split()  #Adds space before note and then split            
            for note in chord: # Chord is a list of notes
                #Except InvalidLetterException
                try:
                    highlighted_note_position = self.map_note_to_position(note, blank_icon, input_mode, note_shift)
                except KeyError:
                    pass
                else:
                    is_empty = False
                    chord_skygrid[highlighted_note_position] = {}
                    chord_skygrid[highlighted_note_position][chord_idx] = True

        results = [chord_skygrid, not(is_empty), repeat]
        return results

