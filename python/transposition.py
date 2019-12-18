#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 20:39:43 2019
A dev file to transpose in the chromatic scale
@author: jmmelko
KNOWN BUGS: repeat is imported but not exported
"""
import os
import re
import math


western_position_map = {
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


dodeca_sharps = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'] 
dodeca_flats = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'] 
       


QUAVER_DELIMITER = '-' # Dash-separated list of chords
ICON_DELIMITER = ' ' # Chords separation
PAUSE = '.'
COMMENT_DELIMITER = '#' # Lyrics delimiter, can be used for comments
REPEAT_INDICATOR = '*'
SONG_DIR_IN = 'songs_in'
SONG_DIR_OUT = 'songs_out'

def is_file(string):
    isfile = False
    fp = os.path.join(SONG_DIR_IN, os.path.normpath(string))
    isfile = os.path.isfile(fp)

    if not(isfile):
        fp = os.path.join(SONG_DIR_IN, os.path.normpath(string+'.txt'))
        isfile = os.path.isfile(fp)

    if not(isfile):
        fp = os.path.join(os.path.normpath(string))
        isfile = os.path.isfile(fp)

    if not(isfile):
        splitted = os.path.splitext(string)
        if len(splitted[0])>0 and len(splitted[1])>2 and len(splitted[1])<=5: #then probably a file name
            while not(isfile) and len(fp)>2:
                print('\nFile not found.')
                isfile, fp = is_file(input('File name (in ' + os.path.normpath(SONG_DIR_IN) + '/): ').strip())

    return isfile, fp

def check_if_valid_western_note(western_note):

   '''
   Return True if note is in the format /[ABCDEFG][b#]?\d/, else return False
   '''

   #TODO: i don't remember how to use re.compile
   western_note_regexobj = re.match(r'[ABCDEFGabcdefg][b#]?\d', western_note)

   if western_note_regexobj:
       return True
   else:
       return False

def parse_western_note(western_note):
   '''
   Returns a tuple containing note_name, octave_number for a note in the format /[ABCDEFG][b#]?\d/
   '''
   if check_if_valid_western_note(western_note) == True:
      note_name = re.search(r'[ABCDEFGabcdefg][b#]?', western_note).group(0)
      octave_number = int(re.search(r'\d', western_note).group(0))
      return (note_name, octave_number)
   else:
      return (None, None)


def parse_icon(icon, delimiter):
    return icon.split(delimiter)

def split_chord(chord, repeat_indicator, position_map): 
    
    try:
        repeat = int(re.split(re.escape(repeat_indicator), chord)[1])
        chord = re.split(re.escape(repeat_indicator), chord)[0]
    except:
        repeat = 0

    chord = chord.upper()
    if position_map == western_position_map:
        chord = re.sub('([A-G])', ' \\1', chord).split()
        
    return repeat, chord


def parse_chords(chords, pause='.',  repeat_indicator='*', position_map=western_position_map, note_shift=0):

   splitted_chords = []
   n = len(dodeca_sharps)
   for chord_idx, chord in enumerate(chords):
      repeat, chord = split_chord(chord, repeat_indicator, position_map)
      for idx_in_chord, note in enumerate(chord): # Chord is a list of notes
         if note_shift != 0:
            (note_name, octave_number) = parse_western_note(note)
            if note_name != None:
               if note_name in dodeca_sharps:
                  idx = dodeca_sharps.index(note_name)
                  idx_shift = (idx + note_shift) % n
                  note_name = dodeca_sharps[idx_shift]
                  octave_number += math.floor((idx + note_shift)/n)
               elif note_name in dodeca_flats:
                  idx = dodeca_flats.index(note_name)
                  idx_shift = (idx + note_shift) % n
                  note_name = dodeca_flats[idx_shift]
                  octave_number += math.floor((idx + note_shift)/n)
               else:
                  print('This note has an error:'+note)
               #build note string again
               note = note_name + str(octave_number)
               chord[idx_in_chord] = note
      chords[chord_idx] = chord
   splitted_chords.append(chords)
   return splitted_chords

def parse_line(line, icon_delimiter=' ', pause='.', quaver_delimiter='-', comment_delimiter='#', repeat_indicator='*', position_map=western_position_map, note_shift=0):
    line = line.strip()
    re.sub(re.escape(icon_delimiter)+'{2,'+str(max(2,len(line)))+'}',icon_delimiter,line)#removes surnumerous spaces
    
    splitted_line = []
    if len(line)>0:
        if line[0] == comment_delimiter:
           lyrics = line.split(comment_delimiter) 
           for lyric in lyrics:
              if len(lyric)>0:
                 splitted_line.append('#'+lyric)
           #splitted_line.append(lyric_line)
        else:
            icons=line.split(icon_delimiter)
             #    
            for icon in icons:
                chords = parse_icon(icon, quaver_delimiter)
                splitted_chords = parse_chords(chords, pause, repeat_indicator, position_map, note_shift)
                splitted_line.append(splitted_chords)
        return splitted_line
    else:
        return ['']

def render_parsed_song(song_lines):
   song = ''
   for song_line in song_lines:
      song += '\n'
      for instr_idx, instrument in enumerate(song_line):
         if song_line[0][0][0] == '#':
            song += str(instrument)
         else:
            for icon_idx, icon in enumerate(instrument):
               for chord_idx, chord in enumerate(icon):
                  for note in chord:
                     song += note
                  if chord_idx+1 < len(icon):
                     song += '-'
            if icon_idx+1 < len(instrument):
               song += ' '
         if instr_idx+1 < len(song_line):
            song += ' '
   return song

        
mycwd = os.getcwd()
os.chdir("..")       
        
first_line = input('Type or copy-paste notes, or enter file name (in ' + os.path.normpath(SONG_DIR_IN) + '/): ').strip()

isfile, fp = is_file(first_line)
      
song_lines = []
if isfile:
    try:
        for song_line in open(fp,mode='r'):
            song_lines.append(song_line)
    except (OSError, IOError) as err:
         print('Error opening file.')
         raise err
    print('(Song imported from ' + os.path.abspath(fp)+')')
else:
    song_line = first_line
    while song_line:
        song_line = song_line.split(os.linesep)
        for line in song_line:
            song_lines.append(line)
        song_line = input('Type next line: ')
        

try:
    note_shift = int(input('Transposition ? (-12 ; +12): ').strip())
except ValueError:
    note_shift = 0

print('\n==Original:==')
for song_line in song_lines:
   print(song_line)

parsed_song = [] 
for song_line in song_lines:
    parsed_line = parse_line(song_line, ICON_DELIMITER, PAUSE, QUAVER_DELIMITER, COMMENT_DELIMITER, REPEAT_INDICATOR, western_position_map, note_shift)
    parsed_song.append(parsed_line)

print('\n==transposed:==')
print(render_parsed_song(parsed_song))
