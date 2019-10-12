# Import from other files

from instrument import Harp
from notes import NoteRoot, NoteCircle, NoteDiamond
from modes import InputMode, RenderMode
from render import render_instrument_line, render_instrument_lines
from textwrap import wrap
import os as os
import re

### Parser

class Parser:

    def __init__(self):

        if (os.getenv('LANG') == 'fr') or (os.getenv('LANG') == 'be'):
            self.keyboard_position_map = {'A': (0, 0), 'Z': (0, 1), 'E': (0, 2), 'R': (0, 3), 'T': (0, 4), 'Q': (1, 0), 'S': (1, 1), 'D': (1, 2), 'F': (1, 3), 'G': (1, 4), 'W': (2, 0), 'X': (2, 1), 'C': (2, 2), 'V': (2, 3), 'B': (2, 4)}
            self.keyboard_layout="AZERT QSDFG WXCVB"
        else:
            self.keyboard_position_map = {'Q': (0, 0), 'W': (0, 1), 'E': (0, 2), 'R': (0, 3), 'T': (0, 4), 'A': (1, 0), 'S': (1, 1), 'D': (1, 2), 'F': (1, 3), 'G': (1, 4), 'Z': (2, 0), 'X': (2, 1), 'C': (2, 2), 'V': (2, 3), 'B': (2, 4)}
            self.keyboard_layout="QWERT ASDFG ZXCVB"

        self.sky_position_map = {
                'A1': (0, 0), 'A2': (0, 1), 'A3': (0, 2), 'A4': (0, 3), 'A5': (0, 4),
                'B1': (1, 0), 'B2': (1, 1), 'B3': (1, 2), 'B4': (1, 3), 'B5': (1, 4),
                'C1': (2, 0), 'C2': (2, 1), 'C3': (2, 2), 'C4': (2, 3), 'C5': (2, 4)
                }
        self.western_position_map = {
                'D1': (-4, 0), 'E1': (-4, 1), 'F1': (-4, 2), 'G1': (-4, 3), 'A1': (-4, 4),
                'B1': (-3, 0), 'C2': (-3, 1), 'D2': (-3, 2), 'E2': (-3, 3), 'F2': (-3, 4),
                'G2': (-2, 0), 'A2': (-2, 1), 'B2': (-2, 2), 'C3': (-2, 3), 'D3': (-2, 4),
                'E3': (-1, 0), 'F3': (-1, 1), 'G3': (-1, 2), 'A3': (-1, 3), 'B3': (-1, 4),
                'C4': (0, 0), 'D4': (0, 1), 'E4': (0, 2), 'F4': (0, 3), 'G4': (0, 4),
                'A4': (1, 0), 'B4': (1, 1), 'C5': (1, 2), 'D5': (1, 3), 'E5': (1, 4),
                'F5': (2, 0), 'G5': (2, 1), 'A5': (2, 2), 'B5': (2, 3), 'C6': (2, 4),
                'D6': (3, 0), 'E6': (3, 1), 'F6': (3, 2), 'G6': (3, 3), 'A6': (3, 4),
                'B6': (4, 0), 'C7': (4, 1), 'D7': (4, 2), 'E7': (4, 3), 'F7': (4, 4)
                }
        self.jianpu_position_map = {
                '2---': (-4, 0), '3---': (-4, 1), '4---': (-4, 2), '5---': (-4, 3), '6---': (-4, 4),
                '7---': (-3, 0), '1--': (-3, 1), '2--': (-3, 2), '3--': (-3, 3), '4--': (-3, 4),
                '5--': (-2, 0), '6--': (-2, 1), '7--': (-2, 2), '1-': (-2, 3), '2-': (-2, 4),
                '3-': (-1, 0), '4-': (-1, 1), '5-': (-1, 2), '6-': (-1, 3), '7-': (-1, 4),
                '1': (0, 0), '2': (0, 1), '3': (0, 2), '4': (0, 3), '5': (0, 4),
                '6': (1, 0), '7': (1, 1), '1+': (1, 2), '2+': (1, 3), '3+': (1, 4),
                '4+': (2, 0), '5+': (2, 1), '6+': (2, 2), '7+': (2, 3), '1++': (2, 4),
                '2++': (3, 0), '3++': (3, 1), '4++': (3, 2), '5++': (3, 3), '6++': (3, 4),
                '7++': (4, 0), '1+++': (4, 1), '2+++': (4, 2), '3+++': (4, 3), '4+++': (4, 4)
                }

    def get_keyboard_position_map(self):
        return self.keyboard_position_map

    def get_sky_position_map(self):
        return self.sky_position_map

    def get_western_position_map(self):
        return self.western_position_map

    def get_jianpu_position_map(self):
        return self.jianpu_position_map

    def parse_icon(self, icon, QUAVER_DELIMITER, input_mode):

        tokens = icon.split(QUAVER_DELIMITER)
        return tokens

    def parse_line(self, line, icon_delimiter, blank_icon, QUAVER_DELIMITER, input_mode, octave_shift=0):
        '''
        Returns instrument_line: a list of chord images
        '''
        icons = line.rstrip().lstrip().replace(icon_delimiter+icon_delimiter,icon_delimiter).split(icon_delimiter)
        instrument_line = []

        #TODO: Implement logic for parsing line vs single icon.
        for icon in icons:
            chords = self.parse_icon(icon, QUAVER_DELIMITER, input_mode)
            results = self.parse_chords(chords, blank_icon, input_mode, octave_shift)
            chord_image = results[0]
            harp_is_highlighted = results[1]

            harp = Harp()
            harp.set_is_highlighted(harp_is_highlighted)
            harp.set_chord_image(chord_image)

            instrument_line.append(harp)

        return instrument_line

    def map_note_to_position(self, note, blank_icon, input_mode, octave_shift=0):
        '''
        Returns a tuple containing the row index and the column index of the note's position.
        '''
        if input_mode == InputMode.KEYBOARD:
            position_map = self.get_keyboard_position_map()
        elif input_mode == InputMode.SKY or input_mode == InputMode.SKYFILE:
            position_map = self.get_sky_position_map()
        elif input_mode == InputMode.WESTERN or input_mode == InputMode.WESTERNFILE:
            position_map = self.get_western_position_map()
        elif input_mode == InputMode.JIANPU or input_mode == InputMode.JIANPUFILE:
            position_map = self.get_jianpu_position_map()
        else:
            position_map = self.get_keyboard_position_map()
        note = note.upper()

        if note in position_map.keys():
            pos=position_map[note] #tuple
            idx=pos[0]*5+pos[1]
            idxshift=idx+7*octave_shift
            pos=(int(idxshift/5),idxshift-5*int(idxshift/5))
            if pos>=(0,0) and pos<=(2,4):
                return pos
            else:
                raise KeyError
        #elif letter == BLANK_ICON:
        #    print(letter)
        #    raise BlankIconError
        elif note == blank_icon:
            #TODO: Implement support for breaks/empty harps
            #Define a custom InvalidLetterException
            raise KeyError
        else:
            raise KeyError

    def parse_chords(self, chords, blank_icon, input_mode, octave_shift=0):

        is_empty = True
        chord_image = {}
        for chord_idx, chord in enumerate(chords):
            # Create an image of the harp's chords
            # For each chord, set the highlighted state of each note accordingly (whether True or False)
            if input_mode in [InputMode.SKY, InputMode.SKYFILE, InputMode.WESTERN, InputMode.WESTERNFILE]:
                chord=wrap(chord, 2) # Notes are always 2 character-long in Sky and Western notations

            if input_mode in [InputMode.JIANPU, InputMode.JIANPUFILE]:
                chord=re.sub('([1-9])',' \\1',chord).split()

            for note in chord: # Chord is a list of notes
                #Except InvalidLetterException
                try:
                    highlighted_note_position = self.map_note_to_position(note, blank_icon, input_mode, octave_shift)
                except KeyError:
                    pass
                else:
                    is_empty = False
                    chord_image[highlighted_note_position] = {}
                    chord_image[highlighted_note_position][chord_idx] = True

        results = [chord_image, not(is_empty)]
        return results


