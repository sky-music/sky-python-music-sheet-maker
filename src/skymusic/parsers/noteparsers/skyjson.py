import re

from . import noteparser

class SkyJson(noteparser.NoteParser):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        #The numbers should have 2 digits and not 1 to ease splitting of glued chords. The input notes with only 1 digit will be sanitized to have two
        self.position_map = {
            '.': (-1, -1),
            'Key00': (0, 0), 'Key01': (0, 1), 'Key02': (0, 2), 'Key03': (0, 3), 'Key04': (0, 4),
            'Key05': (1, 0), 'Key06': (1, 1), 'Key07': (1, 2), 'Key08': (1, 3), 'Key09': (1, 4),
            'Key10': (2, 0), 'Key11': (2, 1), 'Key12': (2, 2), 'Key13': (2, 3), 'Key14': (2, 4)
        } # Valid as long as no instrument is larger than this
        
        #Only one digit because it is the format chosen by Specy
        self.inverse_position_map = {
            (-1, -1): '.',
            (0, 0): 'Key0', (0, 1): 'Key1', (0, 2): 'Key2', (0, 3): 'Key3', (0, 4): 'Key4',
            (1, 0): 'Key5', (1, 1): 'Key6', (1, 2): 'Key7', (1, 3): 'Key8', (1, 4): 'Key9',
            (2, 0): 'Key10', (2, 1): 'Key11', (2, 2): 'Key12', (2, 3): 'Key13', (2, 4): 'Key14'
        }

        #Layer information is discarded
        self.note_name_with_layer_regex = re.compile(r'(\d{,2})(Key\d{2})', re.IGNORECASE)
        self.note_name_with_octave_regex = re.compile(r'\d{,2}(Key\d{2})', re.IGNORECASE)
        self.note_name_regex = self.note_name_with_octave_regex
        self.single_note_name_regex = re.compile(r'\b\d{,2}(Key\d{2}\b)', re.IGNORECASE)
        self.note_octave_regex = re.compile(r'\b\d\d')
        self.not_note_name_regex = re.compile(r'[^Key\d]+', re.IGNORECASE) #not accurate
        self.not_octave_regex = re.compile(r'[^\d]+') #not accurate

    def calculate_coordinate_for_note(self, note, song_key=None, note_shift=0, is_finding_key=False):
        """
        Returns a tuple containing the row index and the column index of the note's position.
        """
        note = self.sanitize_note_name(note)

        if note in self.position_map.keys():  # Note Shift (ie transposition in Sky)
            pos = self.position_map[note]  # tuple
            if (pos[0] < 0) and (pos[1] < 0):  # Special character
                return pos
            else:
                idx = pos[0] * self.columns + pos[1]
                idx = idx + note_shift
                pos = (int(idx / self.columns), idx - self.columns * int(idx / self.columns))
                if (0, 0) <= pos <= (2, 4):
                    return pos
                else:
                    raise KeyError('Note ' + str(note) + ' was not in range of the Sky keyboard.')
        else:
            raise KeyError('Note ' + str(note) + ' was not found in the position_map dictionary.')

    def get_note_from_coordinate(self, coord, layer=1):

        try:
            note = self.inverse_position_map[coord]
        except KeyError:
            note = 'X'
            
        if note != '.': note = '%02d' % layer

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
