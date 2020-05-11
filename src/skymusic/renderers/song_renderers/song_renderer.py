from src.skymusic import Lang

class SongRenderer():
    
    def __init__(self, locale=None):
        
        if locale is None:
            self.locale = Lang.guess_locale()
            print(f"**WARNING: Song self.maker has no locale. Reverting to: {self.locale}")
        else:
            self.locale = locale


    def write_buffers(self, song, **kwargs):
        
        return