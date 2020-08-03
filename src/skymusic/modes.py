from enum import Enum
import src.skymusic.parsers.noteparsers
import src.skymusic.instruments
from src.skymusic import Lang

class InputMode(Enum):
    SKYKEYBOARD = (False, "input_mode/skykeyboard/short_desc", "input_mode/skykeyboard/long_desc", src.skymusic.parsers.noteparsers.skykeyboard.SkyKeyboard)
    SKY = (False, "input_mode/sky/short_desc", "input_mode/sky/long_desc", src.skymusic.parsers.noteparsers.skyabc15.SkyABC15)
    SKYHTML = (False, "input_mode/skyhtml/short_desc", "input_mode/skyhtml/long_desc", src.skymusic.parsers.noteparsers.skyabc15.SkyABC15)
    SKYJSON = (False, "input_mode/skyjson/short_desc", "input_mode/skyjson/long_desc", src.skymusic.parsers.noteparsers.skyjson.SkyJson)
    ENGLISH = (True, "input_mode/english/short_desc", "input_mode/english/long_desc", src.skymusic.parsers.noteparsers.english.English)
    DOREMI = (True, "input_mode/doremi/short_desc", "input_mode/doremi/long_desc", src.skymusic.parsers.noteparsers.doremi.Doremi)
    JIANPU = (True, "input_mode/jianpu/short_desc", "input_mode/jianpu/long_desc", src.skymusic.parsers.noteparsers.jianpu.Jianpu)
    ENGLISHCHORDS = (True, "input_mode/englishchords/short_desc", "input_mode/englishchords/long_desc",
                     src.skymusic.parsers.noteparsers.englishchords.EnglishChords)
    DOREMIJP = (True, "input_mode/doremijp/short_desc", "input_mode/doremijp/long_desc", src.skymusic.parsers.noteparsers.doremi_jp.DoremiJP)

    def __init__(self, chromatic, short_desc, long_desc, note_parser_method):
        self.chromatic = chromatic
        self.short_desc_yaml = short_desc
        self.long_desc_yaml = long_desc
        self.note_parser_method = note_parser_method

    def __str__(self):
        return self.get_short_desc('en_US')

    def get_is_chromatic(self):
        return self.chromatic

    def get_short_desc(self, locale='en_US'):
        return Lang.get_string(self.short_desc_yaml, locale)

    def get_long_desc(self, locale='en_US'):
        return Lang.get_string(self.long_desc_yaml, locale)

    def get_note_parser(self, locale='en_US'):
        return self.note_parser_method(locale=locale)



class RenderMode(Enum):
    HTML = (False, False, False, "render_mode/html/short_desc", 'text/html', '.html', src.skymusic.parsers.noteparsers.skyabc15.SkyABC15)
    SVG = (True, False, False, "render_mode/svg/short_desc", 'image/svg+xml', '.svg', src.skymusic.parsers.noteparsers.skyabc15.SkyABC15)
    PNG = (True, False, False, "render_mode/png/short_desc", 'image/png', '.png', src.skymusic.parsers.noteparsers.skyabc15.SkyABC15)
    MIDI = (False, True, True, "render_mode/midi/short_desc", 'audio/midi', '.mid', src.skymusic.parsers.noteparsers.skyabc15.SkyABC15)
    SKYJSON = (False, True, False, "render_mode/skyjson/short_desc", 'application/json', '.json', src.skymusic.parsers.noteparsers.skyjson.SkyJson)
    SKYASCII = (False, False, False, "render_mode/skyascii/short_desc", 'text/plain', '_sky.txt', src.skymusic.parsers.noteparsers.skyabc15.SkyABC15)
    ENGLISHASCII = (False, False, True, "render_mode/englishascii/short_desc", 'text/plain', '_english.txt', src.skymusic.parsers.noteparsers.english.English)
    JIANPUASCII = (False, False, True, "render_mode/jianpuascii/short_desc", 'text/plain', '_jianpu.txt', src.skymusic.parsers.noteparsers.jianpu.Jianpu)
    DOREMIASCII = (False, False, True, "render_mode/doremiascii/short_desc", 'text/plain', '_doremi.txt', src.skymusic.parsers.noteparsers.doremi.Doremi)


    def __init__(self, image_mode, time_mode, chromatic, short_desc, mime_type, extension, note_parser_method):
        self.image_mode = image_mode
        self.time_mode = time_mode
        self.chromatic = chromatic
        self.short_desc_yaml = short_desc
        self.mime_type = mime_type
        self.extension = extension
        self.note_parser_method = note_parser_method

    def __str__(self):
        return self.get_short_desc('en_US')

    def get_is_image(self):
        return self.image_mode
        
    def get_is_time(self):
        return self.time_mode
        
    def get_is_chromatic(self):
        return self.chromatic
 
    def get_time_modes():
        
          return [mode for mode in RenderMode if RenderMode.get_is_time()]  
          
    def get_image_modes():
        
          return [mode for mode in RenderMode if RenderMode.get_is_image()]

    def get_chromatic_modes():
        
          return [mode for mode in RenderMode if RenderMode.get_is_chromatic()]            
                              
    def get_short_desc(self, locale='en_US'):
        return Lang.get_string(self.short_desc_yaml, locale)

    def get_note_parser(self, locale='en_US'):
        return self.note_parser_method(locale=locale)

    def get_mime_type(self):
        return self.mime_type

    def get_extension(self):
        return self.extension

