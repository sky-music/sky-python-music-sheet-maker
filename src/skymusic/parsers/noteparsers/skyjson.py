import re

from . import noteparser

class SkyJson(noteparser.NoteParser):
    """
    harp_coord_map = {
        '.': (-1, -1),
        'Key00': (0, 0), 'Key01': (0, 1), 'Key02': (0, 2), 'Key03': (0, 3), 'Key04': (0, 4),
        'Key05': (1, 0), 'Key06': (1, 1), 'Key07': (1, 2), 'Key08': (1, 3), 'Key09': (1, 4),
        'Key10': (2, 0), 'Key11': (2, 1), 'Key12': (2, 2), 'Key13': (2, 3), 'Key14': (2, 4)
    } # Valid as long as no instrument is larger than this
    
    #Only one digit because it is the format chosen by Specy
    harp_inv_coord_map = {
        (-1, -1): '.',
        (0, 0): 'Key0', (0, 1): 'Key1', (0, 2): 'Key2', (0, 3): 'Key3', (0, 4): 'Key4',
        (1, 0): 'Key5', (1, 1): 'Key6', (1, 2): 'Key7', (1, 3): 'Key8', (1, 4): 'Key9',
        (2, 0): 'Key10', (2, 1): 'Key11', (2, 2): 'Key12', (2, 3): 'Key13', (2, 4): 'Key14'
    }
    """
    coord_map = {'.': (-1, -1)}
    inv_coord_map = {(-1, -1): '.'}
    note_prefix = 'Key'
    map_zeros = 1 #Preprend 0 for 0-9
    inv_map_zeros = 0

    #Layer information is discarded
    note_name_with_layer_regex = re.compile(r'(\d{,2})(Key\d{2})', re.IGNORECASE)
    note_name_with_octave_regex = re.compile(r'\d{,2}(Key\d{2})', re.IGNORECASE)
    note_name_regex = note_name_with_octave_regex
    single_note_name_regex = re.compile(r'\b\d{,2}(Key\d{2}\b)', re.IGNORECASE)
    note_octave_regex = re.compile(r'\b\d\d')
    not_note_name_regex = re.compile(r'[^Key\d]+', re.IGNORECASE) #not accurate
    not_octave_regex = re.compile(r'[^\d]+') #not accurate

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        #The numbers should have 2 digits and not 1 to ease splitting of glued chords. The input notes with only 1 digit will be sanitized to have two
        self.__set_coord_maps__(self.shape)
        
    def __set_coord_maps__(self, shape=None):
        '''Creates the correspondance dict between the (row,col) coordinates and the JSON Key string'''
        if shape is None: shape=self.shape
        
        self.coord_map = self.__class__.coord_map.copy()
        self.inv_coord_map = self.__class__.inv_coord_map.copy()
        fmt = '{:0%dd}' % (self.map_zeros+1)
        inv_fmt = '{:0%dd}' % (self.inv_map_zeros+1)
        for row in range(0,shape[0]):
            for col in range(0,shape[1]):
                index = row*shape[1] + col
                self.inv_coord_map[(row,col)] = self.note_prefix + str.format(inv_fmt,index)
                self.coord_map[self.note_prefix + str.format(fmt,index)] =  (row, col)
 
    def get_coord_map(self, inverse=False):
        return self.inv_coord_map if inverse else self.coord_map                               

    def set_shape(self, shape):
        self.shape = shape
        self.__set_coord_maps__(shape)

    def calculate_coordinate_for_note(self, note, song_key=None, note_shift=0, is_finding_key=False):
        """
        Returns a tuple containing the row index and the column index of the note's coord.
        """
        note = self.sanitize_note_name(note)

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

    def get_note_from_coord(self, coord, layer_index=0, version='old'):
        '''string representation of note, using unpadded layer numbers, or list'''
        note = self.inv_coord_map.get(coord, 'X')
        
        if version == 'old':
            if note == '.':
                note = ''
            else:
                note = '%d' % layer_index + note #no zero padding in rendering
        elif version == 'new':
            if note == '.':
                note = []
            elif note == 'X':
                note = [0, '0']
            else:
                note = [int(note.replace('Key','')), hex(layer_index).replace('0x','')]
        else:
            raise KeyError(version)

        return note

    def sanitize_note_name(self, note_name):

        note_name = note_name.lower().capitalize()
        
        return note_name

    def sanitize_digits(self, note):
        '''
        Reformats notes from 0Key2 to 01Key02
        to avoid confusion between 1 and 10 when splitting chords with glued notes, e.g. 01Key0101Key02
        '''
        sanitized_note = re.sub(r'\b(\d)([^\d])', r'0\g<1>\g<2>', note)

        sanitized_note = re.sub(r'([^\d])(\d)\b', r'\g<1>0\g<2>', sanitized_note)
        
        return sanitized_note
        
    def get_layer(self,note,default=''):
        
        g = self.note_name_with_layer_regex.match(note)
        if g:
            return g.group(1)
        else:
            return default


