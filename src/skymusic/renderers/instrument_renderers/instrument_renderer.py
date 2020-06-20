from src.skymusic import Lang
from src.skymusic.instruments import Harp, Voice

class InstrumentRenderer():

    def __init__(self, locale=None):
        
        if locale is None:
            self.locale = Lang.guess_locale()
            print(f"**ERROR: Song self.maker has no locale. Reverting to: {self.locale}")
        else:
            self.locale = locale


    def render(self, *args, **kwargs):
        
        try:
            instrument = args[0]        
        except IndexError:
            instrument = kwargs['instrument']

        if isinstance(instrument, Harp):
            return self.render_harp(*args, **kwargs)
        elif isinstance(instrument, Voice):
            return self.render_voice(*args, **kwargs)
        else:
            raise TypeError(f"Expected Harp or Voice, got:{instrument.__class__.__name__}")
            
