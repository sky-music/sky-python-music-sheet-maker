#!/usr/bin/env python3
from modes import InputModes, RenderModes, CSSModes
from parsers import Parser
from songs import Song
import os

### Define Errors
#class Error(Exception):
#    """Base class for exceptions in this module."""
#    pass
def ask_for_mode(modes):

    mydict = {}
    i = 0
    print('Please choose your note format:\n')
    if InputModes.SKYKEYBOARD in modes:
        i += 1
        print(str(i) + ') ' + InputModes.SKYKEYBOARD.value[2] + '\n   ' + myparser.keyboard_layout.replace(' ','\n   ') + ':')
        mydict[i] = InputModes.SKYKEYBOARD
    if InputModes.SKY in modes:
        i += 1
        print(str(i) + ') ' + InputModes.SKY.value[2])
        mydict[i] = InputModes.SKY
    if InputModes.WESTERN in modes:
        i += 1
        print(str(i) + ') ' + InputModes.WESTERN.value[2])
        mydict[i] = InputModes.WESTERN
    if InputModes.JIANPU in modes:
        i += 1
        print(str(i) + ') ' + InputModes.JIANPU.value[2])
        mydict[i] = InputModes.JIANPU
    if InputModes.WESTERNCHORDS in modes:
        i += 1
        print(str(i) + ') ' + InputModes.WESTERNCHORDS.value[2])
        mydict[i] = InputModes.WESTERNCHORDS
    try:
        song_notation = int(input("Mode (1-" + str(i) + "): ").strip())
        mode = mydict[song_notation]
    except (ValueError, KeyError):
        mode = InputModes.SKY
    return mode


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
        if len(splitted[0])>0 and len(splitted[1])>0 and len(splitted[1])<=5: #then probably a file name
            while not(isfile) and len(fp)>2:
                print('\nFile not found.')
                isfile, fp = is_file(input('File name (in ' + os.path.normpath(SONG_DIR_IN) + '/): ').strip())

    return isfile, fp

# Parameters that can be changed by advanced users
QUAVER_DELIMITER = '-' # Dash-separated list of chords
ICON_DELIMITER = ' ' # Chords separation
NOTE_WIDTH = "1em" #Any CSS-compatible unit can be used
PAUSE = '.'
COMMENT_DELIMITER = '#' # Lyrics delimiter, can be used for comments
REPEAT_INDICATOR = '*'
SONG_DIR_IN = 'songs'
SONG_DIR_OUT = 'songs'
CSS_PATH = 'css/main.css'
CSS_MODE = CSSModes.EMBED
ENABLED_MODES = [RenderModes.HTML, RenderModes.SVG, RenderModes.PNG, RenderModes.SKYASCII, RenderModes.JIANPUASCII, RenderModes.WESTERNASCII]

myparser = Parser() # Create a parser object

### Change directory
mycwd = os.getcwd()
os.chdir("..")
if not os.path.isdir(SONG_DIR_OUT):
    os.mkdir(SONG_DIR_OUT)

### MAIN SCRIPT

print('===== VISUAL MUSIC SHEETS FOR SKY:CHILDREN OF THE LIGHT =====')
print('\nAccepted music notes formats:')
print('\n* ' + InputModes.SKYKEYBOARD.value[2] + '\n   ' + myparser.keyboard_layout.replace(' ','\n   '))
print('\n* ' + InputModes.SKY.value[2])
print('\n* ' + InputModes.WESTERN.value[2])
print('\n* ' + InputModes.JIANPU.value[2])
print('\n* ' + InputModes.WESTERNCHORDS.value[2])
print('\nNotes composing a chord must be glued together (e.g. A1B1C1).')
print('Separate chords with \"' + ICON_DELIMITER + '\".')
print('Use \"' + PAUSE + '\" for a silence (rest).')
print('Use \"' + QUAVER_DELIMITER + '\" to link notes within an icon, for triplets, quavers... (e.g. A1' + QUAVER_DELIMITER + 'B1' + QUAVER_DELIMITER + 'C1).')
print('Add ' + REPEAT_INDICATOR + '2 after a chord to indicate repetition.')
print('Sharps # and flats b (semitones) are not supported in Sky.')
print('============================================================')


first_line = input('Type or copy-paste notes, or enter file name (in ' + os.path.normpath(SONG_DIR_IN) + '/): ').strip()

isfile, fp = is_file(first_line)

song_lines = []
if isfile:
    try:
        for song_line in open(fp,mode='r', encoding='utf-8', errors='ignore'):
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


possible_modes = myparser.detect_input_type(song_lines, ICON_DELIMITER, PAUSE, QUAVER_DELIMITER, COMMENT_DELIMITER, REPEAT_INDICATOR)

if len(possible_modes) > 1:
    print('\nSeveral possible notations detected.')
    song_notation = ask_for_mode(possible_modes)
