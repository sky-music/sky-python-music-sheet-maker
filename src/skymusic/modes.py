from enum import Enum
import skymusic.parsers.noteparsers
import skymusic.instruments
from skymusic import Lang
"""
This file stores input/output modes as classes.
This is more secure than simply numbering them, or labeling them with a string.
ALL CLASSES LISTED IN ReplyType MUST CONTAIN the get_short_desc() and get_long_desc() methods
"""

class InputMode(Enum):
    '''A class of different input languages that can be parsed by the program'''
    SKYKEYBOARD = (False, "input_mode/skykeyboard/short_desc", "input_mode/skykeyboard/long_desc", skymusic.parsers.noteparsers.skykeyboard.SkyKeyboard)
    SKY = (False, "input_mode/sky/short_desc", "input_mode/sky/long_desc", skymusic.parsers.noteparsers.skyabc15.SkyABC15)
    SKYHTML = (False, "input_mode/skyhtml/short_desc", "input_mode/skyhtml/long_desc", skymusic.parsers.noteparsers.skyabc15.SkyABC15)
    SKYJSON = (False, "input_mode/skyjson/short_desc", "input_mode/skyjson/long_desc", skymusic.parsers.noteparsers.skyjson.SkyJson)
    ENGLISH = (True, "input_mode/english/short_desc", "input_mode/english/long_desc", skymusic.parsers.noteparsers.english.English)
    DOREMI = (True, "input_mode/doremi/short_desc", "input_mode/doremi/long_desc", skymusic.parsers.noteparsers.doremi.Doremi)
    JIANPU = (True, "input_mode/jianpu/short_desc", "input_mode/jianpu/long_desc", skymusic.parsers.noteparsers.jianpu.Jianpu)
    ENGLISHCHORDS = (True, "input_mode/englishchords/short_desc", "input_mode/englishchords/long_desc",
                     skymusic.parsers.noteparsers.englishchords.EnglishChords)
    DOREMIJP = (True, "input_mode/doremijp/short_desc", "input_mode/doremijp/long_desc", skymusic.parsers.noteparsers.doremi_jp.DoremiJP)
    MIDI = (True, "input_mode/midi/short_desc", "input_mode/midi/long_desc", skymusic.parsers.noteparsers.english.English)

    def __init__(self, chromatic, short_desc, long_desc, note_parser_method):
        self.chromatic = chromatic
        self.short_desc_yaml = short_desc
        self.long_desc_yaml = long_desc
        self.note_parser_method = note_parser_method

    def __str__(self, locale='en_US'):
        return self.get_short_desc(locale)

    def get_is_chromatic(self):
        return self.chromatic

    def get_short_desc(self, locale='en_US'):
        return Lang.get_string(self.short_desc_yaml, locale)

    def get_long_desc(self, locale='en_US'):
        return Lang.get_string(self.long_desc_yaml, locale)

    def get_note_parser(self, *args, **kwargs):
        return self.note_parser_method(*args, **kwargs)


class RenderMode(Enum):
    """
    A class of possible output file types that can be rendered by the program.
    Instruments with different grid sizes are handled via InstrumentType
    Gaming platforms requiring button names instead of icons are handled in GamePlatform
    """
    HTML = (True, False, False, False, "render_mode/html/short_desc", 'text/html', '.html', skymusic.parsers.noteparsers.skyabc15.SkyABC15)
    SVG = (True, True, False, False, "render_mode/svg/short_desc", 'image/svg+xml', '.svg', skymusic.parsers.noteparsers.skyabc15.SkyABC15)
    PNG = (True, True, False, False, "render_mode/png/short_desc", 'image/png', '.png', skymusic.parsers.noteparsers.skyabc15.SkyABC15)
    MIDI = (False, False, True, True, "render_mode/midi/short_desc", 'audio/midi', '.mid', skymusic.parsers.noteparsers.skyabc15.SkyABC15)
    SKYJSON = (False, False, True, False, "render_mode/skyjson/short_desc", 'application/json', '.json.txt', skymusic.parsers.noteparsers.skyjson.SkyJson)
    SKYASCII = (False, False, False, False, "render_mode/skyascii/short_desc", 'text/plain', '_skyABC15.txt', skymusic.parsers.noteparsers.skyabc15.SkyABC15)
    ENGLISHASCII = (False, False, False, True, "render_mode/englishascii/short_desc", 'text/plain', '_english.txt', skymusic.parsers.noteparsers.english.English)
    JIANPUASCII = (False, False, False, True, "render_mode/jianpuascii/short_desc", 'text/plain', '_jianpu.txt', skymusic.parsers.noteparsers.jianpu.Jianpu)
    DOREMIASCII = (False, False, False, True, "render_mode/doremiascii/short_desc", 'text/plain', '_doremi.txt', skymusic.parsers.noteparsers.doremi.Doremi)

    def __init__(self, visual, image_mode, time_mode, chromatic, short_desc, mime_type, extension, note_parser_method):
        self.visual = visual
        self.image_mode = image_mode
        self.time_mode = time_mode
        self.chromatic = chromatic
        self.short_desc_yaml = short_desc
        self.mime_type = mime_type
        self.extension = extension
        self.note_parser_method = note_parser_method

    def __str__(self, locale='en_US'):
        return self.get_short_desc(locale)

    def get_is_visual(self): return self.visual

    def get_is_image(self): return self.image_mode
        
    def get_is_time(self): return self.time_mode
        
    def get_is_chromatic(self): return self.chromatic
 
    def get_visual_modes():
        return [mode for mode in RenderMode if RenderMode.get_is_visual()]  

    def get_image_modes():
        return [mode for mode in RenderMode if RenderMode.get_is_image()] 
   
    def get_time_modes():
        return [mode for mode in RenderMode if RenderMode.get_is_time()]

    def get_chromatic_modes():
        return [mode for mode in RenderMode if RenderMode.get_is_chromatic()]            
                              
    def get_short_desc(self, locale='en_US'):
        return Lang.get_string(self.short_desc_yaml, locale)

    def get_note_parser(self, *args, **kwargs):
        return self.note_parser_method(*args, **kwargs)

    def get_mime_type(self): return self.mime_type

    def get_extension(self): return self.extension


