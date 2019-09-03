# Import from other files

from instrument import Harp
from notes import NoteRoot, NoteCircle, NoteDiamond
from parser import Parser
from modes import InputMode, RenderMode
from render import render_instrument_line, render_instrument_lines

import os as os

# Dash separated list of chords
CHORD_DELIMITER = '-'

ICON_DELIMITER = ' '
NOTE_WIDTH = 40

BLANK_ICON = '.'

parser = Parser()

### Define Errors
class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class BlackIconError(Error):
    pass


### Note collection class


print('==NEW SONG==')
song_title = input('Song title: ')
print('============')

#print("CHOOSE INPUT MODE")
#print("1) Use QWERT ASDFG ZXCVB as keyboard.")
#print("2) Use A1 A2 A3 A4 A5, B1 B2 B3 B4 B5, C1 C2 C3 C4 C5 directly.")

#try:
#    song_input_mode = int(input("Mode (Type '1' or '2'): ").strip())
#except ValueError:
#    song_input_mode = 1

song_input_mode = 1

if song_input_mode == 1:
    song_input_mode = InputMode.KEYBOARD
elif song_input_mode == 2:
    song_input_mode = InputMode.ALPHANUMERIC
else:
    song_input_mode == InputMode.KEYBOARD

print('Separate blocks of notes with \"' + ICON_DELIMITER + '\".')
print('Use \"' + BLANK_ICON + '\" for a blank block.')
print('If you want multiple colours within an icon, separate the colours with \"' + CHORD_DELIMITER + '\".')
print('============')
song_line = input('Type line: ')

instrument_lines = [] # A list of instrument_lines

while song_line:

    instrument_line = parser.parse_line(song_line, ICON_DELIMITER, BLANK_ICON, CHORD_DELIMITER, song_input_mode)

    instrument_lines.append(instrument_line)

    song_line = input('Type line: ')

print('============')
print('Press ENTER to skip the following.')
original_artists = input('Original artist(s): ')
transcript_writer = input('Transcribed by: ')
recommended_key = input('Recommended key: ')

# Render the song

mycwd = os.getcwd()
os.chdir("..")

root_dir = os.getcwd()

if not os.path.exists('songs'):
    os.makedirs('songs')

song_file_path = os.path.join('songs', song_title + '.html')

with open(song_file_path, 'w+') as song_file:
    song_file.write('<!DOCTYPE html>\n')
    song_file.write('<html>\n')
    song_file.write('<head> <title>' + song_title + '</title> <link href="../css/main.css" rel="stylesheet" /> </head>\n')

    song_file.write('<body>\n')
    song_file.write('<h1> ' + song_title + ' </h1>\n')

    if original_artists:
        song_file.write('<p> <b>Original Artist(s):</b> ' + original_artists + ' </p>\n')
    if transcript_writer:
        song_file.write('<p> <b> Transcript:</b> ' + transcript_writer + ' </p>\n')
    if recommended_key:
        song_file.write('<p> <b> Recommended key:</b> ' + recommended_key + ' </p>\n')

    song_file.write('<div id="transcript">\n\n')


    song_file.write(render_instrument_lines(instrument_lines, NOTE_WIDTH))


    song_file.write('</div>\n')
    song_file.write('</body>\n')

    song_file.write('</html>\n')

os.chdir(mycwd)

print('============')
print('Your song is located at ' + str(root_dir) + '/' + str(song_file_path))
