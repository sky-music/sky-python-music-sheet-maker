import re

from . import noteparser

class SkyABC15(noteparser.NoteParser):

    """
        harp_coord_map = {
            '.': (-1, -1),
            'A1': (0, 0), 'A2': (0, 1), 'A3': (0, 2), 'A4': (0, 3), 'A5': (0, 4),
            'B1': (1, 0), 'B2': (1, 1), 'B3': (1, 2), 'B4': (1, 3), 'B5': (1, 4),
            'C1': (2, 0), 'C2': (2, 1), 'C3': (2, 2), 'C4': (2, 3), 'C5': (2, 4)
        } # Valid as long as no instrument is larger than this

        harp_inv_coord_map = {
            (-1, -1): '.',
            (0, 0): 'A1', (0, 1): 'A2', (0, 2): 'A3', (0, 3): 'A4', (0, 4): 'A5',
            (1, 0): 'B1', (1, 1): 'B2', (1, 2): 'B3', (1, 3): 'B4', (1, 4): 'B5',
            (2, 0): 'C1', (2, 1): 'C2', (2, 2): 'C3', (2, 3): 'C4', (2, 4): 'C5'
        } # Valid as long as no instrument is larger than this
        """

    note_name_with_octave_regex = re.compile(r'([ABCabc][1-5])')
    note_name_regex = note_name_with_octave_regex
    single_note_name_regex = re.compile(r'(\b[ABCabc][1-5]\b)')
    not_note_name_regex = re.compile(r'[^ABCabc]+')
    not_octave_regex = re.compile(r'[^123]+')

    coord_map = {'.': (-1, -1)}
    inv_coord_map = {(-1, -1): '.'}

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.__set_coord_maps__(self.shape)
        
    def __set_coord_maps__(self, shape=None):
        '''Creates the correspondance dict between the (row,col) coordinates and the ABC1-5 Sky notation'''
        if shape is None: shape=self.shape
        
        self.coord_map = self.__class__.coord_map.copy()
        self.inv_coord_map = self.__class__.inv_coord_map.copy()
        i0 = ord('A')
        for row in range(0,shape[0]):
            for col in range(0, shape[1]):
                self.coord_map[chr(i0+row)+str(col+1)] = (row, col)
                self.inv_coord_map[(row,col)] = chr(i0+row)+str(col+1)

    def get_coord_map(self, inverse=False):
        return self.inv_coord_map if inverse else self.coord_map                               

    def set_shape(self, shape):
        self.shape = shape
        self.__set_coord_maps__(shape)                

    def calculate_coordinate_for_note(self, note, song_key=None, note_shift=0, is_finding_key=False):
        """
        Returns a tuple containing the row index and the column index of the note's position.
        """
        note = note.upper()

        if note in self.coord_map.keys():  # Note Shift (ie transposition in Sky)
            pos = self.coord_map[note]  # tuple
            if (pos[0] < 0) and (pos[1] < 0):  # Special character
                return pos
            else:
                columns = self.get_num_columns()
                idx = pos[0] * columns + pos[1]
                idx = idx + note_shift
                pos = (int(idx / columns), idx - columns * int(idx / columns))
                if (0, 0) <= pos <= (2, 4):
                    return pos
                else:
                    raise KeyError('Note ' + str(note) + ' was not in range of the Sky keyboard.')
        else:
            raise KeyError('Note ' + str(note) + ' was not found in the coord_map dictionary.')

    def get_note_from_coord(self, coord):

        return self.inv_coord_map.get(coord,'X')
        

    def sanitize_note_name(self, note_name):

        # make sure the first letter of the note is uppercase, for sky note's dictionary keys
        note_name = note_name.capitalize()
        return note_name


