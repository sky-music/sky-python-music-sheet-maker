#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 20:39:43 2019
A dev file to transpose in the chromatic scale
@author: jmmelko
THIS SCRIPTS IS COMPLETELY OBSOLETE AND SHOULD BE REWRITTEN
"""
if __name__ == '__main__':    
    import os, sys
    project_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../'))
    if project_path not in sys.path:
        sys.path.append(project_path)
import os
import math
from skymusic.parsers.song_parser import SongParser
from skymusic.modes import InputMode
from skymusic.resources import Resources

def set_dodecas(mode):
    if mode==InputMode.DOREMI:
        dodeca_sharps = ['do', 'do#', 're', 're#', 'mi', 'fa', 'fa#', 'sol', 'sol#', 'la', 'la#', 'si']
        dodeca_flats = ['do', 'reb', 're', 'mib', 'mi', 'fa', 'solb', 'sol', 'lab', 'la', 'sib', 'si']
    elif mode==InputMode.JIANPU:
        dodeca_sharps = ['1', '1#', '2', '2#', '3', '4', '4#', '5', '5#', '6', '6#', '7']
        dodeca_flats = ['1', '2b', '2', '3b', '3', '4', '5b', '5', '6b', '6', '7b', '7']
    elif mode==InputMode.DOREMIJP:
        dodeca_sharps = ['ド', 'ド#', 'レ', 'レ#', 'ミ', 'ファ', 'ファ#', 'ソ', 'ソ#', 'ラ', 'ラ#', 'シ']
        dodeca_flats = ['ド', 'レb', 'レ', 'ミb', 'ミ', 'ファ', 'ソb', 'ソ', 'ラb', 'ラ', 'シb', 'シ']
    else:
        dodeca_sharps = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        dodeca_flats = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
    return (dodeca_sharps,dodeca_flats)


def parse_chords(song_parser, chords, note_shift=0, song_jet='C'):
    splitted_chords = []
    n = len(dodeca_sharps)
    for chord_idx, chord in enumerate(chords):
        repeat, chord = song_parser.split_chord(chord)
        for idx_in_chord, note in enumerate(chord):  # Chord is a list of notes
            if note_shift != 0:
                try:
                    (note_name, octave_number) = song_parser.get_note_parser().parse_note(note, song_key)
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


def parse_line(song_parser, line, note_shift=0, song_key='C'):
    lyric_delimiter = song_parser.get_lyric_delimiter()

    line = song_parser.sanitize_line(line)
    
    splitted_line = []
    if len(line) > 0:
        if line[0] == lyric_delimiter:
            lyrics = song_parser.split_line(line)
            for lyric in lyrics:
                if len(lyric) > 0:
                    splitted_line.append(Resources.LYRIC_DELIMITER + lyric)
            # splitted_line.append(lyric_line)
        else:
            icons = song_parser.split_line(line)

            for icon in icons:
                chords = song_parser.split_icon(icon)
                splitted_chords = parse_chords(song_parser, chords, note_shift, song_key)
                splitted_line.append(splitted_chords)
        return splitted_line
    else:
        return ['']


def render_transposed_song(song_lines):

    if isinstance(song_lines,str): #Break newlines and make sure the result is a List
        song_lines = song_lines.split(os.linesep)

    song = ''
    for song_line in song_lines:
        if song_line[0] != '':
            song += '\n'
        for instr_idx, instrument in enumerate(song_line):
            try:
                if song_line[0][0][0] == Resources.LYRIC_DELIMITER:
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

print('===== TRANSPOSITION TOOL IN THE CHROMATIC SCALE =====')

song_lines = []

while True:
    line = input("Type your notes here: ")
    if line == '':
        break
    line = line.split(os.linesep)
    song_lines += line

"""
try:
    note_shift = int(input('Transpose by how many semitones? (-12 ; +12): ').strip())
except ValueError:
    note_shift = 0
"""

song_parser = SongParser(None)

possible_modes = song_parser.get_possible_modes(song_lines=song_lines)

if len(possible_modes) > 1:
    print('\nSeveral possible notations detected.')
    for i,mode in enumerate(possible_modes):
        print(f'{i}: {mode.get_short_desc()}')
    num = int(input('Choose your mode number:'))
    song_notation = possible_modes[num]
elif len(possible_modes) == 0:
    print('\nCould not detect your note format. Maybe your song contains typo errors?')
    possible_modes = [mode for mode in InputMode]
    for i,mode in enumerate(possible_modes):
        print(f'{i}: {mode.get_short_desc()}')
    num = int(input('Choose your mode number:'))
    song_notation = possible_modes[num]
else:
    print('\nWe detected that you use the following notation: %s.'%possible_modes[0].get_short_desc())
    song_notation = possible_modes[0]

song_parser.set_input_mode(song_notation)


# Attempts to detect key for input written in absolute musical scales (western, Jianpu)
possible_keys = []
song_key = None
if song_notation in [InputMode.ENGLISH, InputMode.DOREMI, InputMode.JIANPU, InputMode.DOREMIJP]:
    possible_keys = song_parser.find_key(song_lines)
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

print('\n=== Original song ===')
print(''.join(song_lines))

for note_shift in range(-12, 12):

    parsed_song = []
    for song_line in song_lines:
        parsed_line = parse_line(song_parser, song_line, note_shift)
        parsed_song.append(parsed_line)

    print('\n=== Transposition by %+d ===' % note_shift)
    print(render_transposed_song(parsed_song))
