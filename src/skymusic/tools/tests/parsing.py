import os, sys
this_dir = os.path.join(os.path.dirname(__file__))
SRC_ROOT = os.path.normpath(os.path.join(this_dir, '../../../'))
sys.path.append(SRC_ROOT)

from skymusic import Lang
from skymusic.resources import Resources
from skymusic.parsers import song_parser

FILE = 'brackets.txt'

p = song_parser.SongParser(maker=None)

with open(os.path.normpath(os.path.join(SRC_ROOT,'../test_songs',FILE))) as fp:
    lines = fp.readlines()
    
modes = p.get_possible_modes(lines)

p.set_input_mode(modes[0])

l = lines[3]
print('line=\n'+l)

l = p.sanitize_line(l)
print('sanitized=\n'+l)

icons = p.split_line(l)
print('icons= '+str(icons))

for icon in icons:
    chords = p.split_icon(icon)
    print(chords)
