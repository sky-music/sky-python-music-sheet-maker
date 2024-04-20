import re
from skymusic import notes


class Skygrid():
    
    def __init__(self, shape=(3,5)):
        
        self.shape = shape #rows*columns, excluding negative coordinates, reserved for silences
        self.grid = {}
        self.inverse_grid = {} #Only highlighted notes
        #self._num_frames = 0
        self._num_by_frame = {}

    def get_num_rows(self): return self.shape[0]

    def get_num_columns(self): return self.shape[1]

    def get_shape(self): return self.shape

    def set_note(self, coord, frame=None, highlighted=True):
        
        frames = [frame] if frame is not None else range(0,max(1,self.get_num_frames()))
        for frame in frames: self.grid[coord] = {frame: highlighted}
        # Reset counters
        self._num_by_frame = {}
        #self._num_frames = 0
        self.inverse_grid = {}


    def get_grid(self, frame=None):
        """
        Returns the dictionary for the instrument:
        where each key is the note coord (tuple of row/index),
        each value is a dictionary {frame: state} where state=True/False,
        meaning whether the note is played or not.
        The dictionary is sparse:
        - Inactive notes are not in the dictionary at all
        - Inactive frames are not in the keys of the value dict, so in principle {0:False} should not exist
        Full Example: {(0,0):{0:True}, (1,1):{0:True, 1:True}}
        0 frame is the normal frame
        >1 frames are for notes of a triplet or quaver
        """
        if frame is None:
            return self.grid
        else:
            if frame < 0 or frame > self.get_num_frames()-1:
                return None
            else:
                #return {coord:frames for coord,frames in self.grid.items() if frame in list(filter(lambda k:frames[k] is True, frames))}
                return {coord:frames for coord,frames in self.grid.items() if frame in frames.keys()}


    def get_inverse_grid(self):
        '''Builds the inverse dictionary, keeping None notes'''
        if not self.inverse_grid:
            inverse_grid = {}
            for coord in self.grid:
                for f in self.grid[coord]:
                    if self.grid[coord][f]: inverse_grid[f] = inverse_grid.get(f,[]) + [coord]
            self.inverse_grid = inverse_grid 
        return self.inverse_grid


    def get_highlighted_frames(self, note_coord=None):
        '''Returns a list of frame numbers in which the note at coord is highlighted'''
        if note_coord is None: # Try all coords
            #note_coords = self.grid.keys()
            return sorted(self.get_inverse_grid().keys())
        else: # Test for specified note only
            note_frames = self.grid.get(note_coord, {})
            highlighted_frames = sorted([f for f in note_frames.keys() if note_frames[f] is True])

    
        return sorted(list(set(highlighted_frames)))


    def get_highlighted_coords(self, frame=None):
        '''Returns a list of coordinates of highlighted notes, only in the specified frame, removing invalid notes'''
        
        inverse_grid = self.get_inverse_grid()
        frames = [frame] if frame is not None else range(0,self.get_num_frames())
        highlighted_coords = []
        for frame in frames:
            highlighted_coords += list(filter(None,inverse_grid[frame]))
        #grid = instrument.get_grid(frame)
        #highlighted_coords = []
        #frames = [frame] if frame is not None else range(0,self.get_num_frames())
        #grid = self.get_grid(frame)
        #if self.grid:
            #for frame in frames:
                #for coord in self.grid:  # Cycle over (row, col) coords in an icon
                    #highlighted = self.grid[coord].get(frame,False)  # Button is highlighted
                    #if highlighted: highlighted_coords += [coord]
        
        return sorted(highlighted_coords)


    def get_num_frames(self):
        '''Returns the number of highlighted frames'''
        #if not self._num_frames:
            
        return len(self.get_inverse_grid())    
            #num_frames = [max(list(self.grid[coord].keys()))+1 for coord in self.grid.keys()]
            
            #if num_frames:
                #self._num_frames = max(num_frames)
            #else:
                #self._num_frames = 0
            
        #return self._num_frames 

    def get_num_highlighted(self, frame=None):
        '''Returns the number of highlighted notes, in specified frame or all frames'''
        if not self._num_by_frame: self.get_num_by_frame()
        return self._num_by_frame.get(frame, None) if frame is not None else sum(self._num_by_frame.values())


    def get_num_by_frame(self):
        '''number of highlighted notes in a frame'''
        if not self._num_by_frame: 
            #num_highlighted = {f:0 for f in range(0,self.get_num_frames())}
            #for coord in self.grid:
                #for f in self.grid[coord]:
                    #if self.grid[coord][f]: num_highlighted[f] += 1
            inverse_grid = self.get_inverse_grid()
            self._num_by_frame = {f: len(inverse_grid[f]) for f in inverse_grid}
        return self._num_by_frame


    def get_max_num_by_frame(self):
        num_by_frame = self.get_num_by_frame()
        if num_by_frame:
            return max(num_by_frame.values())
        else:
            return 0
                 

