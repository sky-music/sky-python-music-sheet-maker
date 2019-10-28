from enum import Enum

class InputMode(Enum):
    SKYKEYBOARD = 1
    SKY = 2
    WESTERN = 3
    JIANPU = 4
    SKYFILE = 5
    WESTERNFILE = 6
    JIANPUFILE = 7

class RenderMode(Enum):
    VISUALHTML = 1
    VISUALIMG = 2
    SKYASCII = 3
    WESTERNASCII = 4
    JIANPUASCII = 5