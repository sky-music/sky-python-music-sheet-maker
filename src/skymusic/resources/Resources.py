# -*- coding: utf-8 -*-
import io, os, importlib
try:
    from importlib import resources as importlib_resources
except ImportError:
    import importlib_resources
from skymusic.resources import fonts, png, css, js


def get_default_theme():
    global THEMES
    return list(THEMES)[0]

def detect_themes():
    '''
    Detects available themes by listing directories inside ./css/    
    '''
    css_dir = os.path.dirname(css.__file__)
    contents = os.listdir(css_dir)
    themes = [content for content in contents if os.path.isdir(os.path.join(css_dir, content))]
    return themes

def load_theme(theme):
    '''
    Loads CSS and PNG files as string and bytes buffers respectively, for a theme whose name 'theme' must be defined in the THEMES list
    '''
    global PNGS, CSS, THEMES
    global font_color, png_color, text_bkg, song_bkg
    
    if theme not in THEMES:
        load_theme(get_default_theme())
    elif THEMES[theme] is False:
        
        png_module = importlib.import_module('.'+theme, png.__name__)
        
        png_files = importlib_resources.contents(png_module)
        
        if not png_files:
            print(f"\n*** ERROR: could not find any PNG file to embed from {png_module}. ***\n")   
        
        png_files = [file for file in png_files if os.path.splitext(file)[1] == '.png']
        
        for png_file in png_files:
            PNGS[os.path.splitext(png_file)[0]] =  io.BytesIO(importlib_resources.read_binary(png_module, png_file))

        css_module = importlib.import_module('.'+theme, css.__name__)        
        
        css_files = importlib_resources.contents(css_module)
        if not css_files:
            print(f"\n*** ERROR: could not find any CSS file to embed from {css_module}. ***\n")     
        
        css_files = [file for file in css_files if os.path.splitext(file)[1] == '.css']
        
        for css_file in css_files:
            CSS[os.path.splitext(css_file)[0]] =  io.StringIO(importlib_resources.read_text(css_module, css_file))
                                               
        if theme == 'dark':
            font_color = (255, 255, 255)   #Discord colors
            png_color = (54, 57, 63)
            text_bkg = (54, 57, 63, 0)  # Transparent dark
            song_bkg = (54, 57, 63)  # White paper sheet
            
        THEMES[theme] = True

THEMES = {'light': False, 'dark': False}
# THEMES = detect_themes()
# Must be initialized with the theme names, which must correspond to directories in tue css and png folders

CSS = {'svg': io.StringIO(), 'html': io.StringIO(), 'common': io.StringIO()}
# Must be initialized with the base names of the CSS files inside each theme directory in ./css/{theme}/
# At the moment the svg renderer needs svg.css, the html one html.css, and both need  common.css. The svg to png converter also needs svg.css

PNGS = dict()
#Will be populated by load_theme()

font_color = (0, 0, 0)
png_color = (255, 255, 255)
text_bkg = (255, 255, 255, 0)  # Transparent white
song_bkg = (255, 255, 255)  # White paper sheet                                                                        

with importlib_resources.path(fonts, 'NotoSansCJKjp-Bold.otf') as fp:
    font_path = str(fp)
    if not os.path.isfile(font_path):
        raise FileNotFoundError(f"Could not find fonts/{os.path.relpath(font_path, start=os.path.dirname(fonts.__file__))}")

rel_css_path = '../css/main.css' # For IMPORT and HREF methods of embedding css files
offline_scripts_urls = [] #Embedded in HTML files
online_scripts_urls = ['/js/navigationTableScript.js', '/js/sheetDarkModeScript.js', '/js/sheetDownloaderScript.js'] # linked in HTML files, stored on sky-music.github.io

script_buffers = []
for script in offline_scripts_urls:
    try:
        script_buffers.append(io.StringIO(importlib_resources.read_text(js, script)))
    except FileNotFoundError:
        print(f"\n***WARNING: could not find javascript {script} file to embed it in HTML.\n")
        script_buffers.append(io.StringIO())

# To generate a link by sky-musiv.herokuapp.com
skyjson_api_url = "https://sky-music.herokuapp.com/api/generateTempSong"
skyjson_api_key = ""    

harp_font_size = 38
voice_font_size = 32
png_font_size = 36
png_title_font_size = 48
png_compress = 6

MAX_FILENAME_LENGTH = 127
MAX_NUM_FILES = 15

ICON_DELIMITER = '\s'
PAUSE = '.'
JIANPU_PAUSE = '0'
QUAVER_DELIMITER = '-'
JIANPU_QUAVER_DELIMITER = '^'
LYRIC_DELIMITER = '#'
METADATA_DELIMITER = '#$'
REPEAT_INDICATOR = '*'
BROKEN_HARP= 'X'
SKYJSON_CHORD_DELAY = 50 #Delay in ms below which 2 notes are considered a chord
DEFAULT_BPM = 220
PARSING_START_OCTAVE = 1
RENDERING_START_OCTAVE = 4

MUSIC_MAKER_NAME = 'music_sheet_maker'
MUSIC_COG_NAME = 'music_cog'
SKY_MUSIC_WEBSITE_NAME = 'sky_music_website'
COMMAND_LINE_NAME = 'command_line'

MUSIC_COG_THEME = 'dark'
SKY_MUSIC_WEBSITE_THEME = 'light'
COMMAND_LINE_THEME = 'light'

DEFAULT_KEY = 'C'

DEFAULT_INSTRUMENT = 'harp'

MIDI_PITCHES = {'C': 60, 'C#': 61, 'Db': 61, 'D': 62, 'D#': 63, 'Eb': 63, 'E': 64, 'F': 65, 'F#': 66, 'Gb': 66, 'G': 67, 'G#': 68, 'Ab': 68, 'A': 69, 'A#': 70, 'Bb': 70, 'B': 71}
MIDI_SEMITONES = [0, 2, 4, 5, 7, 9, 11]  # May no longer be used when Western_scales is merged

