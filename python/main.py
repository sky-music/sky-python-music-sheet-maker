#!/usr/bin/env python3
from modes import InputModes, RenderModes, CSSModes
from parsers import Parser
from songs import Song
import os
import re

def ask_for_mode(modes):

    mydict = {}
    i = 0
    print('Please choose your note format:\n')
    for mode in modes:
       i += 1
       print(str(i) + ') ' + mode.value[2])
       if mode == InputModes.SKYKEYBOARD:
           print('   ' + myparser.get_keyboard_layout().replace(' ','\n   ') + ':')          
       mydict[i] = mode
    try:
        song_notation = int(input('Mode (1-' + str(i) + "): ").strip())
        mode = mydict[song_notation]
    except (ValueError, KeyError):
        mode = InputModes.SKY
    return mode

def load_file(string):
    '''
    if string is a file name, loads the file, else return None
    '''
    fp = os.path.join(SONG_DIR_IN, os.path.normpath(string))
    isfile = os.path.isfile(fp)

    #Assumes that user has forgotten extension
    if not(isfile):
        fp = os.path.join(SONG_DIR_IN, os.path.normpath(string+'.txt'))
        isfile = os.path.isfile(fp)

    if not(isfile):
        fp = None
        splitted = os.path.splitext(string)
        if len(splitted[0])>0 and len(splitted[1])>2 and len(splitted[1])<=5 and re.search('\\.',splitted[0])==None: #then probably a file name
            while fp==None:
                print('\nFile not found.')
                fp = load_file(input('File name (in ' + os.path.normpath(SONG_DIR_IN) + '/): ').strip())
                isfile = os.path.isfile(fp)        
    if isfile:
        return fp
    else:
        return None


def read_lines(fp=None):
	'''
     Read song lines in fp, or asks the user to type each line in the console
	'''
	song_lines = []
	if fp != None:
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
	return song_lines

# Parameters that can be changed by advanced users
QUAVER_DELIMITER = '-' # Dash-separated list of chords
ICON_DELIMITER = ' ' # Chords separation
PAUSE = '.'
COMMENT_DELIMITER = '#' # Lyrics delimiter, can be used for comments
REPEAT_INDICATOR = '*'
SONG_DIR_IN = 'songs'
SONG_DIR_OUT = 'songs'
CSS_PATH = 'css/main.css'
CSS_MODE = CSSModes.EMBED
ENABLED_MODES = [mode for mode in RenderModes]
#ENABLED_MODES = [RenderModes.HTML, RenderModes.SVG, RenderModes.PNG, RenderModes.SKYASCII, RenderModes.JIANPUASCII, RenderModes.WESTERNASCII, RenderModes.MIDI]

myparser = Parser() # Create a parser object

### Change directory
mycwd = os.getcwd()
os.chdir("..")
if not os.path.isdir(SONG_DIR_OUT):
    os.mkdir(SONG_DIR_OUT)

### MAIN SCRIPT
print('===== VISUAL MUSIC SHEETS FOR SKY:CHILDREN OF THE LIGHT =====')
print('\nAccepted music notes formats:')
for mode in InputModes:
    print('\n* ' + mode.value[2])
    if mode == InputModes.SKYKEYBOARD:
        print('   ' + myparser.get_keyboard_layout().replace(' ','\n   ') + ':')          
print('\nNotes composing a chord must be glued together (e.g. A1B1C1).')
print('Separate chords with \"' + ICON_DELIMITER + '\".')
print('Use \"' + PAUSE + '\" for a silence (rest).')
print('Use \"' + QUAVER_DELIMITER + '\" to link notes within an icon, for triplets, quavers... (e.g. A1' + QUAVER_DELIMITER + 'B1' + QUAVER_DELIMITER + 'C1).')
print('Add ' + REPEAT_INDICATOR + '2 after a chord to indicate repetition.')
print('Sharps # and flats b (semitones) are not yet supported.')
print('============================================================')


first_line = input('Type or copy-paste notes, or enter file name (in ' + os.path.normpath(SONG_DIR_IN) + '/): ').strip()

fp = load_file(first_line) #loads file or asks for next line

song_lines = read_lines(fp)

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


if song_notation == InputModes.JIANPU and QUAVER_DELIMITER =='-':
    print('\nWarning: quaver delimiter \'-\' is incompatible with Jianpu notation. Please use \'^\' instead.')
    QUAVER_DELIMITER = '^'

if song_notation == InputModes.JIANPU and PAUSE !='0':
    print('\nWarning: pause in Jianpu is usually ''0''.')
    PAUSE = '0'

# Attempts to detect key for input written in absolute musical scales (western, Jianpu)
musickeys  = []
song_key = None
if song_notation in [InputModes.WESTERN, InputModes.JIANPU]:
    musickeys = myparser.find_key(song_lines, COMMENT_DELIMITER, song_notation)
    if len(musickeys) == 0:
        print("\nYour song cannot be transposed exactly in Sky.")
        print("\nDefault key will be set to C.")
        song_key = 'C'
    elif len(musickeys) == 1:
        song_key = str(musickeys[0])
        print("\nYour song can be transposed in Sky with the following key: " + song_key)
    else:
        print("\nYour song can be transposed in Sky with the following keys: " + ', '.join(musickeys))
        song_key = ''
        while song_key not in musickeys:
            song_key = str(input('Choose your key:'))

if song_notation in [InputModes.WESTERN, InputModes.JIANPU, InputModes.WESTERNCHORDS]:
    try:
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

#===== Renders the song
mysong.set_title(song_title)
mysong.set_headers(original_artists, transcript_writer, musical_key)

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
            print('Your song in TXT converted to Western notation with C key is located at:', western_ascii_path)

os.chdir(mycwd)
