import os, sys
this_dir = os.path.join(os.path.dirname(__file__))
SRC_ROOT = os.path.normpath(os.path.join(this_dir, '../../../'))
sys.path.append(SRC_ROOT)

FILE = 'senzenbonkura.jfj'

file_path = os.path.normpath(os.path.join(SRC_ROOT,'../test_songs',FILE))

from skymusic import FileUtils

print(os.path.isfile(file_path))
print(os.path.isdir(os.path.dirname(file_path)))

s = FileUtils.file_status(file_path)
print(s)

print(FileUtils.__edit_distance__('abcdef','abctyu'))
