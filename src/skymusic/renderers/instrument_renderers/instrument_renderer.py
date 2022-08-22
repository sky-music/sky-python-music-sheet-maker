from skymusic import Lang
from skymusic.instruments import Voice
from skymusic.sheetlayout import Ruler

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

        if isinstance(instrument, Voice):
            return self.render_voice(*args, **kwargs)
        elif isinstance(instrument, Ruler):
            return self.render_ruler(*args, **kwargs)
        else:
            return self.render_harp(*args, **kwargs)
            
