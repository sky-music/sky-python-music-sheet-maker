#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 20:39:43 2019
A dev file to transpose in the chromatic scale
@author: jmmelko
KNOWN BUGS: repeat is imported but not exported
"""
import sys
sys.path.append('..')
import os
import re
import math
from responder import Responder
from parsers import SongParser
from modes import InputMode, ResponseMode

def set_dodecas(mode):
    if mode==InputMode.DOREMI:
        dodeca_sharps = ['do', 'do#', 're', 're#', 'mi', 'fa', 'fa#', 'sol', 'sol#', 'la', 'la#', 'si']
        dodeca_flats = ['do', 'reb', 're', 'mib', 'mi', 'fa', 'solb', 'sol', 'lab', 'la', 'sib', 'si']
    elif mode==InputMode.JIANPU:
        dodeca_sharps = ['1', '1#', '2', '2#', '3', '4', '4#', '5', '5#', '6', '6#', '7']
        dodeca_flats = ['1', '2b', '2', '3b', '3', '4', '5b', '5', '6b', '6', '7b', '7']
    else:
        dodeca_sharps = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        dodeca_flats = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
    return (dodeca_sharps,dodeca_flats)

QUAVER_DELIMITER = '-'  # Dash-separated list of chords
ICON_DELIMITER = ' '  # Chords separation
PAUSE = '.'
COMMENT_DELIMITER = '#'  # Lyrics delimiter, can be used for comments
REPEAT_INDICATOR = '*'

def parse_chords(chords, note_shift=0, song_jet='C'):
    splitted_chords = []
    n = len(dodeca_sharps)
    for chord_idx, chord in enumerate(chords):
        repeat, chord = skyparser.split_chord(chord)
        for idx_in_chord, note in enumerate(chord):  # Chord is a list of notes
            if note_shift != 0:
                try:
                    (note_name, octave_number) = skyparser.get_note_parser().parse_note(note, song_key)
                    if note_name is not None:
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


def parse_line(line, note_shift=0, song_key='C'):
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
                splitted_chords = parse_chords(chords, note_shift, song_key)
                splitted_line.append(splitted_chords)
        return splitted_line
    else:
        return ['']


def render_transposed_song(song_lines):
    song = ''
    for song_line in song_lines:
        if song_line[0] != '':
            song += '\n'
        for instr_idx, instrument in enumerate(song_line):
            try:
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
            except IndexError:
                pass
    return song


# ========== MAIN SCRIPT================
os.chdir(os.getcwd())

print('===== TRANSPOSITION TOOL IN THE CHROMATIC SCALE =====')

song_responder = Responder()
song_responder.set_response_mode(ResponseMode.COMMAND_LINE)

first_line = song_responder.ask_first_line()

fp = song_responder.load_file(song_responder.get_song_dir_in(), first_line)  # loads file or asks for next line

song_lines = song_responder.read_lines(first_line, fp)

try:
    note_shift = int(input('Transposition ? (-12 ; +12): ').strip())
except ValueError:
    note_shift = 0

skyparser = SongParser(song_responder)
skyparser.set_delimiters(ICON_DELIMITER, PAUSE, QUAVER_DELIMITER, COMMENT_DELIMITER, REPEAT_INDICATOR)
possible_modes = skyparser.get_possible_modes(song_lines)

if len(possible_modes) > 1:
    print('\nSeveral possible notations detected.')
    song_notation = song_responder.ask_to_select_mode(possible_modes)
elif len(possible_modes) == 0:
    print('\nCould not detect your note format. Maybe your song contains typo errors?')
    song_notation = song_responder.ask_to_select_mode(possible_modes)
else:
    print('\nWe detected that you use the following notation: ' + possible_modes[0].value[1] + '.')
    song_notation = possible_modes[0]

skyparser.set_input_mode(song_notation)

if song_notation == InputMode.JIANPU and PAUSE != '0':
    print('\nWarning: pause in Jianpu has been reset to ''0''.')
    PAUSE = '0'

# Attempts to detect key for input written in absolute musical scales (western, Jianpu)
possible_keys = []
song_key = None
if song_notation in [InputMode.ENGLISH, InputMode.DOREMI, InputMode.JIANPU]:
    possible_keys = skyparser.find_key(song_lines)
    if len(possible_keys) == 0:
        # print("\nYour song cannot be transposed exactly in Sky.")
        # trans = input('Enter a key or a number to transpose your song within the chromatic scale:')
        # print("\nDefault key will be set to C.")
        song_key = 'C'
    elif len(possible_keys) == 1:
        song_key = str(possible_keys[0])
        print("\nYour song can be transposed in Sky with the following key: " + song_key)
    else:
        # print("\nYour song can be transposed in Sky with the following keys: " + ', '.join(possible_keys))
        # song_key = ''
        # while song_key not in possible_keys:
        # song_key = str(input('Choose your key: '))
        song_key = str(possible_keys[0])
else:
    song_key = str(input('Recommended key to play the visual pattern: '))

dodeca_sharps, dodeca_flats = set_dodecas(song_notation)

parsed_song = []
for song_line in song_lines:
    parsed_line = parse_line(song_line, note_shift)
    parsed_song.append(parsed_line)

print('\n==Original song:==')
print(''.join(song_lines))

print('\n==Transposed song:==')
print(render_transposed_song(parsed_song))
