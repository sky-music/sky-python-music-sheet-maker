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
from main import load_file, read_lines, ask_for_mode
from parsers import SongParser
from modes import InputModes

dodeca_sharps = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
dodeca_flats = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

QUAVER_DELIMITER = '-'  # Dash-separated list of chords
ICON_DELIMITER = ' '  # Chords separation
PAUSE = '.'
COMMENT_DELIMITER = '#'  # Lyrics delimiter, can be used for comments
REPEAT_INDICATOR = '*'
SONG_DIR_IN = 'test_songs'
SONG_DIR_OUT = 'songs_out'


def parse_chords(chords, note_shift=0):
    splitted_chords = []
    n = len(dodeca_sharps)
    for chord_idx, chord in enumerate(chords):
        repeat, chord = skyparser.split_chord(chord)
        for idx_in_chord, note in enumerate(chord):  # Chord is a list of notes
            if note_shift != 0:
                try:
                    (note_name, octave_number) = skyparser.get_note_parser().parse_note(note)
                    if note_name != None:
                        if note_name in dodeca_sharps:
                            idx = dodeca_sharps.index(note_name)
                            idx_shift = (idx + note_shift) % n
                            note_name = dodeca_sharps[idx_shift]
                            octave_number += math.floor((idx + note_shift) / n)
                        elif note_name in dodeca_flats:
                            idx = dodeca_flats.index(note_name)
                            idx_shift = (idx + note_shift) % n
                            note_name = dodeca_flats[idx_shift]
                            octave_number += math.floor((idx + note_shift) / n)
                        else:
                            print('This note has an error:' + note)
                        # build note string again
                        note = note_name + str(octave_number)
                except SyntaxError:
                    pass
                chord[idx_in_chord] = note
    chords[chord_idx] = chord
    splitted_chords.append(chords)
    return splitted_chords


def parse_line(line, note_shift=0):
    icon_delimiter = skyparser.icon_delimiter
    comment_delimiter = skyparser.comment_delimiter

    line = line.strip()
    re.sub(re.escape(icon_delimiter) + '{2,' + str(max(2, len(line))) + '}', icon_delimiter,
           line)  # removes surnumerous spaces

    splitted_line = []
    if len(line) > 0:
        if line[0] == comment_delimiter:
            lyrics = line.split(comment_delimiter)
            for lyric in lyrics:
                if len(lyric) > 0:
                    splitted_line.append('#' + lyric)
            # splitted_line.append(lyric_line)
        else:
            icons = line.split(icon_delimiter)
            #
            for icon in icons:
                chords = skyparser.split_icon(icon)
                splitted_chords = parse_chords(chords, note_shift)
                splitted_line.append(splitted_chords)
        return splitted_line
    else:
        return ['']


def render_transposed_song(song_lines):
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
                        if chord_idx + 1 < len(icon):
                            song += '-'
                if icon_idx + 1 < len(instrument):
                    song += ' '
            if instr_idx + 1 < len(song_line):
                song += ' '
    return song


# ========== MAIN SCRIPT================
mycwd = os.getcwd()
os.chdir("..")

print('===== TRANSPOSITION TOOL IN THE CHROMATIC SCALE =====')
first_line = input('Type or copy-paste notes, or enter file name (in ' + os.path.normpath(SONG_DIR_IN) + '/): ').strip()

fp = load_file(SONG_DIR_IN, first_line)  # loads file or asks for next line

song_lines = read_lines(fp)

try:
    note_shift = int(input('Transposition ? (-12 ; +12): ').strip())
except ValueError:
    note_shift = 0

skyparser = SongParser()
skyparser.set_delimiters(ICON_DELIMITER, PAUSE, QUAVER_DELIMITER, COMMENT_DELIMITER, REPEAT_INDICATOR)
possible_modes = skyparser.get_possible_modes(song_lines)

if len(possible_modes) > 1:
    print('\nSeveral possible notations detected.')
    song_notation = ask_for_mode(possible_modes)
elif len(possible_modes) == 0:
    print('\nCould not detect your note format. Maybe your song contains typo errors?')
    song_notation = ask_for_mode(possible_modes)
else:
    print('\nWe detected that you use the following notation: ' + possible_modes[0].value[1] + '.')
    song_notation = possible_modes[0]

skyparser.set_input_mode(song_notation)

if song_notation == InputModes.JIANPU and PAUSE != '0':
    print('\nWarning: pause in Jianpu has been reset to ''0''.')
    PAUSE = '0'

parsed_song = []
for song_line in song_lines:
    parsed_line = parse_line(song_line, note_shift)
    parsed_song.append(parsed_line)

print('\n==Original song:==')
print(''.join(song_lines))

print('\n==Transposed song:==')
print(render_transposed_song(parsed_song))