class InstrumentType(Enum):
    '''A class of possible instrument types, typically having different grid sizes'''
    HARP = ("instrument_type/normal/short_desc", "instrument_type/normal/long_desc", skymusic.instruments.Harp)
    DRUM = ("instrument_type/drum/short_desc", "instrument_type/drum/long_desc", skymusic.instruments.Drum)

    @classmethod
    def get_default(cls): return cls.HARP    

    def __init__(self, short_desc_yaml, long_desc_yaml, instrument_class):
        self.short_desc_yaml = short_desc_yaml
        self.long_desc_yaml = long_desc_yaml
        self.instrument_class = instrument_class
        try:
            self.shape = self.instrument_class.shape
        except AttributeError:
            self.shape = None

    def __str__(self, locale='en_US'):
        return self.get_short_desc(locale)

    def get_short_desc(self, locale='en_US'):
        return Lang.get_string(self.short_desc_yaml, locale)

    def get_long_desc(self, locale='en_US'):
        return Lang.get_string(self.long_desc_yaml, locale)
    
    def get_instrument(self):
        return self.instrument_class() #Returns object and not class

    def get_shape(self): return self.shape
    
    def get_type(self): return self.instrument_class.type
        

class AspectRatio(Enum):
    '''A class storing possible formats for PNG sheets'''
    WIDESCREEN = ("aspect_ratio/widescreen/short_desc", 16/9.0)
    OLDTV = ("aspect_ratio/oldtv/short_desc", 4/3.0)
    SQUARE = ("aspect_ratio/square/short_desc", 1.0)
    A4 = ("aspect_ratio/A4/short_desc", 21/29.7)
    VERTPANEL = ("aspect_ratio/vertical_panel/short_desc", 1/2.0)

    def __init__(self, short_desc_yaml, ratio):
        self.short_desc_yaml = short_desc_yaml
        self.ratio = ratio

    def __str__(self, locale='en_US'):
        return self.get_short_desc(locale)

    def get_short_desc(self, locale='en_US'):
        return Lang.get_string(self.short_desc_yaml, locale)

    def get_ratio(self): return self.ratio


class GamePlatform(Enum):
    """
    A class of possible gaming platforms.
    The enum names must NOT be changed as they correspond to directory names
    """
    MOBILE = ('', False, "game_platform/mobile/short_desc", "game_platform/mobile/long_desc")
    PLAYSTATION = ('ps', True, "game_platform/playstation/short_desc", "game_platform/playstation/long_desc")
    SWITCH = ('sw', True, "game_platform/switch/short_desc", "game_platform/switch/long_desc")

    @classmethod
    def get_default(cls): return cls.MOBILE

    def __init__(self, nickname, has_gamepad, short_desc_yaml, long_desc_yaml):
        self.nickname = nickname
        self.short_desc_yaml = short_desc_yaml
        self.long_desc_yaml = long_desc_yaml
        self.has_gamepad = has_gamepad

    def __str__(self, locale='en_US'):
        return self.get_short_desc(locale)

    def get_short_desc(self, locale='en_US'):
        return Lang.get_string(self.short_desc_yaml, locale)

    def get_long_desc(self, locale='en_US'):
        return Lang.get_string(self.long_desc_yaml, locale)
    
    def get_nickname(self):
        '''Used for SVG tag names'''
        return self.nickname
        
    def get_name(self):
        '''Used for directories'''
        return self.name.lower()
 

