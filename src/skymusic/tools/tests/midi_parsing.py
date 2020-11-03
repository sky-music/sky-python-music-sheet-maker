import os
from mido import MidiFile
from io import BytesIO


this_file = os.path.abspath(__file__)

fileroot = "../../../../test_songs/"
filename = 'supermario.mid'
filepath = os.path.join(fileroot, filename)


with open(filepath, mode='rb') as fp:
    lines = fp.readlines()  # Returns a list of bytes
    
#print(lines)

midi_bytes = b''.join(lines)

print(midi_bytes)

buffer = BytesIO()
buffer.write(midi_bytes)
buffer.seek(0)
mid = MidiFile(file=buffer)

#mid = MidiFile(filepath)


for i, track in enumerate(mid.tracks):
    print('Track {}: {}'.format(i, track.name))
    for msg in track:
        print(msg)
        

print(isinstance(mid,MidiFile))
