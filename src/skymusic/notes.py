
class Note:

    def __init__(self, instrument, coord=None):
        self.coord = coord
        self.instrument = instrument #Instrument object owing the note
        if coord is not None:
            self.index = (coord[0] * instrument.get_num_columns()) + coord[1]
        else:
            self.index = None

    def get_coord(self):
        '''Return the note coord as a tuple row/column'''
        return self.coord

    def set_coord(self, coord):
        '''Sets the coord tuple from row and column values'''
        self.coord = coord
        self.index = (coord[0] * self.instrument.get_num_columns()) + coord[1]

    def get_index(self):
        '''Returns the note index in Sky grid'''
        return self.index

    def get_highlighted_frames(self):
        return self.instrument.get_highlighted_frames(self.get_coord())

    def is_highlighted(self):
        highlighted_frames = self.get_highlighted_frames()
        if len(highlighted_frames) > 0:
            return True
        else:
            return False

    def __str__(self):
        return f"<{self.index}, coord={self.coord}, highlighted frames={self.get_highlighted_frames()}>"

