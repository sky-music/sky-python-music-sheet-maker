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
        print(str(i) + ") Type on keyboard as you would in Sky:\n   " + myparser.keyboard_layout.replace(' ','\n   '))
        mydict[i] = InputModes.SKYKEYBOARD
    if InputModes.SKY in modes:
        i += 1
        print(str(i) + ") Sky colum/row notation:\n   A1 A2 A3 A4 A5\n   B1 B2 B3 B4 B5\n   C1 C2 C3 C4 C5")
        mydict[i] = InputModes.SKY
    if InputModes.WESTERN in modes:
        i += 1
        print(str(i) + ") Western (note name + octave, e.g. C4 D4 E4 ..., or do4 re4 mi4 ...)")    
        mydict[i] = InputModes.WESTERN
    if InputModes.JIANPU in modes:
        i += 1
        print(str(i) + ") Jianpu (note names as 1 2 3 4 5 6 7, followed by + or - for octaves)") 
        mydict[i] = InputModes.JIANPU
    if InputModes.WESTERNCHORDS in modes:
        i += 1
        print(str(i) + ") Guitar chord name (AC D E F G A B):") 
        mydict[i] = InputModes.WESTERNCHORDS
    try:
        song_notation = int(input("Mode (1-" + str(i) + "): ").strip())
    except ValueError:
        return InputModes.SKY
    return mydict[song_notation]


def is_file(string):
    isfile = False
    fp = os.path.join(SONG_DIR, os.path.normpath(string))
    isfile = os.path.isfile(fp)
    
    if not(isfile):
        fp = os.path.join(SONG_DIR, os.path.normpath(string+'.txt'))
        isfile = os.path.isfile(fp)
    
    if not(isfile):
        fp = os.path.join(os.path.normpath(string))
        isfile = os.path.isfile(fp)

    if not(isfile):
        splitted = os.path.splitext(string)
        if len(splitted[0])>0 and len(splitted[1])>0 and len(splitted[1])<=5: #then probably a file name
            while not(isfile) and len(fp)>2:
                print('\nFile not found.')
                isfile, fp = is_file(input('File name (in ' + os.path.normpath(SONG_DIR) + '/): ').strip())  
    
    return isfile, fp

# Parameters that can be changed by advanced users
QUAVER_DELIMITER = '-' # Dash-separated list of chords
ICON_DELIMITER = ' ' # Chords separation
NOTE_WIDTH = "1em" #Any CSS-compatible unit can be used
PAUSE = '.'
COMMENT_DELIMITER = '#' # Lyrics delimiter, can be used for comments
SONG_DIR = 'songs'
CSS_PATH = 'css/main.css'
CSS_MODE = CSSModes.HREF

myparser = Parser() # Create a parser object

### Change directory
mycwd = os.getcwd()
os.chdir("..")

### MAIN SCRIPT
 
print('===== VISUAL MUSIC SHEETS FOR SKY:CHILDREN OF THE LIGHT =====')
print('\nAccepted music notes formats:')
print("\n* Typing on keyboard as you would in Sky:\n   " + myparser.keyboard_layout.replace(' ','\n   '))
print("\n* Sky colum/row notation:\n   A1 A2 A3 A4 A5\n   B1 B2 B3 B4 B5\n   C1 C2 C3 C4 C5")
print("\n* Western (note name + octave, e.g. C4 D4 E4 ..., or do4 re4 mi4 ...)")    
print("\n* Jianpu (note names as 1 2 3 4 5 6 7, followed by + or - for octaves)") 
#print("  * Guitar chord name (AC D E F G A B):") 
print('\nNotes composing a chord must be glued together (e.g. A1B1C1).')
print('Separate chords with \"' + ICON_DELIMITER + '\".')
print('Use \"' + PAUSE + '\" for a silence (rest).')
print('Use \"' + QUAVER_DELIMITER + '\" to link notes within an icon, for triplets, quavers... (e.g. A1-B1-C1).')
print('Add x2 after a chord to indicate repetition.')
print('Sharps # and flats b (semitones) are not supported in Sky.')
print('============================================================')


first_line = input('Type or copy-paste notes, or enter file name (in ' + os.path.normpath(SONG_DIR) + '/): ').strip()

isfile, fp = is_file(first_line)

song_lines = []
if isfile:
    try:
        for song_line in open(fp,mode='r'):
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


possible_modes = myparser.detect_input_type(song_lines, ICON_DELIMITER, PAUSE, QUAVER_DELIMITER, COMMENT_DELIMITER)

if len(possible_modes) > 1:
    print('Several possible notations detected.')
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
    musickeys = myparser.find_key(song_lines, COMMENT_DELIMITER, song_notation) 
    if len(musickeys) == 0:
        print("\nYour song cannot be transposed exactly in Sky.")
    else:
        print("\nYour song can be transposed in Sky with the following keys: " + str(musickeys))
        print('Transposition is not implemented yet. Assuming you will play in \'C\'.')

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
    instrument_line = myparser.parse_line(song_line.strip(), ICON_DELIMITER, PAUSE, QUAVER_DELIMITER, COMMENT_DELIMITER, song_notation, note_shift)            
    mysong.add_line(instrument_line)


print('============================================================')
if mysong.get_num_broken()/max(1,mysong.get_num_instruments())<0.05:
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

html_path = os.path.join(SONG_DIR, song_title + '.html')
html_path = mysong.write_html(html_path, NOTE_WIDTH, CSS_MODE, CSS_PATH)

if html_path != '':
    print('============================================================')
    print('Your song in HTML is located at:', os.path.join(str(SONG_DIR), html_path))

svg_path0 = os.path.join(SONG_DIR, song_title + '.svg')
filenum, svg_path = mysong.write_svg(svg_path0, CSS_MODE, CSS_PATH)

if svg_path != '':
    print('--------------------------------------------------')
    print('Your song in SVG is located in', os.path.join(str(SONG_DIR)))
    print('Your song has been splitted in ' + str(filenum+1) + ' files '
          'between ' + os.path.split(svg_path0)[1] + ' and ' + os.path.split(svg_path)[1])

png_path0 = os.path.join(SONG_DIR, song_title + '.png')
filenum, png_path = mysong.write_png(png_path0)

if png_path != '':
    print('--------------------------------------------------')
    print('Your song in PNG is located in:', os.path.join(str(SONG_DIR)))
    print('Your song has been splitted in ' + str(filenum+1) + ' files '
          'between ' + os.path.split(png_path0)[1] + ' and ' + os.path.split(png_path)[1])

if song_notation in [InputModes.WESTERN, InputModes.JIANPU, InputModes.WESTERNCHORDS]:
    sky_ascii_path = os.path.join(SONG_DIR, song_title + '_sky.txt')
    res = mysong.write_ascii(sky_ascii_path, RenderModes.SKYASCII)
    if sky_ascii_path != '':
        print('--------------------------------------------------')
        print('Your song converted to Sky notation is located at:', os.path.join(str(SONG_DIR), sky_ascii_path))    
 
if song_notation in [InputModes.SKY, InputModes.SKYKEYBOARD]:
    western_ascii_path = os.path.join(SONG_DIR, song_title + '_western.txt')
    western_ascii_path = mysong.write_ascii(western_ascii_path, RenderModes.WESTERNASCII)
    if western_ascii_path != '':
        print('--------------------------------------------------')
        print('Your song in TXT converted to Western notation is located at:', os.path.join(str(SONG_DIR), western_ascii_path))    

os.chdir(mycwd)