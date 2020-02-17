from communicator import Communicator
from parsers import SongParser


class MusicSheetMaker:

    def __init__(self):
        self.communicator = Communicator()
        self.parser = SongParser()
        self.song = None