# Dash separated list of chords

QUAVER_DELIMITER = '-'
JIANPU_QUAVER_DELIMITER = '^'

ICON_DELIMITER = ' '
NOTE_WIDTH = "1em"
BLANK_ICON = '.'

parser = Parser() # Create a parser object

### Define Errors
class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class BlankIconError(Error):
    pass

### Change directory
mycwd = os.getcwd()
os.chdir("..")
if not os.path.exists('songs'):
    os.makedirs('songs')
os.chdir("songs")
song_dir=os.getcwd()


### MAIN SCRIPT

#print('===== NEW SONG =====')
#print("Choose input mode:\n")
#print("1) Use " + Parser().keyboard_layout + " as keyboard.")
#print("2) Type directly using sky notation (A1 A2 A3 A4 A5, B1 B2 B3 B4 B5, C1 C2 C3 C4 C5)")
#print("3) Import sheet from a file using Sky notation.")
#print("4) Type directly using *musical* notation ().")
#print("5) Import sheet from a file using *musical* notation.")

print('===== NEW SONG =====')
print("Choose input mode:\n")
print("1) Use " + Parser().keyboard_layout + " as keyboard.")
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

if song_input_mode != 1 and song_notation != 1:
    try:
        octave_shift = int(input('Octave shift (-3 -2 -1 0 1 2 3): ').strip())
    except ValueError:
        octave_shift = 0