elif len(possible_modes) == 0:
    print('\nCould not detect your note format. Maybe your song contains typo errors?')
    song_notation = ask_for_mode(possible_modes)
else:
    print('\nWe detected that you use the following notation: ' + possible_modes[0].value[1] + '.')
    song_notation = possible_modes[0]

if song_notation == 'JIANPU' and QUAVER_DELIMITER =='-':
    print('\nWarning: quaver delimiter \'-\' is incompatible with Jianpu notation. Please use \'^\' instead.')
    QUAVER_DELIMITER = '^'

# Attempts to detect key for input written in absolute musical scales (western, Jianpu)
musickeys  = []
if song_notation in [InputModes.WESTERN, InputModes.JIANPU]:
    #TODO: update find_keys
    musickeys = myparser.find_key(song_lines, COMMENT_DELIMITER, song_notation)
    if len(musickeys) == 0:
        print("\nYour song cannot be transposed exactly in Sky.")
    else:
        print("\nYour song can be transposed in Sky with the following keys: " + str(musickeys))

if song_notation in [InputModes.WESTERN, InputModes.JIANPU, InputModes.WESTERNCHORDS]:
    try:
        #TODO: print default range for each mode

        note_shift = int(input('Shift notes by n positions ? (-21 ; +21): ').strip())
    except ValueError:
        note_shift = 0
else:
    note_shift = 0

# Parses song line by line
mysong = Song()
for song_line in song_lines:
    instrument_line = myparser.parse_line(song_line, ICON_DELIMITER, PAUSE, QUAVER_DELIMITER, COMMENT_DELIMITER, song_notation, note_shift, REPEAT_INDICATOR)
    mysong.add_line(instrument_line)


print('============================================================')
error_ratio = mysong.get_num_broken()/max(1,mysong.get_num_instruments())
if error_ratio==0:
    print('Song successfully read with no errors!')
elif error_ratio<0.05:
    print('Song successfully read with few errors!')
else:
    print('Your song contains many errors.')
print('\nPlease fill song info or press ENTER to skip:')
if len(musickeys)>0:
    musical_key = musickeys[0]
else:
    musical_key = input('Recommended key to play the visual pattern: ')

song_title = input('Song title (also used for the file name): ')
if song_title=='':
    song_title='untitled'
original_artists = input('Original artist(s): ')
transcript_writer = input('Transcribed by: ')

# Renders the song
mysong.set_title(song_title)
mysong.set_headers(original_artists, transcript_writer, musical_key)

if RenderModes.HTML in ENABLED_MODES:
    html_path = os.path.join(SONG_DIR_OUT, song_title + '.html')
    html_path = mysong.write_html(html_path, NOTE_WIDTH, CSS_MODE, CSS_PATH)

    if html_path != '':
        print('============================================================')
        print('Your song in HTML is located at:', html_path)

if RenderModes.SVG in ENABLED_MODES:
    svg_path0 = os.path.join(SONG_DIR_OUT, song_title + '.svg')
    filenum, svg_path = mysong.write_svg(svg_path0, CSS_MODE, CSS_PATH)

    if svg_path != '':
        print('--------------------------------------------------')
        print('Your song in SVG is located in:', SONG_DIR_OUT)
        print('Your song has been split into ' + str(filenum+1) + ' files '
              'between ' + os.path.split(svg_path0)[1] + ' and ' + os.path.split(svg_path)[1])

if RenderModes.PNG in ENABLED_MODES:
    png_path0 = os.path.join(SONG_DIR_OUT, song_title + '.png')
    filenum, png_path = mysong.write_png(png_path0)

    if png_path != '':
        print('--------------------------------------------------')
        print('Your song in PNG is located in:', SONG_DIR_OUT)
        print('Your song has been split into ' + str(filenum+1) + ' files '
              'between ' + os.path.split(png_path0)[1] + ' and ' + os.path.split(png_path)[1])

if RenderModes.SKYASCII in ENABLED_MODES:
    if song_notation in [InputModes.WESTERN, InputModes.JIANPU, InputModes.WESTERNCHORDS]:
        sky_ascii_path = os.path.join(SONG_DIR_OUT, song_title + '_sky.txt')
        res = mysong.write_ascii(sky_ascii_path, RenderModes.SKYASCII)
        if sky_ascii_path != '':
            print('--------------------------------------------------')
            print('Your song in TXT converted to Sky notation is located at:', sky_ascii_path)

if RenderModes.WESTERNASCII in ENABLED_MODES:
    if song_notation in [InputModes.SKY, InputModes.SKYKEYBOARD]:
        western_ascii_path = os.path.join(SONG_DIR_OUT, song_title + '_western.txt')
        western_ascii_path = mysong.write_ascii(western_ascii_path, RenderModes.WESTERNASCII)
        if western_ascii_path != '':
            print('--------------------------------------------------')
            print('Your song in TXT converted to Western notation is located at:', western_ascii_path)

os.chdir(mycwd)
