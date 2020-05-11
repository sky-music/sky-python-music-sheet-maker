from enum import Enum
import noteparsers
import Lang


class InputMode(Enum):
    SKYKEYBOARD = (
    1, "input_mode/skykeyboard/short_desc", "input_mode/skykeyboard/long_desc", noteparsers.skykeyboard.SkyKeyboard)
    SKY = (2, "input_mode/sky/short_desc", "input_mode/sky/long_desc", noteparsers.skyabc15.SkyABC15)
    ENGLISH = (3, "input_mode/english/short_desc", "input_mode/english/long_desc", noteparsers.english.English)
    DOREMI = (4, "input_mode/doremi/short_desc", "input_mode/doremi/long_desc", noteparsers.doremi.Doremi)
    JIANPU = (5, "input_mode/jianpu/short_desc", "input_mode/jianpu/long_desc", noteparsers.jianpu.Jianpu)
    ENGLISHCHORDS = (6, "input_mode/englishchords/short_desc", "input_mode/englishchords/long_desc",
                     noteparsers.englishchords.EnglishChords)
    DOREMIJP = (7, "input_mode/doremijp/short_desc", "input_mode/doremijp/long_desc", noteparsers.doremi_jp.DoremiJP)

    def __init__(self, number, short_desc, long_desc, note_parser_method):
        self.number = number
        self.short_desc_yaml = short_desc
        self.long_desc_yaml = long_desc
        self.note_parser_method = note_parser_method

    def __str__(self):
        return self.get_short_desc('en_US')

    def get_short_desc(self, locale='en_US'):
        return Lang.get_string(self.short_desc_yaml, locale)

    def get_long_desc(self, locale='en_US'):
        return Lang.get_string(self.long_desc_yaml, locale)

    def get_note_parser(self):
        return self.note_parser_method()


class RenderMode(Enum):
    HTML = (1, "render_mode/html/short_desc", 'text/html', '.html', noteparsers.skyabc15.SkyABC15)
    SVG = (2, "render_mode/svg/short_desc", 'image/svg+xml', '.svg', noteparsers.skyabc15.SkyABC15)
    PNG = (3, "render_mode/png/short_desc", 'image/png', '.png', noteparsers.skyabc15.SkyABC15)
    MIDI = (4, "render_mode/midi/short_desc", 'audio/midi', '.mid', noteparsers.skyabc15.SkyABC15)
    SKYASCII = (5, "render_mode/skyascii/short_desc", 'text/plain', '_sky.txt', noteparsers.skyabc15.SkyABC15)
    ENGLISHASCII = (6, "render_mode/englishascii/short_desc", 'text/plain', '_english.txt', noteparsers.english.English)
    JIANPUASCII = (7, "render_mode/jianpuascii/short_desc", 'text/plain', '_jianpu.txt', noteparsers.jianpu.Jianpu)
    DOREMIASCII = (8, "render_mode/doremiascii/short_desc", 'text/plain', '_doremi.txt', noteparsers.doremi.Doremi)

    def __init__(self, number, short_desc, mime_type, extension, note_parser_method):
        self.number = number
        self.short_desc_yaml = short_desc
        self.mime_type = mime_type
        self.extension = extension
        self.note_parser_method = note_parser_method

    def __str__(self):
        return self.get_short_desc('en_US')

    def get_short_desc(self, locale='en_US'):
        return Lang.get_string(self.short_desc_yaml, locale)

    def get_note_parser(self):
        return self.note_parser_method()

    def get_mime_type(self):
        return self.mime_type

    def get_extension(self):
        return self.extension


class CSSMode(Enum):
    XML = 1
    HREF = XML
    LINK = XML
    IMPORT = 2
    EMBED = 3
    HARD = EMBED


class ResponseMode(Enum):
    COMMAND_LINE = 1
    BOT = 2


class ReplyType(Enum):
    TEXT = 1  # str
    INTEGER = 2  # int
    NOTE = 3  # str, with possible additional checks
    INPUTMODE = 4  # modes.InputMode
    RENDERMODES = 5
    FILEPATH = 6  # A file path
    BUFFERS = 7
    OTHER = 8
