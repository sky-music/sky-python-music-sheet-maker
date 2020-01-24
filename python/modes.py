from enum import Enum


class InputModes(Enum):
    SKYKEYBOARD = [1, 'Sky keyboard', 'Type on keyboard as you would in Sky']
    SKY = [2, 'Sky ABC1-5', 'Sky column/row notation:\n   A1 A2 A3 A4 A5\n   B1 B2 B3 B4 B5\n   C1 C2 C3 C4 C5']
    ENGLISH = [3, 'English CDEFGAB',
               'English (note name in C D E F G A B + alteration b/# + octave number, e.g. Cb4 D#4 E5 ...)']
    DOREMI = [4, 'French doremi',
              'Doremi (note name in do re mi fa sol la si/ti + alteration b/# + octave number, e.g. dob4 re#4 mi5 ...)']
    JIANPU = [5, 'Jianpu 1234567+-',
              'Jianpu (note name in 1 2 3 4 5 6 7, followed by alteration b/# and several + or - for octave shift)']
    ENGLISHCHORDS = [6, 'Chords CDEFGABmaj',
                     'Abbreviated English chord name (e.g. C, F, Dm, Bdim, A+, Csus2, Dsus4, C6, Cmaj7, Dm11)']


class RenderModes(Enum):
    HTML = 1
    SVG = 2
    PNG = 3
    SKYASCII = 4
    ENGLISHASCII = 5
    JIANPUASCII = 6
    DOREMIASCII = 7
    MIDI = 8


class CSSModes(Enum):
    XML = 1
    HREF = XML
    LINK = XML
    IMPORT = 2
    EMBED = 3
    HARD = EMBED