class GamepadLayout(Enum):
    '''A class of possible gamepad buttons layout, for different gaming platforms'''
    PS1 = ('PS1',GamePlatform.PLAYSTATION, InstrumentType.HARP, "gamepad_layout/playstation/normal/ps1", skymusic.parsers.noteparsers.gamepad.Playstation)
    PS2 = ('PS2', GamePlatform.PLAYSTATION, InstrumentType.HARP, "gamepad_layout/playstation/normal/ps2", skymusic.parsers.noteparsers.gamepad.Playstation)
    PS3 = ('PS3',GamePlatform.PLAYSTATION, InstrumentType.HARP, "gamepad_layout/playstation/normal/ps3", skymusic.parsers.noteparsers.gamepad.Playstation)
    PS4 = ('PS4',GamePlatform.PLAYSTATION, InstrumentType.HARP, "gamepad_layout/playstation/normal/ps4", skymusic.parsers.noteparsers.gamepad.Playstation)
    SW1 = ('SW1',GamePlatform.SWITCH, InstrumentType.HARP, "gamepad_layout/switch/normal/sw1", skymusic.parsers.noteparsers.gamepad.Switch)
    SW2 = ('SW2',GamePlatform.SWITCH, InstrumentType.HARP, "gamepad_layout/switch/normal/sw2", skymusic.parsers.noteparsers.gamepad.Switch)
    SW3 = ('SW3',GamePlatform.SWITCH, InstrumentType.HARP, "gamepad_layout/switch/normal/sw3", skymusic.parsers.noteparsers.gamepad.Switch)

    PS1_DRUM = ('PS1',GamePlatform.PLAYSTATION, InstrumentType.DRUM, "gamepad_layout/playstation/drum/ps1", skymusic.parsers.noteparsers.gamepad.Playstation)
    
    SW1_DRUM = ('SW1',GamePlatform.SWITCH, InstrumentType.DRUM, "gamepad_layout/playstation/drum/ps1", skymusic.parsers.noteparsers.gamepad.Switch)

    @classmethod
    def get_layouts(cls,platform=GamePlatform.PLAYSTATION, instrument=InstrumentType.HARP):
        return list(filter(lambda lay: (lay.platform==platform) and (lay.instrument==instrument), list(cls)))
    
    @classmethod
    def get_default(cls, platform=GamePlatform.PLAYSTATION):
        possible_gamepads = cls.get_layouts(platform)
        try:
            return possible_gamepads[0]
        except (TypeError, IndexError):
            return None
    
    def __init__(self, nickname, platform, instrument, short_desc_yaml, note_parser_method):
        self.nickname = nickname
        self.platform = platform
        self.instrument = instrument
        self.short_desc_yaml = short_desc_yaml
        self.note_parser_method = note_parser_method

    def __str__(self, locale='en_US'):
        return self.get_short_desc(locale)

    def get_short_desc(self, locale='en_US'):
        return Lang.get_string(self.short_desc_yaml, locale)

    def get_long_desc(self, locale='en_US'):
        return Lang.get_string(self.short_desc_yaml, locale)

    def get_note_parser(self, *args, **kwargs):
        if 'layout' not in kwargs: kwargs.update({'layout': self.nickname})
        return self.note_parser_method(*args, **kwargs)
    
    def get_nickname(self):
        return self.nickname
    

class CSSMode(Enum):
    ''' A class to store possible CSS embedding options in HTML and SVG files'''
    XML = 1
    HREF = XML
    LINK = XML
    IMPORT = 2
    EMBED = 3
    HARD = EMBED


class ReplyType(Enum):
    '''A Class of possible replies from the user'''
    TEXT = (1, (str,))  # str
    NUMBER = (2, (int, float))  # int
    NOTE = (3, (str,))  # str, with possible additional checks
    INPUTMODE = (4, (InputMode,))  # modes.InputMode
    RENDERMODES = (5, (RenderMode,)) # Rendering mode
    ASPECTRATIO = (6, (AspectRatio,)) # PNG sheet aspect ratio
    INSTRUMENT = (7, (InstrumentType,)) # Instrument type among normal, drum
    GAMEPLATFORM = (8, (GamePlatform,)) # Gaming platform (eg Playstation which uses button names)
    GAMEPADLAYOUT = (9, (GamepadLayout,)) # Gaming platform (eg Playstation which uses button names)
    FILEPATH = (10, (str,))  # A file path
    OTHER = (11, None) # Something else!
    
    def __init__(self, number, enum_classes):
        self.number = number
        self.enum_classes = enum_classes
        
    def get_classes(self):
        return self.enum_classes

    def get_defined_types():
        return [reply_type for reply_type in ReplyType if reply_type.get_classes()]
                        
    def get_string_types():
        return [reply_type for reply_type in ReplyType.get_defined_types() if str in reply_type.get_classes()]
        
    def get_number_types():       
        return [reply_type for reply_type in ReplyType.get_defined_types() if (int in reply_type.get_classes() or float in reply_type.get_classes())]
 
    def get_object_types():
        
        number_types = ReplyType.get_number_types()
        string_types = ReplyType.get_string_types()
        return [reply_type for reply_type in ReplyType.get_defined_types() if reply_type not in (string_types+number_types)]
