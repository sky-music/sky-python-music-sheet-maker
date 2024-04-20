import re
from skymusic.resources import Resources
"""A collection of objects that can be put in song lines in lieu of instruments"""

class PseudoInstrument():

    def __init__(self):
        self.type = None #mandatory
        self.index = 0 # mandatory to avoid errors
        self.repeat = 0 # Mandatory to avoid errors
        self.is_tonal = False
        self.is_textual = False
        
    def get_type(self):
        return self.type
    
    #Mandatory because called by Song.get_harp_type()
    def get_is_tonal(self): return False
    
    def get_is_textual(self):
        return getattr(self, 'text','') != ''
        
    def get_is_decorative(self): return False
    
    def set_index(self, index): self.index = index
        
    def get_index(self): return self.index 
 
    def set_repeat(self, repeat): self.repeat = repeat

    def get_repeat(self):
        """Returns the number of times the instrument must be played"""
        return self.repeat
        
        
class Ruler(PseudoInstrument):
    
    codes = Resources.MARKDOWN_CODES['rulers']
    
    def __init__(self, code=None):
        super().__init__()
        self.type = 'ruler' #mandatory
        self.code = None
        if code: self.set_code(code)
        self.text = ""
        self.emphasis = ''
    
    def get_is_decorative(self): return True
    
    def set_text(self, text: str):
        self.text = text[:64].strip()
        
        h_match = re.match(r'(?<!")(?P<emphasis>#*)(?P<lyric>.*)',self.text)
        h = len(h_match.group('emphasis'))
        if h>0:
            self.text = h_match.group('lyric')
            self.emphasis = f'h{h}'
        else:
            star_match = re.match(r'(?P<start>\**)(?P<lyric>[^\*]*)(?P<end>\**)',self.text)
            self.text = star_match.group('lyric')
            if len(star_match.group('start')) >= 2 and len(star_match.group('end')) >= 2:
                self.emphasis = 'b'
            elif (len(star_match.group('start')) == 1 and len(star_match.group('end')) == 1):
                self.emphasis = 'i'    
        
    def get_text(self):
        return self.text

    def get_emphasis(self):
        return self.emphasis
    
    def set_code(self, code):
        if code not in self.codes:
            raise KeyError("Invalid %s code:'%s'. Valid codes are: %s" % (self.type, code, ','.join(self.codes)))
        else:
            self.code = code
        return code

    def get_code(self):
        return self.code

    def __len__(self):
        return len(self.code)

    def __str__(self):
        return str(self.code)

    def __repr__(self):
        return f"<{self.type}, {len(self)} chars, code='{self.code}', text='{self.text}'>"
        
class Layer(Ruler):
    
    codes = [Resources.DELIMITERS['layer']]
    
    def __init__(self):
        super().__init__()
        self.type = 'layer'
        
