#!/usr/bin/env python3
from modes import InputModes, RenderModes, CSSModes
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
    for mode in InputModes:
        print('\n* ' + mode.value[2])
        if mode == InputModes.SKYKEYBOARD:
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

    myparser.set_delimiters(ICON_DELIMITER, PAUSE, QUAVER_DELIMITER, COMMENT_DELIMITER, REPEAT_INDICATOR)
    possible_modes = myparser.get_possible_modes(song_lines)

    if len(possible_modes) > 1:
        print('\nSeveral possible notations detected.')
        song_notation = ask_for_mode(possible_modes)
    elif len(possible_modes) == 0:
        print('\nCould not detect your note format. Maybe your song contains typo errors?')
        song_notation = ask_for_mode(possible_modes)
    else:
        print('\nWe detected that you use the following notation: ' + possible_modes[0].value[1] + '.')
        song_notation = possible_modes[0]

    myparser.set_input_mode(song_notation)

    if song_notation == InputModes.JIANPU and PAUSE != '0':
        print('\nWarning: pause in Jianpu has been reset to ''0''.')
        PAUSE = '0'

    # Attempts to detect key for input written in absolute musical scales (western, Jianpu)
    possible_keys = []
    song_key = None
    if song_notation in [InputModes.ENGLISH, InputModes.DOREMI, InputModes.JIANPU]:
        possible_keys = myparser.find_key(song_lines)
        if len(possible_keys) == 0:
            print("\nYour song cannot be transposed exactly in Sky.")
            # trans = input('Enter a key or a number to transpose your song within the chromatic scale:')
            print("\nDefault key will be set to C.")
            song_key = 'C'
        elif len(possible_keys) == 1:
            song_key = str(possible_keys[0])
            print("\nYour song can be transposed in Sky with the following key: " + song_key)
        else:
            print("\nYour song can be transposed in Sky with the following keys: " + ', '.join(possible_keys))
            song_key = ''
            while song_key not in possible_keys:
                song_key = str(input('Choose your key: '))
    else:
        song_key = str(input('Recommended key to play the visual pattern: '))

    if song_notation in [InputModes.ENGLISH, InputModes.DOREMI, InputModes.JIANPU, InputModes.ENGLISHCHORDS]:
        try:
            note_shift = int(7 * eval(input('Shift song by how many octaves? (-n ; +n): ').strip()))
        except (NameError, SyntaxError):
            note_shift = 0
    else:
        note_shift = 0

    # print('Your key is: '+song_key)
    # print('Your key in English is: '+myparser.english_note_name(song_key))
    english_song_key = myparser.english_note_name(song_key)

    # Parses song line by line
    song = Song(english_song_key)  # The song key must be in English format
    for song_line in song_lines:
        instrument_line = myparser.parse_line(song_line, song_key,
                                              note_shift)  # The song key must be in the original format
        song.add_line(instrument_line)

    print('============================================================')
    error_ratio = song.get_num_broken() / max(1, song.get_num_instruments())
    if error_ratio == 0:
        print('Song successfully read with no errors!')
    elif error_ratio < 0.05:
        print('Song successfully read with few errors!')
    else:
        print('**WARNING**: Your song contains many errors. Please check the following:'
              '\n- All your notes are within octaves 4 and 6. If not, try again with an octave shift.'
              '\n- Your song is free of typos. Please check this website for full instructions: '
              'https://sky.bloomexperiment.com/t/summary-of-input-modes/403')
    print('\nPlease fill song info or press ENTER to skip:')



    # ===== Renders the song
    song.set_headers(original_artists, transcript_writer, song_key)



    os.chdir(mycwd)
