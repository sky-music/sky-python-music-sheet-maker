from enum import Enum

class InputMode(Enum):
    KEYBOARD = 1
    SKY = 2
    WESTERN = 3
    JIANPU = 4
    SKYFILE = 5
    WESTERNFILE = 6
    JIANPUFILE = 7

class RenderMode(Enum): # Currently unused as of october 9th 2019
    VISUAL = 1
    ASCII = 2