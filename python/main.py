#!/usr/bin/env python3
from modes import InputModes, RenderModes, CSSModes
from parsers import SongParser
from songs import Song
import os
import re
try:
    import readline
except ModuleNotFoundError:
    pass  # probably Windows


def ask_for_mode(modes, myparser=None):
    if myparser == None:
        myparser = SongParser()
    mydict = {}
    i = 0
    print('Please choose your note format:\n')
    for mode in modes:
        i += 1
        print(str(i) + ') ' + mode.value[2])
        if mode == InputModes.SKYKEYBOARD:
            print('   ' + myparser.get_keyboard_layout().replace(' ', '\n   ') + ':')
        mydict[i] = mode
    try:
        notation = int(input('Mode (1-' + str(i) + "): ").strip())
        mode = mydict[notation]
    except (ValueError, KeyError):
        mode = InputModes.SKY
    return mode


def load_file(directory, filename):
    """
    if string is a file name, loads the file, else return None
    """
    filepath = os.path.join(directory, os.path.normpath(filename))
    isfile = os.path.isfile(filepath)

    # Assumes that user has forgotten extension
    if not isfile:
        filepath = os.path.join(filename, os.path.normpath(filename + '.txt'))
        isfile = os.path.isfile(filepath)

    if not isfile:
        filepath = None
        splitted = os.path.splitext(filename)
        if len(splitted[0]) > 0 and 2 < len(splitted[1]) <= 5 and re.search('\\.', splitted[0]) is None:
            # then probably a file name
            while filepath is None:
                print('\nFile not found.')
                filepath = load_file(directory, input('File name (in ' + os.path.normpath(directory) + '/): ').strip())
                isfile = os.path.isfile(filepath)
    if isfile:
        return filepath
    else:
        return None


def read_lines(filepath=None, first_line=None):
    """
     Read song lines in fp, or asks the user to type each line in the console
    """
    lines = []
    if filepath is not None:
        try:
            for line in open(filepath, mode='r', encoding='utf-8', errors='ignore'):
                lines.append(line)
        except (OSError, IOError) as err:
            print('Error opening file.')
            raise err
        print('(Song imported from ' + os.path.abspath(filepath) + ')')
    else:
        line = first_line
        while line:
            line = line.split(os.linesep)
            for line in line:
                lines.append(line)
            line = input('Type next line: ')
    return lines


