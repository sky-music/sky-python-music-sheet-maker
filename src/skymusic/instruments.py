import re
from skymusic import notes


class Skygrid():
    
    def __init__(self, shape=(3,5)):
        
        self.shape = shape #rows*columns, excluding negative coordinates, reserved for silences
        self.grid = {}
        self.frame_count = 0
        self.num_highlighted = None

    def get_row_count(self):
        return self.shape[0]

    def get_column_count(self):
        return self.shape[1]

    def get_shape(self):
        return self.shape

    def set_note(self, coord, frame=None, highlighted=True):
        
        frames = [frame] if frame is not None else range(0,max(1,self.get_frame_count()))
        for frame in frames: self.grid[coord] = {frame: highlighted}        

    def get_grid(self, frame=None):
        """
        Returns the dictionary for the instrument:
        where each key is the note position (tuple of row/index),
        the value is a dictionary with key=frame, value=True/False,
        where True/False means whether the note is played or not.
        The dictionarybis is sparse:
        - Inactive notes are not in the dictionary at all
        - Inactive frames are not in the keys of the value dict, so in principle {0:False} should not exist
        Full Example: {(0,0):{0:True}, (1,1):{0:True}}
        0 frame is the normal frame
        >1 frames are for notes of a triplet or quaver
        """
        if frame is None:
            return self.grid
        else:
            if frame < 0 or frame > self.get_frame_count()-1:
                return None
            else:
                #return {coord:frames for coord,frames in self.grid.items() if frame in list(filter(lambda k:frames[k] is True, frames))}
                return {coord:frames for coord,frames in self.grid.items() if frame in frames.keys()}

    def get_num_highlighted(self):
        '''Returns the number of highlighted notes, whatever the frame'''
        if self.num_highlighted is None:
            num = 0
            for coord in self.grid.keys():
                for frame in self.grid[coord].keys():
                    if self.grid[coord][frame]:
                        num += 1
            self.num_highlighted = num
        
        return self.num_highlighted

    def get_frame_count(self):
        '''Returns the number of frames'''
        if not self.frame_count:        
            frame_counts = [max(list(self.grid[coord].keys()))+1 for coord in self.grid.keys()]
            if frame_counts:
                self.frame_count = max(frame_counts)
            else:
                self.frame_count = 0
            
        return self.frame_count 
  
    def get_highlighted_frames(self, note_coord):
        '''Returns a list of frame numbers in which the note at coord is highlighted'''
        try:
            note_frames = self.grid[note_coord]  # Is note at 'position' highlighted or not
            highlighted_frames = [frame_index for frame_index in note_frames.keys()]
        except KeyError:  # Note is not in the grid dictionary: so it is not highlighted
            highlighted_frames = []
        return highlighted_frames


    def get_highlighted_coords(self, frame=None):
        '''Returns a list of coordinates of highlighted notes, only in the specified frame'''   
        #grid = instrument.get_grid(frame)
        highlighted_coords = []
        frames = [frame] if frame is not None else range(0,self.get_frame_count())
        #grid = self.get_grid(frame)
        if self.grid:
            for frame in frames:
                for coord in self.grid:  # Cycle over (row, col) positions in an icon
                    highlighted = self.grid[coord].get(frame,False)  # Button is highlighted
                    if highlighted: highlighted_coords += [coord]
        return highlighted_coords
        
        

TEXT = ['voice','lyric']
HARPS = ['harp','drum']

class Instrument():

    def __init__(self):
        self.type = 'undefined'
        self.repeat = 1
        self.index = 0
        self.is_silent = True
        self.is_broken = False

    def get_type(self):
        return self.type

    def set_repeat(self, repeat):
        self.repeat = repeat

    def get_repeat(self):
        '''Returns the number of times the instrument must be played'''
        return self.repeat

    def set_index(self, index):
        self.index = index

    def get_index(self):
        '''Instrument index in the song'''
        return self.index

    def get_is_silent(self):
        '''Returns whether the Harp is empty of notes (silent)'''
        return self.is_silent

    def get_is_broken(self):
        '''Returns whether the Harp is broken (notes were not recognized by the Parser)'''
        return self.is_broken
    
    def get_is_dead(self):
        '''Returns whether the instrument is broken (=its skygrid contains invalid notes)'''
        return self.get_is_broken()

    def set_is_broken(self, is_broken=True):
        '''Returns a boolean whether the harp could be translated'''
        self.is_broken = is_broken

    def set_is_silent(self, is_silent=True):
        '''Returns a boolean whether the harp is empty in this frame'''
        self.is_silent = is_silent


class Voice(Instrument):  # Lyrics or comments

    def __init__(self):
        super().__init__()
        self.type = 'voice'
        self.lyric = ''
        self.TAG_RE = re.compile(r'<[^>]+>')
        self.emphasis = None

    def get_lyric(self, strip_html=False):
        if strip_html:
            return self.TAG_RE.sub('', self.lyric)
        else:
            return self.lyric

    def set_lyric(self, lyric):
        
        lyric = lyric.strip()
        h_match = re.match(r'(?<!")(?P<emphasis>#*)(?P<lyric>.*)',lyric)
        h = len(h_match.group('emphasis'))
        if h>0:
            self.lyric = h_match.group('lyric')
            self.emphasis = f'h{h}'
        else:
            star_match = re.match(r'(?P<start>\**)(?P<lyric>[^\*]*)(?P<end>\**)',lyric)
            self.lyric = star_match.group('lyric')
            if len(star_match.group('start')) >= 2 and len(star_match.group('end')) >= 2:
                self.emphasis = 'b'
            elif (len(star_match.group('start')) == 1 and len(star_match.group('end')) == 1):
                self.emphasis = 'i'

    def __len__(self):
        return len(self.lyric)

    def __repr__(self):
        return f'<{self.type}-{self.index}, {len(self)} chars, repeat={self.repeat}>'
        
    def __str__(self):
        return str(self.get_lyric(strip_html=True))


class Harp(Instrument):
    '''Any harmonic instrument with a 3x5 grid'''
    def __init__(self):
        super().__init__()
        self.type = 'harp'
        self.shape = (3, 5)
        self.skygrid = Skygrid(shape=self.shape)
        
    def __getattr__(self, attr_name):
        return getattr(self.skygrid, attr_name)

    def get_is_dead(self):
        return self.get_is_broken() and self.get_num_highlighted() == 0

    def get_aspect_ratio(self):
        return self.shape[1]/self.shape[0]

    def __len__(self):
        return self.shape[1] * self.shape[0]

    def __str__(self):
        if self.get_is_dead():
            broken = 'dead'
        elif self.get_is_broken():
            broken = ' broken' 
        else:
            broken = ''
        silent = ' broken' if self.get_is_silent() else ''
        return f'<{self.type}-{self.index}, {self.get_row_count()}*{self.get_column_count()}, {self.get_num_highlighted()} ON, repeat={self.repeat}, {broken}{silent}>'       

    def get_note_from_position(self, pos):
        '''Returns the note type Root, Diamond, Circle from the position in Sky grid'''
        # Calculate the note's overall index in the harp (0 to 14)              
        
        return notes.Note(self, pos)

    def set_skygrid(self, skygrid):
        if self.shape != skygrid.shape:
            raise ValueError(f"Skygrid shape {skygrid.shape} is not equal to instrument shape {self.shape}")
        self.skygrid = skygrid        

class Drum(Harp):
    
    def __init__(self):
        super().__init__()
        self.type = 'drum'
        self.shape = (2,4)
        self.skygrid = Skygrid(shape=(self.row_count, self.column_count))
    