class Instrument():

    type = 'GenericInstrument'
    def __init__(self):
        self.repeat = 1
        self.index = 0
        self.is_silent = True
        self.is_broken = False

    @property
    def is_tonal(self): return self.get_is_tonal()
    
    @property
    def is_textual(self): return self.get_is_textual()    

    def get_type(self):
        return self.type

    def get_is_tonal(self):
        return hasattr(self, 'skygrid')
        
    def get_is_textual(self):
        #Another definition could be envsioned, but currently .lyric is too specific to be relied on
        return hasattr(self, 'lyric')

    def get_is_decorative(self):
        return False

    def set_repeat(self, repeat): self.repeat = repeat

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
    type = 'voice'
    TAG_RE = re.compile(r'<[^>]+>')
    def __init__(self):
        super().__init__()
        self.lyric = ''
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

    def get_text(self, *args, **kwargs): return self.get_lyric(*args, **kwargs)
    
    def set_text(self, *args, **kwargs): return self.set_lyric(*args, **kwargs)    

    def __len__(self):
        return len(self.lyric)

    def __repr__(self):
        return f'<{self.type}-{self.index}, {len(self)} chars, repeat={self.repeat}>'
        
    def __str__(self):
        return str(self.get_lyric(strip_html=True))


class Harp(Instrument):
    '''Any harmonic instrument with a 3x5 grid'''
    type = 'harp'
    shape = (3, 5)
    def __init__(self):
        super().__init__()
        self.skygrid = Skygrid(shape=self.shape) #do not change name as it is used by get_is_tonal() and get_is_textual()
        
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
        return f'<{self.type}-{self.index}, {self.get_num_rows()}*{self.get_num_columns()}, {self.get_num_highlighted()} ON, repeat={self.repeat}, {broken}{silent}>'       

    def get_middle_coord(self):
        return (int(self.get_num_rows()/2.0), int(self.get_num_columns()/2.0))

    def get_middle_index(self):
        """Returns the index at the center of Sky grid"""
        return int(self.get_num_rows() * self.get_num_columns() / 2.0)

    def get_note_from_coord(self, coord):
        '''Returns the note type Root, Diamond, Circle from the coords in Sky grid'''
        return notes.Note(self, coord)

    def set_skygrid(self, skygrid):
        if self.shape != skygrid.shape:
            raise ValueError(f"Skygrid shape {skygrid.shape} is not equal to instrument shape {self.shape}")
        self.skygrid = skygrid        

    def get_skygrid(self):
        return self.skygrid

class Drum(Harp):
    '''Any harmonic instrument with a 2x4 grid'''    
    type = 'drum'
    shape = (2,4)
    def __init__(self):
        super().__init__()
        self.skygrid = Skygrid(shape=self.shape) #do not change name as it is used by get_is_tonal() and get_is_textual()
    

#TEXTS = ['voice','lyric']
#HARPS = ['harp','drum']

