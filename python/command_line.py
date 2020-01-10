#!/usr/bin/env python3
from modes import InputMode, RenderMode, CSSMode
from parsers import SongParser
from songs import Song
import os
import re


if __name__ == "command_line":

    myparser = SongParser()  # Create a parser object

    # ## Change directory

    # ## MAIN SCRIPT
    print('===== VISUAL MUSIC SHEETS FOR SKY:CHILDREN OF THE LIGHT =====')
    print('\nAccepted music notes formats:')
    for mode in InputMode:
        print('\n* ' + mode.value[2])
        if mode == InputMode.SKYKEYBOARD:
            print('   ' + myparser.get_keyboard_layout().replace(' ', '\n   ') + ':')
    print('\nNotes composing a chord must be glued together (e.g. A1B1C1).')
    print('Separate chords with \"' + ICON_DELIMITER + '\".')
    print('Use \"' + PAUSE + '\" for a silence (rest).')
    print(
        'Use \"' + QUAVER_DELIMITER + '\" to link notes within an icon, for triplets, quavers... (e.g. A1' + QUAVER_DELIMITER + 'B1' + QUAVER_DELIMITER + 'C1).')
    print('Add ' + REPEAT_INDICATOR + '2 after a chord to indicate repetition.')
    print('Sharps # and flats b (semitones) are supported for Western and Jianpu notations.')
    print('============================================================')

    first_line = input(
        'Type or copy-paste notes, or enter file name (in ' + os.path.normpath(SONG_DIR_IN) + '/): ').strip()

    fp = load_file(SONG_DIR_IN, first_line)  # loads file or asks for next line

    song_lines = read_lines(fp)

    os.chdir(mycwd)