else:
    octave_shift = 0

if song_input_mode == 1:
    song_input_mode = InputMode.KEYBOARD
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
    song_input_mode = InputMode.KEYBOARD

if song_input_mode == InputMode.JIANPU or song_input_mode == InputMode.JIANPUFILE:
    QUAVER_DELIMITER = JIANPU_QUAVER_DELIMITER

print('\nSeparate blocks of notes with \"' + ICON_DELIMITER + '\".')
print('Use \"' + BLANK_ICON + '\" for a blank block.')
print('If you want multiple colours within an icon, separate the colours with \"' + QUAVER_DELIMITER + '\".')
print('=========================')

instrument_lines = [] # A list of instrument_lines

if song_input_mode in [InputMode.SKYFILE, InputMode.WESTERNFILE, InputMode.JIANPUFILE]:
    fp = os.path.normpath(input('File name (in ' + os.path.normpath('../songs/') + '): '))
    try:
        fic = open(fp,mode='r')
        print(['Opening file: ' + os.path.abspath(fp)])
        for song_line in fic:
            instrument_line = parser.parse_line(song_line.rstrip(), ICON_DELIMITER, BLANK_ICON, QUAVER_DELIMITER, song_input_mode, octave_shift)
            instrument_lines.append(instrument_line)

        fic.close()
    except (OSError, IOError) as err:
         print('Error opening file.')
         raise err
else:
    song_line = input('Type line: ')
    while song_line:
        instrument_line = parser.parse_line(song_line, ICON_DELIMITER, BLANK_ICON, QUAVER_DELIMITER, song_input_mode, octave_shift)
        instrument_lines.append(instrument_line)
        song_line = input('Type line: ')


print('============')
print('Press ENTER to skip the following.')
musical_key = input('Recommended musical key: ')
song_title = input('Song title (used for the file name): ')
original_artists = input('Original artist(s): ')
transcript_writer = input('Transcribed by: ')


# Render the song


song_file_path = os.path.join(song_title + '.html')

with open(song_file_path, 'w+') as song_file:
    song_file.write('<!DOCTYPE html>\n')
    song_file.write('<html>\n')
    song_file.write('<head> <title>' + song_title + '</title> <link href="../css/main.css" rel="stylesheet" /> <meta charset="utf-8"/> </head>\n')

    song_file.write('<body>\n')
    song_file.write('<h1> ' + song_title + ' </h1>\n')

    if original_artists:
        song_file.write('<p> <b>Original Artist(s):</b> ' + original_artists + ' </p>\n')
    if transcript_writer:
        song_file.write('<p> <b> Transcript:</b> ' + transcript_writer + ' </p>\n')
    if musical_key:
        song_file.write('<p> <b> Recommended key:</b> ' + musical_key + ' </p>\n')

    song_file.write('<div id="transcript">\n\n')


    song_file.write(render_instrument_lines(instrument_lines, NOTE_WIDTH, RenderMode.VISUAL))


    song_file.write('</div>\n')
    song_file.write('</body>\n')

    song_file.write('</html>\n')

print('============')
song_full_file_path = os.path.join(str(song_dir), song_file_path)
print('Your song is located at', song_full_file_path)

if song_input_mode in [InputMode.WESTERN, InputMode.JIANPU, InputMode.WESTERNFILE, InputMode.JIANPUFILE]:
    ascii_file_path = os.path.join(song_title + '_ascii.txt')
    with open(ascii_file_path, 'w+') as ascii_file:
        ascii_file.write(render_instrument_lines(instrument_lines, NOTE_WIDTH, RenderMode.ASCII))
    ascii_full_file_path = os.path.join(str(song_dir), ascii_file_path)
    print('Your converted song is located at', ascii_full_file_path)

os.chdir(mycwd)
