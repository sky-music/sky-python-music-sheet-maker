#!/usr/bin/env python3
from modes import InputMode, RenderMode
from parsers import Parser
from render import write_html, write_ascii
import os

### Define Errors
class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class BlackIconError(Error):
    pass

# Parameters that can be changed by advanced users
QUAVER_DELIMITER = '^' # Dash-separated list of chords
ICON_DELIMITER = ' ' # Chords separation
NOTE_WIDTH = "1.0em" #Any CSS-compatible unit can be used
BLANK_ICON = '.'
COMMENT_DELIMITER = '#' # Lyrics delimiter, can be used for comments

myparser = Parser() # Create a parser object

### Change directory
mycwd = os.getcwd()
os.chdir("..")
if not os.path.exists('songs'):
    os.makedirs('songs')
os.chdir("songs")
song_dir=os.getcwd()


### MAIN SCRIPT
 
print('===== NEW SONG =====')
print("Choose input mode:\n")
print("1) Use " + myparser.keyboard_layout + " as keyboard.")
print("2) Type in the command line.")
print("3) Import a text file.")
   
try:
    song_input_mode = int(input("Mode (1-3): ").strip())
except ValueError:
    song_input_mode = 1

if song_input_mode != 1:
    print("Choose your notation:\n")
    print("1) Sky notation (A1 A2 A3 A4 A5, B1 B2 B3 B4 B5, C1 C2 C3 C4 C5)")
    print("2) Western (C4 D4 E4 F4 G4 A4 B4)")
    print("3) Jianpu (1 2 3 4 5 6 7, followed by + or - for octaves)")
    try:
        song_notation = int(input("Mode (1-3): ").strip())
    except ValueError:
        song_notation = 1    
else:
    song_notation = 1
    
if song_input_mode == 1:
    song_input_mode = InputMode.SKYKEYBOARD
elif song_input_mode == 2 and song_notation == 1:
    song_input_mode = InputMode.SKY
elif song_input_mode == 2 and song_notation == 2:
    song_input_mode = InputMode.WESTERN
elif song_input_mode == 2 and song_notation == 3:
    song_input_mode = InputMode.JIANPU
elif song_input_mode == 3 and song_notation == 1:
    song_input_mode = InputMode.SKYFILE
elif song_input_mode == 3 and song_notation == 2:
    song_input_mode = InputMode.WESTERNFILE
elif song_input_mode == 3 and song_notation == 3:
    song_input_mode = InputMode.JIANPUFILE
else:
    song_input_mode = InputMode.SKYKEYBOARD

if song_input_mode in [InputMode.WESTERN, InputMode.WESTERNFILE, InputMode.JIANPU, InputMode.JIANPUFILE]:
    try:
        note_shift = int(input('Shift by n notes (-21 ; +21): ').strip())
    except ValueError:
        note_shift = 0
else:
    note_shift = 0

if song_input_mode in [InputMode.JIANPU, InputMode.JIANPUFILE] and QUAVER_DELIMITER =='-':
    print('\nWarning: quaver delimiter \'-\' is incompatible with Jianpu notation. Please use \'^\' instead.')
    QUAVER_DELIMITER = '^'

print('\nSeparate blocks of notes with \"' + ICON_DELIMITER + '\".')
print('Use \"' + BLANK_ICON + '\" for a blank block.')
print('If you want multiple colours within an icon, separate the colours with \"' + QUAVER_DELIMITER + '\".')
print('=========================')


# SONG INPUT: file or console input
if song_input_mode in [InputMode.SKYFILE, InputMode.WESTERNFILE, InputMode.JIANPUFILE]:
    fp = os.path.normpath(input('File name (in ' + os.path.normpath('../songs/') + '): '))
    try:
        if song_input_mode in [InputMode.SKYFILE, InputMode.WESTERNFILE, InputMode.JIANPUFILE]:
           song_lines = open(fp,mode='r')
           print(['Opening file: ' + os.path.abspath(fp)])
    except (OSError, IOError) as err:
         print('Error opening file.')
         raise err
else:
    song_lines = []
    song_line = input('Type line: ')
    while song_line:
        song_lines.append(song_line)
        song_line = input('Type line: ')

# Attempts to detect key for input written in absolute musical scales (western, Jianpu)
musickeys  = []
if song_input_mode in [InputMode.WESTERN, InputMode.JIANPU, InputMode.WESTERNFILE, InputMode.JIANPUFILE]:
    musickeys = myparser.find_key(song_lines, COMMENT_DELIMITER, song_input_mode) 
    if len(musickeys) == 0:
        print("\nYour song cannot be transposed exactly in Sky.")
    else:
        print("\nYour song can be transposed in Sky with the following keys:")
        print(musickeys)
        print('\nTransposition is not implemented yet. Assuming you will play in \'C\'.')

# Parses song line by line
instrument_lines = [] # An array of Instrument class lines
if song_input_mode in [InputMode.SKYFILE, InputMode.WESTERNFILE, InputMode.JIANPUFILE]:
    try:
        song_lines = open(fp,mode='r')            
        for song_line in song_lines:
            instrument_line = myparser.parse_line(song_line.rstrip(), ICON_DELIMITER, BLANK_ICON, QUAVER_DELIMITER, COMMENT_DELIMITER, song_input_mode, note_shift)            
            instrument_lines.append(instrument_line)    
        song_lines.close()
    except (OSError, IOError) as err:
        print('Error opening file.')
        raise err
else:
    for song_line in song_lines:
        instrument_line = myparser.parse_line(song_line, ICON_DELIMITER, BLANK_ICON, QUAVER_DELIMITER, COMMENT_DELIMITER, song_input_mode, note_shift)    
        instrument_lines.append(instrument_line)   


print('=========================')
print('Press ENTER to skip the following.')
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
titlehead = [[''], [song_title]]
headers = [['Original Artist(s):', 'Transcript:', 'Musical key:'], [original_artists, transcript_writer, musical_key]]

html_path = os.path.join(song_title + '.html')
with open(html_path, 'w+') as html_file:
    write_html(html_file, titlehead, headers, instrument_lines, NOTE_WIDTH, RenderMode.VISUALHTML)

print('=========================')
print('Your song in HTML is located at:', os.path.join(str(song_dir), html_path))

if song_input_mode in [InputMode.WESTERN, InputMode.JIANPU, InputMode.WESTERNFILE, InputMode.JIANPUFILE]:
    sky_ascii_path = os.path.join(song_title + '_sky.txt')
    with open(sky_ascii_path, 'w+') as sky_ascii:
        write_ascii(sky_ascii, titlehead, headers, instrument_lines, RenderMode.SKYASCII)
    print('Your song converted to Sky notation is located at:', os.path.join(str(song_dir), sky_ascii_path))    
 
if song_input_mode in [InputMode.SKY, InputMode.SKYFILE, InputMode.SKYKEYBOARD]:
    western_ascii_path = os.path.join(song_title + '_western.txt')
    with open(western_ascii_path, 'w+') as western_ascii:
        write_ascii(western_ascii, titlehead, headers, instrument_lines, RenderMode.WESTERNASCII)
    print('Your song converted to Western notation is located at:', os.path.join(str(song_dir), western_ascii_path))    
       
os.chdir(mycwd)