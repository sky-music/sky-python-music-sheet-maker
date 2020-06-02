#import os
#import io
from src.skymusic import notes

class Instrument():

    def __init__(self):
        self.type = 'undefined'
        self.chord_skygrid = {}
        self.repeat = 1
        self.index = 0
        self.is_silent = True
        self.is_broken = False

    def set_chord_skygrid(self, chord_skygrid):
        self.chord_skygrid = chord_skygrid

    def get_chord_skygrid(self):
        """
        Returns the dictionary for the chord:
        where each key is the note position (tuple of row/index),
        the value is a dictionary with key=frame, value=True/False,
        where True/False means whether the note is played or not.
        Inactive notes are actually not in the dictionary at all.
        Example: {(0,0):{0:True}, (1,1):{0:True}}
        """
        return self.chord_skygrid

    def get_type(self):
        return self.type

    def set_repeat(self, repeat):
        self.repeat = repeat

    def get_repeat(self):
        """Returns the number of times the chord must be played"""
        return self.repeat

    def set_index(self, index):
        self.index = index

    def get_index(self):
        """Instrument index in the song"""
        return self.index

    def get_is_silent(self):
        """Returns whether the Harp is empty of notes (silent)"""
        return (len(self.chord_skygrid) == 0 or self.is_silent)

    def get_is_broken(self):
        """Returns whether the Harp is broken (notes were not recognized by the Parser)"""
        return self.is_broken

    def set_is_broken(self, is_broken=True):
        """Returns a boolean whether the harp could be translated"""
        self.is_broken = is_broken

    def set_is_silent(self, is_silent=True):
        """Returns a boolean whether the harp is empty in this frame"""
        self.is_silent = is_silent


class Voice(Instrument):  # Lyrics or comments

    def __init__(self):
        super().__init__()
        self.type = 'voice'
        self.lyric = ''

    def get_lyric(self):
        return self.lyric

    def set_lyric(self, lyric):
        self.lyric = lyric

    def __len__(self):
        return len(self.lyric)

    def __str__(self):
        return f'<{self.type}-{self.index}, {len(self)} chars, repeat={self.repeat}>'                


class Harp(Instrument):

    def __init__(self):
        super().__init__()
        self.type = 'harp'
        self.column_count = 5
        self.row_count = 3

    def get_row_count(self):
        return self.row_count

    def get_column_count(self):
        return self.column_count

    def get_num_highlighted(self):
        num = 0
        for k in self.chord_skygrid.keys():
            for kk in self.chord_skygrid[k].keys():
                if self.chord_skygrid[k][kk]:
                    num += 1
        return num

    def __len__(self):
        return self.column_count * self.row_count

    def __str__(self):
        return f'<{self.type}-{self.index}, {len(self)} notes, {self.get_num_highlighted()} highlighted, repeat={self.repeat}>'
        

    def get_note_from_position(self, pos):
        """Returns the note type Root, Diamond, Circle from the position in Sky grid"""
        # Calculate the note's overall index in the harp (0 to 14)              
        note_index = (pos[0] * self.get_column_count()) + pos[1]

        if note_index % 7 == 0:  # the 7 comes from the heptatonic scale of Sky's music (no semitones)
            # Note is a root note
            return notes.NoteRoot(self, pos)  # very important: the chord creating the note is passed as a parameter
        elif note_index % self.get_column_count() % 2 == 0:
            # Note is in an odd column, so it is a circle
            return notes.NoteCircle(self, pos)
        else:
            # Note is in an even column, so it is a diamond
            return notes.NoteDiamond(self, pos)
