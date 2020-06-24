# -*- coding: utf-8 -*-
import io, os
try:
    from importlib import resources as importlib_resources
except ImportError:
    import importlib_resources
from src.skymusic.resources import fonts, elements, css, js, html

A_root_png = io.BytesIO(importlib_resources.read_binary(elements, 'A-root.png'))
A_diamond_png = io.BytesIO(importlib_resources.read_binary(elements, 'A-diamond.png'))
A_circle_png = io.BytesIO(importlib_resources.read_binary(elements, 'A-circle.png'))
B_root_png = io.BytesIO(importlib_resources.read_binary(elements, 'B-root.png'))
B_diamond_png = io.BytesIO(importlib_resources.read_binary(elements, 'B-diamond.png'))
B_circle_png = io.BytesIO(importlib_resources.read_binary(elements, 'B-circle.png'))
C_root_png = io.BytesIO(importlib_resources.read_binary(elements, 'C-root.png'))
C_diamond_png = io.BytesIO(importlib_resources.read_binary(elements, 'C-diamond.png'))
C_circle_png = io.BytesIO(importlib_resources.read_binary(elements, 'C-circle.png'))
dead_png = io.BytesIO(importlib_resources.read_binary(elements, 'dead-note.png'))
A_unhighlighted_png = io.BytesIO(importlib_resources.read_binary(elements, 'A-unhighlighted.png'))   
B_unhighlighted_png = io.BytesIO(importlib_resources.read_binary(elements, 'B-unhighlighted.png'))   
C_unhighlighted_png = io.BytesIO(importlib_resources.read_binary(elements, 'C-unhighlighted.png'))
root_highlighted_pngs = [io.BytesIO(importlib_resources.read_binary(elements, 'root-highlighted-' + str(i) + '.png')) for i in range(1, 8)]
diamond_highlighted_pngs = [io.BytesIO(importlib_resources.read_binary(elements, 'diamond-highlighted-' + str(i) + '.png')) for i in range(1, 8)]
circle_highlighted_pngs = [io.BytesIO(importlib_resources.read_binary(elements, 'circle-highlighted-' + str(i) + '.png')) for i in range(1, 8)]

empty_chord_png = io.BytesIO(importlib_resources.read_binary(elements, 'empty-chord.png'))  # blank harp
unhighlighted_chord_png = io.BytesIO(importlib_resources.read_binary(elements, 'unhighlighted-chord.png'))  # harp with unhighlighted notes
broken_png = io.BytesIO(importlib_resources.read_binary(elements, 'broken-symbol.png'))
silent_png = io.BytesIO(importlib_resources.read_binary(elements, 'silent-symbol.png'))

with importlib_resources.path(fonts, 'NotoSansCJKjp-Regular.otf') as fp:
    font_path = str(fp)
    if not os.path.isfile(font_path):
        raise FileNotFoundError(f"Could not find fonts/{os.path.relpath(font_path, start=os.path.dirname(fonts.__file__))}")

try:
    css_buffer = io.StringIO(importlib_resources.read_text(css, 'main.css'))
except FileNotFoundError:
    print(f"\n***ERROR: could not find CSS file to embed it in HTML.\n")
    css_buffer = io.StringIO()

try:
    nav_html_buffer = io.StringIO(importlib_resources.read_text(html, 'navigation.html'))
except FileNotFoundError:
    print(f"\n***WARNING: could not find html navigation file to embed it in HTML.\n")
    nav_html_buffer = io.StringIO()

try:
    nav_js_buffer = io.StringIO(importlib_resources.read_text(js, 'navigation.js'))
except FileNotFoundError:
    print(f"\n***WARNING: could not find javascript navigation file to embed it in HTML.\n")
    nav_js_buffer = io.StringIO()
    
rel_css_path = '../css/main.css'
navigation_id = 'navigation'
SKY_MUSIC_URL = 'sky-music.github.io'

harp_font_size = 38
voice_font_size = 32
png_font_size = 36
png_title_font_size = 48
png_compress = 6

ICON_DELIMITER = '\s'
PAUSE = '.'
JIANPU_PAUSE = '0'
QUAVER_DELIMITER = '-'
JIANPU_QUAVER_DELIMITER = '^'
COMMENT_DELIMITER = '#'
REPEAT_INDICATOR = '*'
BROKEN_CHORD = 'X'
SKYJSON_CHORD_DELAY = 50 #Delay in ms below which 2 notes are considered a chord

MUSIC_MAKER_NAME = 'music_sheet_maker'
MUSIC_COG_NAME = 'music_cog'
SKY_MUSIC_WEBSITE_NAME = 'sky_music_website'
COMMAND_LINE_NAME = 'command_line'

DEFAULT_KEY = 'C'

MIDI_PITCHES = {'C': 60, 'C#': 61, 'Db': 61, 'D': 62, 'D#': 63, 'Eb': 63, 'E': 64, 'F': 65, 'F#': 66, 'Gb': 66, 'G': 67, 'G#': 68, 'Ab': 68, 'A': 69, 'A#': 70, 'Bb': 70, 'B': 71}
MIDI_SEMITONES = [0, 2, 4, 5, 7, 9, 11]  # May no longer be used when Western_scales is merged
