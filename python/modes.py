from enum import Enum

class InputMode(Enum):
    SKYKEYBOARD = 1
    SKY = 2
    WESTERN = 3
    JIANPU = 4
    SKYFILE = 5
    WESTERNFILE = 6
    JIANPUFILE = 7
    WESTERNCHORDS = 8
    WESTERNCHORDSFILE = 9

class RenderMode(Enum):
    VISUAL = 1
    SKYASCII = 2
    WESTERNASCII = 3
    JIANPUASCII = 4