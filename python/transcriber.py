# Import from other files

from instrument import *
from notes import *
from parser import *

# Dash separated list of chords
CHORD_DELIMITER = '-'

ICON_DELIMITER = ' '
NOTE_WIDTH = 40

BLANK_ICON = '.'

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
print('Use QWERT ASDFG ZXCVB keys as the harp keyboard.')
print('Separate blocks of notes with \"' + ICON_DELIMITER + '\".')
print('Use \"' + BLANK_ICON + '\" for a blank block.')
print('If you want multiple colours within an icon, separate the colours with \"' + CHORD_DELIMITER + '\".')
print('============')
song_line = input('Type line: ')

instrument_lines = [] # A list of instrument_lines

while song_line:

    instrument_line = parse_line(song_line, ICON_DELIMITER, BLANK_ICON, CHORD_DELIMITER)

    instrument_lines.append(instrument_line)

    song_line = input('Type line: ')

print('============')
print('Press ENTER to skip the following.')
original_artists = input('Original artist(s): ')
transcript_writer = input('Transcribed by: ')
recommended_key = input('Recommended key: ')

# Render the song

with open(song_title + '.html', 'w+') as song_file:
    song_file.write('<!DOCTYPE html>\n')
    song_file.write('<html>\n')
    song_file.write('<head> <title>' + song_title + '</title> <link href="main.css" rel="stylesheet" /> </head>\n')

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
