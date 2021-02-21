
class Note:

    def __init__(self, instrument, pos=None):
        self.position = pos
        if pos is not None:
            self.index = (pos[0] * instrument.get_column_count()) + pos[1]
        else:
            self.index = None
        self.skygrid = instrument.get_skygrid()
        self.instrument_type = instrument.get_type()
        self.instrument_is_broken = instrument.get_is_broken()
        self.instrument_is_silent = instrument.get_is_silent()
        self.row_count = instrument.get_row_count()
        self.column_count = instrument.get_column_count()

    def get_position(self):
        """Return the note position as a tuple row/column"""
        return self.position

    def set_position(self, pos):
        """Sets the position tuple from row and column values"""
        self.position = pos
        self.index = (pos[0] * self.column_count) + pos[1]

    def get_column_count(self):
        return self.column_count 

    def get_index(self):
        """Returns the note index in Sky grid"""
        return self.index

    def get_middle_position(self):
        return (int(self.row_count/2), int(self.column_count/2))

    def get_middle_index(self):
        """Returns the index at the center of Sky grid"""
        return int(self.row_count * self.column_count / 2.0)

    def get_highlighted_frames(self):
        try:
            note_states = self.skygrid[self.get_position()]  # Is note at 'position' highlighted or not
            highlighted_frames = [frame_index for frame_index in note_states.keys()]
        except KeyError:  # Note is not in the skygrid dictionary: so it is not highlighted
            highlighted_frames = []
        return highlighted_frames

    def is_highlighted(self):
        highlighted_frames = self.get_highlighted_frames()
        if len(highlighted_frames) > 0:
            return True
        else:
            return False

    def __str__(self):
        return f"<{self.index}, pos={self.position}, highlighted frames={self.get_highlighted_frames()}>"

