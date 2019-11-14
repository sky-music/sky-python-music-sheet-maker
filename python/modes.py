from enum import Enum

class InputModes(Enum):
    SKYKEYBOARD = [1, 'Sky keyboard']
    SKY = [2, 'Sky ABC1-5']
    WESTERN = [3, 'Western CDEFGAB2-7']
    JIANPU = [4, 'Jianpu 1234567+-']
    WESTERNCHORDS = [5, 'Chords CDEFGAB']

class RenderModes(Enum):
    VISUAL = 1
    SKYASCII = 2
    WESTERNASCII = 3
    JIANPUASCII = 4
    
class CSSModes(Enum):
    XML = 1
    HREF = XML
    LINK = XML
    IMPORT = 2
    EMBED = 3
    HARD = EMBED