class InstrumentType(Enum):
    NORMAL = ("instrument/normal/short_desc", "instrument/normal/long_desc", src.skymusic.instruments.Harp)
    DRUM = ("instrument/drum/short_desc", "instrument/drum/long_desc", src.skymusic.instruments.Drum)

    def __init__(self, short_desc_yaml, long_desc_yaml, instrument_class):
        self.short_desc_yaml = short_desc_yaml
        self.long_desc_yaml = long_desc_yaml
        self.instrument_class = instrument_class

    def __str__(self):
        return self.get_short_desc('en_US')

    def get_short_desc(self, locale='en_US'):
        return Lang.get_string(self.short_desc_yaml, locale)

    def get_long_desc(self, locale='en_US'):
        return Lang.get_string(self.long_desc_yaml, locale)
    
    def get_instrument(self):
        return self.instrument_class()


class AspectRatio(Enum):
    WIDESCREEN = ("aspect_ratio/widescreen/short_desc", 16/9.0)
    OLDTV = ("aspect_ratio/oldtv/short_desc", 4/3.0)
    SQUARE = ("aspect_ratio/square/short_desc", 1.0)
    A4 = ("aspect_ratio/A4/short_desc", 21/29.7)
    VERTPANEL = ("aspect_ratio/vertical_panel/short_desc", 1/2.0)

    def __init__(self, short_desc_yaml, ratio):
        self.short_desc_yaml = short_desc_yaml
        self.ratio = ratio

    def __str__(self):
        return self.get_short_desc('en_US')

    def get_short_desc(self, locale='en_US'):
        return Lang.get_string(self.short_desc_yaml, locale)

    def get_ratio(self):
        return self.ratio


class CSSMode(Enum):
    XML = 1
    HREF = XML
    LINK = XML
    IMPORT = 2
    EMBED = 3
    HARD = EMBED


class ReplyType(Enum):
    TEXT = (1, (str,))  # str
    NUMBER = (2, (int, float))  # int
    NOTE = (3, (str,))  # str, with possible additional checks
    INPUTMODE = (4, (InputMode,))  # modes.InputMode
    RENDERMODES = (5, (RenderMode,))
    ASPECTRATIO = (6, (AspectRatio,))
    INSTRUMENT = (7, (InstrumentType,))
    FILEPATH = (8, (str,))  # A file path
    OTHER = (9, None)
    
    def __init__(self, number, enum_classes):
        self.number = number
        self.enum_classes = enum_classes
        
    def get_classes(self):
        
        return self.enum_classes

    def get_defined_types():
        
        return [reply_type for reply_type in ReplyType if reply_type.get_classes()]
                        
    def get_string_types():
        
        string_types = [reply_type for reply_type in ReplyType.get_defined_types() if str in reply_type.get_classes()]
        
        return string_types
        
    def get_number_types():
        
        number_types = [reply_type for reply_type in ReplyType.get_defined_types() if (int in reply_type.get_classes() or float in reply_type.get_classes())]
        
        return number_types
        
    def get_object_types():
        
        number_types = ReplyType.get_number_types()
        string_types = ReplyType.get_string_types()
        return [reply_type for reply_type in ReplyType.get_defined_types() if reply_type not in (string_types+number_types)]