if __name__ == "__main__":

    # Parameters that can be changed by advanced users
    QUAVER_DELIMITER = '-'  # Dash-separated list of chords
    ICON_DELIMITER = ' '  # Chords separation
    PAUSE = '.'
    COMMENT_DELIMITER = '#'  # Lyrics delimiter, can be used for comments
    REPEAT_INDICATOR = '*'
    SONG_DIR_IN = 'test_songs'
    SONG_DIR_OUT = 'songs_out'
    CSS_PATH = 'css/main.css'
    CSS_MODE = CSSModes.EMBED
    ENABLED_MODES = [mode for mode in RenderModes]
    # DISABLED_MODES = [RenderModes.JIANPUASCII, RenderModes.DOREMIASCII]
    DISABLED_MODES = []
    ENABLED_MODES = [mode for mode in ENABLED_MODES if mode not in DISABLED_MODES]
    # ENABLED_MODES = [RenderModes.PNG, RenderModes.SKYASCII, RenderModes.WESTERNASCII]

    myparser = SongParser()  # Create a parser object

    # ## Change directory
    mycwd = os.getcwd()
    os.chdir("..")
    if not os.path.isdir(SONG_DIR_OUT):
        os.mkdir(SONG_DIR_OUT)

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

    song_lines = read_lines(fp, first_line)

    myparser.set_delimiters(ICON_DELIMITER, PAUSE, QUAVER_DELIMITER, COMMENT_DELIMITER, REPEAT_INDICATOR)
    possible_modes = myparser.get_possible_modes(song_lines)

    if len(possible_modes) > 1:
        print('\nSeveral possible notations detected.')
        song_notation = ask_for_mode(possible_modes, myparser)
    elif len(possible_modes) == 0:
        print('\nCould not detect your note format. Maybe your song contains typo errors?')
        song_notation = ask_for_mode(possible_modes, myparser)
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
    mysong = Song(english_song_key)  # The song key must be in English format
    for song_line in song_lines:
        instrument_line = myparser.parse_line(song_line, song_key,
                                              note_shift)  # The song key must be in the original format
        mysong.add_line(instrument_line)

    print('============================================================')
    error_ratio = mysong.get_num_broken() / max(1, mysong.get_num_instruments())
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

    song_title = input('Song title (also used for the file name): ')
    if song_title == '':
        song_title = 'untitled'
    original_artists = input('Original artist(s): ')
    transcript_writer = input('Transcribed by: ')

    # ===== Renders the song
    mysong.set_title(song_title)
    mysong.set_headers(original_artists, transcript_writer, song_key)

    if RenderModes.HTML in ENABLED_MODES:
        html_path = os.path.join(SONG_DIR_OUT, song_title + '.html')
        html_path = mysong.write_html(html_path, CSS_MODE, CSS_PATH)

        if html_path != '':
            print('============================================================')
            print('Your song in HTML is located at:', html_path)

    if RenderModes.SVG in ENABLED_MODES:
        svg_path0 = os.path.join(SONG_DIR_OUT, song_title + '.svg')
        filenum, svg_path = mysong.write_svg(svg_path0, CSS_MODE, CSS_PATH)

        if svg_path != '':
            print('--------------------------------------------------')
            print('Your song in SVG is located in:', SONG_DIR_OUT)
            print('Your song has been split into ' + str(filenum + 1) + ' files '
                                                                        'between ' + os.path.split(svg_path0)[
                      1] + ' and ' + os.path.split(svg_path)[1])

    if RenderModes.PNG in ENABLED_MODES:
        png_path0 = os.path.join(SONG_DIR_OUT, song_title + '.png')
        filenum, png_path = mysong.write_png(png_path0)

        if png_path != '':
            print('--------------------------------------------------')
            print('Your song in PNG is located in:', SONG_DIR_OUT)
            print('Your song has been split into ' + str(filenum + 1) + ' files '
                                                                        'between ' + os.path.split(png_path0)[
                      1] + ' and ' + os.path.split(png_path)[1])

    if RenderModes.MIDI in ENABLED_MODES:
        midi_path = os.path.join(SONG_DIR_OUT, song_title + '.mid')
        midi_path = mysong.write_midi(midi_path)
        if midi_path != '':
            print('--------------------------------------------------')
            print('Your song in MIDI is located at:', midi_path)

    if RenderModes.SKYASCII in ENABLED_MODES and song_notation not in [InputModes.SKY, InputModes.SKYKEYBOARD]:
        sky_ascii_path = os.path.join(SONG_DIR_OUT, song_title + '_sky.txt')
        res = mysong.write_ascii(sky_ascii_path, RenderModes.SKYASCII)
        if sky_ascii_path != '':
            print('--------------------------------------------------')
            print('Your song in TXT converted to Sky notation is located at:', sky_ascii_path)

    if RenderModes.ENGLISHASCII in ENABLED_MODES and song_notation not in [InputModes.ENGLISH,
                                                                           InputModes.ENGLISHCHORDS]:
        english_ascii_path = os.path.join(SONG_DIR_OUT, song_title + '_english.txt')
        english_ascii_path = mysong.write_ascii(english_ascii_path, RenderModes.ENGLISHASCII)
        if english_ascii_path != '':
            print('--------------------------------------------------')
            print('Your song in TXT converted to English notation with C key is located at:', english_ascii_path)

    if RenderModes.JIANPUASCII in ENABLED_MODES and song_notation != InputModes.JIANPU:
        jianpu_ascii_path = os.path.join(SONG_DIR_OUT, song_title + '_jianpu.txt')
        jianpu_ascii_path = mysong.write_ascii(jianpu_ascii_path, RenderModes.JIANPUASCII)
        if jianpu_ascii_path != '':
            print('--------------------------------------------------')
            print('Your song in TXT converted to Jianpu notation with 1 key is located at:', jianpu_ascii_path)

    if RenderModes.DOREMIASCII in ENABLED_MODES and song_notation != InputModes.DOREMI:
        doremi_ascii_path = os.path.join(SONG_DIR_OUT, song_title + '_doremi.txt')
        doremi_ascii_path = mysong.write_ascii(doremi_ascii_path, RenderModes.DOREMIASCII)
        if doremi_ascii_path != '':
            print('--------------------------------------------------')
            print('Your song in TXT converted to doremi notation with do key is located at:', doremi_ascii_path)

    os.chdir(mycwd)
