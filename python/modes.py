from enum import Enum
import os
import noteparsers


class InputMode(Enum):
    if (os.getenv('LANG') == 'fr') or (os.getenv('LANG') == 'be'):
        SKYKEYBOARD = (1, 'Sky keyboard', 'Type on keyboard as you would in Sky:\n   AZERT\n   QSDFG\n   WXCVB', noteparsers.skykeyboard.SkyKeyboard)
    else:
        SKYKEYBOARD = (1, 'Sky keyboard', 'Type on keyboard as you would in Sky:\n   QWERT\n   ASDFG\n   ZXCVB', noteparsers.skykeyboard.SkyKeyboard)
    SKY = (2, 'Sky ABC1-5', 'Sky column/row notation:\n   A1 A2 A3 A4 A5\n   B1 B2 B3 B4 B5\n   C1 C2 C3 C4 C5', noteparsers.skyabc15.SkyABC15)
    ENGLISH = (3, 'English CDEFGAB',
               'English (note name in C D E F G A B + alteration b/# + octave number, e.g. Cb4 D#4 E5 ...)', noteparsers.english.English)
    DOREMI = (4, 'French doremi',
              'Doremi (note name in do re mi fa sol la si/ti + alteration b/# + octave number, e.g. dob4 re#4 mi5 ...)', noteparsers.doremi.Doremi)
    JIANPU = (5, 'Jianpu 1234567+-',
              'Jianpu (note name in 1 2 3 4 5 6 7, followed by alteration b/# and several + or - for octave shift)', noteparsers.jianpu.Jianpu)
    ENGLISHCHORDS = (6, 'Chords CDEFGABmaj',
                     'Abbreviated English chord name (e.g. C, F, Dm, Bdim, A+, Csus2, Dsus4, C6, Cmaj7, Dm11)', noteparsers.englishchords.EnglishChords)
    
    def __init__(self, number, short_desc, long_desc, note_parser_method):
        
        self.number = number
        self.short_desc = short_desc
        self.long_desc = long_desc
        self.note_parser_method = note_parser_method

    def __str__(self):
        return self.short_desc
    

class RenderMode(Enum):
    HTML = (1, 'HTML visual sheet', 'text/html', '.html', noteparsers.skyabc15.SkyABC15)
    SVG = (2, 'SVG visual sheet', 'image/svg+xml', '.svg', noteparsers.skyabc15.SkyABC15)
    PNG = (3, 'PNG visual sheet', 'image/png', '.png', noteparsers.skyabc15.SkyABC15)
    MIDI = (4, 'Midi song file', 'audio/midi', '.mid', noteparsers.skyabc15.SkyABC15)
    SKYASCII = (5, 'song in Sky notation', 'text/plain', '_sky.txt', noteparsers.skyabc15.SkyABC15)
    ENGLISHASCII = (6, 'song in English notation', 'text/plain', '_english.txt', noteparsers.english.English)
    JIANPUASCII = (7, 'song in Jianpu notation', 'text/plain', '_jianpu.txt', noteparsers.jianpu.Jianpu)
    DOREMIASCII = (8, 'song in do-re-mi notation', 'text/plain', '_doremi.txt', noteparsers.doremi.Doremi)

    def __init__(self, number, short_desc, mime_type, extension, note_parser_method):
        
        self.number = number
        self.short_desc = short_desc
        self.mime_type = mime_type
        self.extension = extension
        self.note_parser_method = note_parser_method

    def __str__(self):
        return self.short_desc


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
    TEXT = 1 #str
    INTEGER = 2 #int
    NOTE = 3 #str, with possible additional checks
    INPUTMODE = 4 #modes.InputMode
    RENDERMODES = 5
    FILEPATH = 6 #A file path
    BUFFERS = 7
    OTHER = 8
