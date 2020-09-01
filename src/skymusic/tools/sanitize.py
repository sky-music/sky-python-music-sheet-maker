# -*- coding: utf-8 -*-
import os, re

if __name__ == '__main__':
    import sys
    project_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../'))
    if project_path not in sys.path:
        sys.path.append(project_path)


songs_dir = "../../../test_songs/"
filename = "merry.txt"


filepath = os.path.join(songs_dir, filename)
with open(filepath, 'r', encoding='utf-8', errors='ignore') as fp:

    song = fp.read()

song = re.sub(',',' . ', song)
song = re.sub('(\s){2,}',r'\1', song)
chord_matches = re.finditer('(\[(?:(?:\w+\s*)+)\])', song)
for match in chord_matches:
    notes = re.sub('\s|\[|\]|\(|\)','',match.group(0))
    song = song.replace(match.group(0), notes)

song = song.replace('[','')
song = song.replace(']','')
song = song.strip()

(base, ext) = os.path.splitext(filename)
new_filename = base + '_2' + ext
new_filepath = os.path.join(songs_dir, new_filename)

with open(new_filepath, 'w', encoding='utf-8') as fp2:
    
    fp2.write(song)
