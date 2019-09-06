# Import from other files

from instrument import Harp
from notes import NoteRoot, NoteCircle, NoteDiamond
from modes import InputMode, RenderMode
from render import render_instrument_line, render_instrument_lines

import os as os

### Parser

class Parser:

    def __init__(self):

        self.keyboard_position_map = {'Q': (0, 0), 'W': (0, 1), 'E': (0, 2), 'R': (0, 3), 'T': (0, 4), 'A': (1, 0), 'S': (1, 1), 'D': (1, 2), 'F': (1, 3), 'G': (1, 4), 'Z': (2, 0), 'X': (2, 1), 'C': (2, 2), 'V': (2, 3), 'B': (2, 4)}
        self.alphanumeric_position_map = {'A1': (0, 0), 'A2': (0, 1), 'A3': (0, 2), 'A4': (0, 3), 'A5': (0, 4), 'B1': (1, 0), 'B2': (1, 1), 'B3': (1, 2), 'B4': (1, 3), 'B5': (1, 4), 'C1': (2, 0), 'C2': (2, 1), 'C3': (2, 2), 'C4': (2, 3), 'C5': (2, 4)}

    def get_keyboard_position_map(self):
        return self.keyboard_position_map

    def get_alphanumeric_position_map(self):
        return self.alphanumeric_position_map

    def parse_icon(self, icon, delimiter, input_mode):

        if input_mode == InputMode.KEYBOARD:
            tokens = icon.split(delimiter)
            return tokens
        elif input_mode == InputMode.ALPHANUMERIC:
            tokens = icon.split(delimiter)

    def parse_line(self, line, icon_delimiter, blank_icon, chord_delimiter, input_mode):

        '''
        Returns instrument_line: a list of chord images
        '''
        #TODO: HAVENT accounted for double spaces and trailing/leading spaces
        icons = line.split(icon_delimiter)
        instrument_line = []

        #TODO: Implement logic for parsing line vs single icon.
        for icon in icons:
            chords = self.parse_icon(icon, chord_delimiter, input_mode)
            results = self.parse_chords(chords, blank_icon, input_mode)
            chord_image = results[0]
            harp_is_highlighted = results[1]

            harp = Harp()
            harp.set_is_highlighted(harp_is_highlighted)
            harp.set_chord_image(chord_image)


            instrument_line.append(harp)

        return instrument_line

    def map_note_to_position(self, note, blank_icon, input_mode):

        '''
        Returns a tuple containing the row index and the column index of the note's position.
        '''

        if input_mode == InputMode.KEYBOARD:
            position_map = self.get_keyboard_position_map()
        if input_mode == InputMode.ALPHANUMERIC:
            position_map = self.get_alphanumeric_position_map()

        note = note.upper()
        if note in position_map.keys():
            return position_map[note] # Expecting a tuple
        #elif letter == BLANK_ICON:
        #    print(letter)
        #    raise BlankIconError
        elif note == blank_icon:
            #TODO: Implement support for breaks/empty harps
            #Define a custom InvalidLetterException
            raise KeyError
        else:
            raise KeyError

    def parse_chords(self, chords, blank_icon, input_mode):

        is_empty = True
        chord_image = {}

        for chord_idx, chord in enumerate(chords):

            # Create an image of the harp's chords
            # For each chord, set the highlighted state of each note accordingly (whether True or False)

            if input_mode == InputMode.KEYBOARD:

                for note in chord:
                    #Except InvalidLetterException
                    try:
                        highlighted_note_position = self.map_note_to_position(note, blank_icon, input_mode)
                    except KeyError:
                        pass
                    else:
                        is_empty = False
                        chord_image[highlighted_note_position] = {}
                        chord_image[highlighted_note_position][chord_idx] = True

            elif input_mode == InputMode.ALPHANUMERIC:
                try:
                    highlighted_note_position = self.map_note_to_position(chord, blank_icon, input_mode)
                except KeyError:
                    pass
                else:
                    chord_image[highlighted_note_position][chord_idx] = True

        results = [chord_image, not(is_empty)]
        return results


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

print('Use these keys as the music keyboard:')
print('QWERT')
print('ASDFG')
print('ZXCVB\n')

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
song_full_file_path = os.path.join(str(root_dir), song_file_path)
print('Your song is located at', song_full_file_path)
