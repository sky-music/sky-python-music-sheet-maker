from enum import Enum
import os


class InputMode(Enum):
    if (os.getenv('LANG') == 'fr') or (os.getenv('LANG') == 'be'):
        SKYKEYBOARD = [1, 'Sky keyboard', 'Type on keyboard as you would in Sky:\n   AZERT\n   QSDFG\n   WXCVB']
    else:
        SKYKEYBOARD = [1, 'Sky keyboard', 'Type on keyboard as you would in Sky:\n   QWERT\n   ASDFG\n   ZXCVB']
    SKY = [2, 'Sky ABC1-5', 'Sky column/row notation:\n   A1 A2 A3 A4 A5\n   B1 B2 B3 B4 B5\n   C1 C2 C3 C4 C5']
    ENGLISH = [3, 'English CDEFGAB',
               'English (note name in C D E F G A B + alteration b/# + octave number, e.g. Cb4 D#4 E5 ...)']
    DOREMI = [4, 'French doremi',
              'Doremi (note name in do re mi fa sol la si/ti + alteration b/# + octave number, e.g. dob4 re#4 mi5 ...)']
    JIANPU = [5, 'Jianpu 1234567+-',
              'Jianpu (note name in 1 2 3 4 5 6 7, followed by alteration b/# and several + or - for octave shift)']
    ENGLISHCHORDS = [6, 'Chords CDEFGABmaj',
                     'Abbreviated English chord name (e.g. C, F, Dm, Bdim, A+, Csus2, Dsus4, C6, Cmaj7, Dm11)']


class RenderMode(Enum):
    HTML = [1, 'HTML', '.html']
    SVG = [2, 'SVG', '.svg']
    PNG = [3, 'PNG', '.png']
    MIDI = [4, 'MIDI', '.mid']
    SKYASCII = [5, 'Sky ASCII', '_sky.txt']
    ENGLISHASCII = [6, 'English ASCII', '_english.txt']
    JIANPUASCII = [7, 'Jianpu ASCII', '_jianpu.txt']
    DOREMIASCII = [8, 'Doremi ASCII', '_doremi.txt']


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
