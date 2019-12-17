#!/usr/bin/env python3
import re
import os
from modes import InputModes
import instruments
from operator import truediv, itemgetter


### Parser

class Parser:

    def __init__(self):

        self.columns = 5
        self.lines = 3

        if (os.getenv('LANG') == 'fr') or (os.getenv('LANG') == 'be'):
            self.keyboard_position_map = {'.': (-1, -1), 'A': (0, 0), 'Z': (0, 1), 'E': (0, 2), 'R': (0, 3), 'T': (0, 4), 'Q': (1, 0), 'S': (1, 1), 'D': (1, 2), 'F': (1, 3), 'G': (1, 4), 'W': (2, 0), 'X': (2, 1), 'C': (2, 2), 'V': (2, 3), 'B': (2, 4)}
            self.keyboard_layout="AZERT QSDFG WXCVB"
        else:
            self.keyboard_position_map = {'.': (-1, -1), 'Q': (0, 0), 'W': (0, 1), 'E': (0, 2), 'R': (0, 3), 'T': (0, 4), 'A': (1, 0), 'S': (1, 1), 'D': (1, 2), 'F': (1, 3), 'G': (1, 4), 'Z': (2, 0), 'X': (2, 1), 'C': (2, 2), 'V': (2, 3), 'B': (2, 4)}
            self.keyboard_layout="QWERT ASDFG ZXCVB"
        self.sky_position_map = {
                '.': (-1, -1),
                'A1': (0, 0), 'A2': (0, 1), 'A3': (0, 2), 'A4': (0, 3), 'A5': (0, 4),
                'B1': (1, 0), 'B2': (1, 1), 'B3': (1, 2), 'B4': (1, 3), 'B5': (1, 4),
                'C1': (2, 0), 'C2': (2, 1), 'C3': (2, 2), 'C4': (2, 3), 'C5': (2, 4)
                }
        self.western_position_map = {
                '.': (-1, -1),
                'F0': (-5, 0), 'G0': (-5, 1), 'A0': (-5, 2), 'B0': (-5, 3), 'C1': (-5, 4),
                'D1': (-4, 0), 'E1': (-4, 1), 'F1': (-4, 2), 'G1': (-4, 3), 'A1': (-4, 4),
                'B1': (-3, 0), 'C2': (-3, 1), 'D2': (-3, 2), 'E2': (-3, 3), 'F2': (-3, 4),
                'G2': (-2, 0), 'A2': (-2, 1), 'B2': (-2, 2), 'C3': (-2, 3), 'D3': (-2, 4),
                'E3': (-1, 0), 'F3': (-1, 1), 'G3': (-1, 2), 'A3': (-1, 3), 'B3': (-1, 4),
                'C4': (0, 0), 'D4': (0, 1), 'E4': (0, 2), 'F4': (0, 3), 'G4': (0, 4),
                'A4': (1, 0), 'B4': (1, 1), 'C5': (1, 2), 'D5': (1, 3), 'E5': (1, 4),
                'F5': (2, 0), 'G5': (2, 1), 'A5': (2, 2), 'B5': (2, 3), 'C6': (2, 4),
                'D6': (3, 0), 'E6': (3, 1), 'F6': (3, 2), 'G6': (3, 3), 'A6': (3, 4),
                'B6': (4, 0), 'C7': (4, 1), 'D7': (4, 2), 'E7': (4, 3), 'F7': (4, 4),
                'C': (0, 0), 'D': (0, 1), 'E': (0, 2), 'F': (0, 3), 'G': (0, 4),
                'A': (1, 0), 'B': (1, 1),
                'FA0': (-5, 0), 'SOL0': (-5, 1), 'LA0': (-5, 2), 'SI0': (-5, 3), 'DO1': (-5, 4),
                'RE1': (-4, 0), 'MI1': (-4, 1), 'FA1': (-4, 2), 'SOL1': (-4, 3), 'LA1': (-4, 4),
                'SI1': (-3, 0), 'DO2': (-3, 1), 'RE2': (-3, 2), 'MI2': (-3, 3), 'FA2': (-3, 4),
                'SOL2': (-2, 0), 'LA2': (-2, 1), 'SI2': (-2, 2), 'DO3': (-2, 3), 'RE3': (-2, 4),
                'MI3': (-1, 0), 'FA3': (-1, 1), 'SOL3': (-1, 2), 'LA3': (-1, 3), 'SI3': (-1, 4),
                'DO4': (0, 0), 'RE4': (0, 1), 'MI4': (0, 2), 'FA4': (0, 3), 'SOL4': (0, 4),
                'LA4': (1, 0), 'SI4': (1, 1), 'DO5': (1, 2), 'RE5': (1, 3), 'MI5': (1, 4),
                'FA5': (2, 0), 'SOL5': (2, 1), 'LA5': (2, 2), 'SI5': (2, 3), 'DO6': (2, 4),
                'RE6': (3, 0), 'MI6': (3, 1), 'FA6': (3, 2), 'SOL6': (3, 3), 'LA6': (3, 4),
                'SI6': (4, 0), 'DO7': (4, 1), 'RE7': (4, 2), 'MI7': (4, 3), 'FA7': (4, 4),
                'DO': (0, 0), 'RE': (0, 1), 'MI': (0, 2), 'FA': (0, 3), 'SOL': (0, 4),
                'LA': (1, 0), 'SI': (1, 1)
                }
        self.jianpu_position_map = {
                '.': (-1, -1),
                '4----': (-5, 0), '5----': (-5, 1), '6----': (-5, 2), '7----': (-5, 3), '1---': (-5, 4),
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

        self.western_chords = {
                'C':'C4E4G4', 'D':'D4A4', 'F':'F4A4C5', 'G':'G4B4D5', 'Dm':'D4F4A4', 'Em':'E4G4B4',
                'Am':'A4C5E5', 'Bm':'B4D5', 'Bdim':'B4D5F5', 'A+':'A4C5F5', 'Csus2':'C4D4G4',
                'Dsus2':'C4E4A4', 'Fsus2':'F4G4C5', 'Gsus2':'G4A4D5', 'Asus2':'A4B4E5',
                'Csus4':'C4F4G4', 'Dsus4':'D4G4A4', 'Esus4':'E4A4B4', 'Gsus4':'G4C5D5',
                'Asus4':'A4D5E5', 'D7sus4':'D4G4A4C5', 'E7sus4':'E4A4B4D5', 'G7sus4':'G4C5D5F5',
                'A7sus4':'A4D5E5G5', 'C6':'C4E4G4A4', 'F6':'F4A4C5D5', 'G6':'G4B4D5E5', 'G7':'G4B4D5F5',
                'G9':'G4B4D5F5A5', 'Cmaj7':'C4E4G4B4', 'Fmaj7':'F4A4C5E5', 'Cmaj9':'C4E4G4D5',
                'Fmaj9':'F4A4C5E5G5', 'Cmaj11':'C4E4G4D5F5', 'Dm6':'D4F4A4B4', 'Dm7':'D4F4A4C5',
                'Em7':'E4G4B4D5', 'Am7':'A4C5E5G5', 'Dm9':'D4F4A4C5E5', 'Am9':'A4C5E5G5B5',
                'Dm11':'D4F4A4C5E5G5', 'Am11':'D4A4C5E5G5B5', 'Cmaj':'C4E4G4', 'Dmaj':'D4A4', 'Fmaj':'F4A4C5',
                'Gmaj':'G4B4D5', 'Aaug':'A4C5F5', 'Csus':'C4F4G4', 'Dsus':'D4G4A4', 'Esus':'E4A4B4', 'Gsus':'G4C5D5',
                'Asus':'A4D5E5', 'D7sus':'D4G4A4C5', 'E7sus':'E4A4B4D5', 'G7sus':'G4C5D5F5', 'A7sus':'A4D5E5G5'
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

    def get_keyboard_layout(self):
        return self.keyboard_layout
    
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

    def parse_icon(self, icon, delimiter):
        return icon.split(delimiter)

    def decode_chord(self, chord, chord_map):
        try:
            return chord_map[chord]
        except:
            return chord


    def split_chord(self, chord, position_map, repeat_indicator):

        try:
            repeat = int(re.split(re.escape(repeat_indicator), chord)[1])
            chord = re.split(re.escape(repeat_indicator), chord)[0]
        except:
            repeat = 1

        chord = chord.upper()

        if position_map in [self.sky_position_map, self.western_position_map]:
            chord = re.sub('([A-G])', ' \\1', chord).split()
        elif position_map  == self.jianpu_position_map:
            chord = re.sub('([1-9])', ' \\1', chord).split()  #Adds space before note and then split
        elif self.sky_position_map == self.keyboard_position_map:
            chord = re.sub('([' + self.keyboard_layout.replace(' ','') + '])', ' \\1', chord).split()

        return repeat, chord


    def detect_input_type(self, song_lines, icon_delimiter=' ', pause='.', quaver_delimiter='-', comment_delimiter='#', repeat_indicator='*'):
        '''
        Attempts to detect input type and notation
        '''
        possible_modes = [InputModes.SKYKEYBOARD, InputModes.SKY, InputModes.WESTERN, InputModes.JIANPU, InputModes.WESTERNCHORDS]
        position_maps = [self.keyboard_position_map, self.sky_position_map, self.western_position_map, self.jianpu_position_map, self.western_chords]
        good_notes = [0]*len(position_maps)
        num_notes = [0]*len(position_maps)
        DEFG_notes = 0
        octave_span = 0

        for line in song_lines:
            line = line.strip()
            line = re.sub(re.escape(icon_delimiter)+'{2,'+str(max(2,len(line)))+'}',icon_delimiter,line)#removes surnumerous spaces
            if len(line) > 0:
                if line[0] != comment_delimiter:
                    icons=line.split(icon_delimiter)
                    for icon in icons:
                        chords = self.parse_icon(icon, quaver_delimiter)
                        for chord in chords:
                            for idx, position_map in enumerate(position_maps):
                                if position_map == self.western_chords:
                                    notes = [chord] #Because abbreviated chord names are not composed of note names
                                else:
                                    repeat, notes = self.split_chord(chord, position_map, repeat_indicator)
                                #TODO: use self.map_note_to_position?
                                good_notes[idx] += sum([int(note in position_map.keys()) for note in notes])
                                num_notes[idx] += len(notes)
                                if position_map == self.western_position_map:
                                    DEFG_notes += sum([int(re.search('[D-G]',note) != None) for note in notes])
                                    octaves = [re.search('\d',note) for note in notes]
                                    octaves = sorted([int(octave.group(0)) for octave in octaves if octave != None])
                                    if len(octaves)>0:
                                        octave_span = max(octave_span, octaves[-1] - octaves[0] + 1)

        num_notes = [1 if x == 0 else x for x in num_notes] #Removes zeros to avoid division by zero

        ratios = list(map(truediv, good_notes, num_notes))
        DEFG_notes /= num_notes[possible_modes.index(InputModes.WESTERN)]
        if ((DEFG_notes == 0) or (DEFG_notes < 0.01 and octave_span > 2)) and (num_notes[possible_modes.index(InputModes.WESTERN)] > 10):
            ratios[possible_modes.index(InputModes.WESTERN)] *= 0.5
        sorted_inds, sorted_ratios = zip(*sorted([(i,e) for i,e in enumerate(ratios)], key=itemgetter(1), reverse=True))
        if sorted_ratios[0] == 1 and sorted_ratios[1] < 1:
            return [possible_modes[sorted_inds[0]]]
        elif (sorted_ratios[0] > 0.9):
            sorted_ratios = list(map(truediv, sorted_ratios, [max(sorted_ratios)]*len(sorted_ratios)))
            if sorted_ratios[1] < 0.9:
                return [possible_modes[sorted_inds[0]]]
            else:
                return possible_modes
        else:
            return possible_modes


    def find_key(self, song_lines, comment_delimiter='#', input_mode=InputModes.SKY):
        '''
        Finds musical key from notes in a song file
        '''
        if input_mode == InputModes.WESTERN:
            scale = self.get_westernkeys().copy()
            isNoteRegExp = '([A-G])'
            notNoteRegExp = '[^A-Gb#]'
        elif input_mode == InputModes.JIANPU:
            scale = self.get_jianpukeys().copy()
            isNoteRegExp = '([1-7])'
            notNoteRegExp = '[^1-7b#]'
        else:
            return ['']
        indices = self.get_intervals()
        possible_keys = scale[0].copy()

        for line in song_lines:
            if len(line)>0 and any([musickey!='' for musickey in possible_keys]):
                if line[0] != comment_delimiter:
                    notes = re.sub(isNoteRegExp,' \\1',re.sub(notNoteRegExp,'',line)).split() # Clean-up, adds space and split
                    for key_idx, musickey in enumerate(possible_keys):
                        if musickey!='':
                            key_scale = [[scale[0][j] for j in indices], [scale[1][j] for j in indices]]
                            if not all([(note in key_scale[0]) or (note in key_scale[1]) for note in notes]):
                                possible_keys[key_idx]=''
                        scale[0] = scale[0][1::] + scale[0][:1:] # circ shift
                        scale[1] = scale[1][1::] + scale[1][:1:] # circ shift

        possible_keys = [musickey for musickey in possible_keys if musickey != ''] # return reduced set of possible keys
        return self.jianpu2western(possible_keys)


    def parse_line(self, line, icon_delimiter=' ', pause='.', quaver_delimiter='-', comment_delimiter='#', input_mode=InputModes.SKY, note_shift=0, repeat_indicator='*'):
        '''
        Returns instrument_line: a list of chord 'skygrid' (1 chord = 1 dict)
        '''
        instrument_line = []
        line = line.strip()
        line = re.sub(re.escape(icon_delimiter)+'{2,'+str(max(2,len(line)))+'}',icon_delimiter,line)#removes surnumerous spaces
        if len(line)>0:
            if line[0] == comment_delimiter:
                lyrics = line.split(comment_delimiter)
                for lyric in lyrics:
                    if len(lyric)>0:
                        voice = instruments.Voice()
                        voice.set_lyric(lyric.strip())
                        instrument_line.append(voice)
            else:
                icons=line.split(icon_delimiter)
                 #TODO: Implement logic for parsing line vs single icon.
                for icon in icons:
                    chords = self.parse_icon(icon, quaver_delimiter)
                    #From here, real chords are still glued, quavers have been split in different list slots
                    chord_skygrid, harp_broken, harp_silent, repeat = self.parse_chords(chords, pause, input_mode, note_shift, repeat_indicator)
                    harp = instruments.Harp()
                    harp.set_repeat(repeat)
                    harp.set_is_silent(harp_silent)
                    harp.set_is_broken(harp_broken)
                    harp.set_chord_skygrid(chord_skygrid)

                    instrument_line.append(harp)

        return instrument_line

    def map_note_to_position(self, note, position_map, note_shift=0):
        '''
        Returns a tuple containing the row index and the column index of the note's position.
        '''
        note = note.upper()

        if note in position_map.keys(): # Note Shift (ie transposition in Sky)
            pos=position_map[note] #tuple
            if (pos[0] < 0) and (pos[1] < 0): #Special character
                return pos
            else:
                idx = pos[0]*self.columns+pos[1]
                idx = idx+note_shift
                pos = (int(idx/self.columns), idx-self.columns*int(idx/self.columns))
                if pos>=(0,0) and pos<=(2,4):
                    return pos
                else:
                    raise KeyError
        else:
            raise KeyError

    def parse_chords(self, chords, pause='.', input_mode=InputModes.SKY, note_shift=0, repeat_indicator='*'):
        #Individual note is a single-element list: chords=['A5']
        #Real chord is a single element list: chords=['B1A1A3']
        #Triplets and quavers are a list of notes or chords: chords=['B2', 'B3B1', 'B4', 'B5', 'C1', 'C2']
        harp_broken = True
        chord_skygrid = {}

        #print(chord)
        if len(chords)>1:
            idx0 = 1 #Notes in quavers and triplets have a frame index >1
        else:
            idx0 = 0 #Single note or note in chord jas a frame index ==0

        for chord_idx, chord in enumerate(chords):
            # Create a skygrid of the harp's chords
            # For each chord, set the highlighted state of each note accordingly (whether True or False)
            chord = re.sub(re.escape(pause), '.', chord) #Replaces the pause character by the default

            if input_mode == InputModes.SKYKEYBOARD:
                position_map = self.get_keyboard_position_map()
            elif input_mode == InputModes.SKY:
                position_map = self.get_sky_position_map()
            elif input_mode == InputModes.WESTERN:
                position_map = self.get_western_position_map()
            elif input_mode == InputModes.JIANPU:
                position_map = self.get_jianpu_position_map()
            elif input_mode == InputModes.WESTERNCHORDS:
                chord = self.decode_chord(chord, self.western_chords)
                position_map = self.get_western_position_map()
            else:
                position_map = self.get_sky_position_map()

            repeat, chord = self.split_chord(chord, position_map, repeat_indicator)
            #Now the real chord has been split in notes (1 note = 1 list slot)

            harp_broken = False
            harp_silent = False
            for note in chord: # Chord is a list of notes
                #Except InvalidLetterException
                try:
                    highlighted_note_position = self.map_note_to_position(note, position_map, note_shift)
                except KeyError:
                    harp_broken = True
                    pass
                else:
                    chord_skygrid[highlighted_note_position] = {}
                    chord_skygrid[highlighted_note_position][idx0+chord_idx] = True
                    harp_silent = False
                    if highlighted_note_position[0] < 0 and highlighted_note_position[1] < 0: #Note is a silence
                        chord_skygrid[highlighted_note_position][idx0+chord_idx] = False
                        harp_silent = True

        results = [chord_skygrid, harp_broken, harp_silent, repeat]
        return results
