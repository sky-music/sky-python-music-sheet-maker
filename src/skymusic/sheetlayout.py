from skymusic.resources import Resources

class Ruler():
    
    def __init__(self):
        super().__init__()
        self.type = 'ruler'
        self.code = None
        self.content = ""
        self.index = 0
        self.repeat = 0
    
    def get_type(self):
        return self.type
    
    def set_index(self, index):
        self.index = index
        
    def set_content(self, text: str):
        text = text[:64]

    def get_content(self):
        return self.content

    def get_index(self):
        """ index in the song"""
        return self.index 
 
    def set_repeat(self, repeat):
        self.repeat = repeat

    def get_repeat(self):
        """Returns the number of times the instrument must be played"""
        return self.repeat    
    
    def set_code(self, text):
        if text not in Resources.MARKDOWN_CODES['rulers']:
            raise KeyError(text+' not a valid Markdown ruler code')
        else:
            self.code = text

    def get_code(self):
        return self.code

    def __len__(self):
        return len(self.code)

    def __str__(self):
        return str(self.code)

    def __repr__(self):
        return f"<{self.type}, {len(self)} chars, code='{self.code}'>"
        
