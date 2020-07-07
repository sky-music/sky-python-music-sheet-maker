# -*- coding: utf-8 -*-
import io, os, importlib
try:
    from importlib import resources as importlib_resources
except ImportError:
    import importlib_resources

from src.skymusic.resources import fonts, elements, css, js

THEMES = {'light': False, 'dark': False}

PNGS = dict()

font_color = (0, 0, 0)
png_color = (255, 255, 255)
text_bkg = (255, 255, 255, 0)  # Transparent white
song_bkg = (255, 255, 255)  # White paper sheet

def get_default_theme():
    return list(THEMES)[0]

def load_theme(theme):
    global PNGS
    global font_color, png_color, text_bkg, song_bkg
    if theme not in THEMES:
        load_theme(get_default_theme())
    else:
        theme_module = importlib.import_module('.'+theme, 'src.skymusic.resources.elements')
        THEMES[theme] = True
        
        resources_names = importlib_resources.contents(theme_module)
        
        for name in resources_names:
            PNGS[os.path.splitext(name)[0]] =  io.BytesIO(importlib_resources.read_binary(theme_module, name))
        
        if theme == 'dark':
            font_color = (255, 255, 255)   #Discord colors
            png_color = (54, 57, 63)
            text_bkg = (54, 57, 63, 0)  # Transparent dark
            song_bkg = (54, 57, 63)  # White paper sheet
        

with importlib_resources.path(fonts, 'NotoSansCJKjp-Regular.otf') as fp:
    font_path = str(fp)
    if not os.path.isfile(font_path):
        raise FileNotFoundError(f"Could not find fonts/{os.path.relpath(font_path, start=os.path.dirname(fonts.__file__))}")

try:
    svg_css_buffer = io.StringIO(importlib_resources.read_text(css, 'svg.css'))
except FileNotFoundError:
    print(f"\n***ERROR: could not find svg.css file to embed it in HTML.\n")
    svg_css_buffer = io.StringIO()

try:
    html_css_buffer = io.StringIO(importlib_resources.read_text(css, 'html.css'))
except FileNotFoundError:
    print(f"\n***ERROR: could not find html.css file to embed it in HTML.\n")
    html_css_buffer = io.StringIO()
    
try:
    common_css_buffer = io.StringIO(importlib_resources.read_text(css, 'common.css'))
except FileNotFoundError:
    print(f"\n***ERROR: could not find common.css file to embed it.\n")
    common_css_buffer = io.StringIO()

'''
try:
    nav_html_buffer = io.StringIO(importlib_resources.read_text(html, 'navigation.html'))
except FileNotFoundError:
    print(f"\n***WARNING: could not find html navigation file to embed it in HTML.\n")
    nav_html_buffer = io.StringIO()
'''
    
rel_css_path = '../css/main.css'
offline_scripts_urls = []
online_scripts_urls = ['/js/navigationTableScript.js', '/js/sheetDarkModeScript.js', '/js/sheetDownloadScript.js']

script_buffers = []
for script in offline_scripts_urls:
    try:
        script_buffers.append(io.StringIO(importlib_resources.read_text(js, script)))
    except FileNotFoundError:
        print(f"\n***WARNING: could not find javascript {script} file to embed it in HTML.\n")
        script_buffers.append(io.StringIO())
    

harp_font_size = 38
voice_font_size = 32
png_font_size = 36
png_title_font_size = 48
png_compress = 6

MAX_NUM_FILES = 15

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

