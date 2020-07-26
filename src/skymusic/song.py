from src.skymusic import instruments, Lang
from src.skymusic.renderers.song_renderers import html_sr, svg_sr, png_sr, midi_sr, skyjson_sr, ascii_sr
from src.skymusic.modes import RenderMode
from src.skymusic.resources import Resources

class Song():

    def __init__(self, locale=None, music_key='C'):

        if isinstance(music_key, str):
            self.music_key = music_key
        else:
            self.music_key = Resources.DEFAULT_KEY
            print("\n***ERROR: Invalid song key passed to Song(): using {self.music_key} instead")            

        self.locale = locale

        self.lines = []        
        self.meta = {
                    'title': [Lang.get_string("song_meta/title", self.locale) + ':', Lang.get_string("song_meta/untitled", self.locale)],
                    'artist': [Lang.get_string("song_meta/artist", self.locale) + ': ', ''],
                    'transcript': [Lang.get_string("song_meta/transcript", self.locale) + ': ', ''],
                    'song_key': [Lang.get_string("song_meta/musical_key", self.locale) + ': ', '']}

    def get_title(self):

        return self.meta['title'][1]

    def add_line(self, line):
        """Adds a line of Instrument to the Song"""
        if len(line) > 0:
            if isinstance(line[0], instruments.Instrument):
                self.lines.append(line)

    def get_line(self, row):
        """Returns line #row, if row is in the Song, or else returns an empty list"""
        try:
            return self.lines[row]
        except:
            return [[]]

    def get_music_key(self):

        return self.music_key

    def get_lines(self):
        """Returns the Song, a list of lists of Instruments"""
        return self.lines

    def get_instrument(self, row, col):
        """Returns the Instrument object at row, col in the Song"""
        try:
            return self.lines[row][col]
        except Exception as ex:
            return []
            raise ex

    def get_num_lines(self):
        """Returns the number of lines n the Song"""
        return len(self.lines)

    def __len__(self):
        return self.get_num_instruments()

    def __str__(self):
        return f"<{self.__clas__.__name__} '{self.get_title()}', {self.get_num_lines()} lines, {self.get_num_instruments()} instruments, {self.get_num_broken()} errors>"

    def get_num_instruments(self):
        """Returns the number of instruments in the Song"""
        c = 0
        for line in self.lines:
            c += len(line)
        return c

    def get_num_broken(self):
        """Returns the number of broken instruments in the Song"""
        b = 0
        for line in self.lines:
            for instr in line:
                try:
                    b += int(instr.get_is_broken())
                except:
                    pass
        return b

    def get_max_instruments_per_line(self):
        """Returns the number of instruments in the longest line"""
        if len(self.lines) > 0:
            return max(list(map(len, self.lines)))
        else:
            return 0     
    
    def get_meta(self):
        
        return self.meta
                
    def set_meta(self, **kwargs):
                
        for k in kwargs:
            try:
                if kwargs[k].lower().strip() != '':
                    self.meta[k.lower().strip()][1] = kwargs[k]
            except KeyError:
                pass
            
    def render(self, render_mode, **kwargs):

        try:
            aspect_ratio = kwargs['aspect_ratio'].get_ratio()
        except (KeyError, AttributeError):
            aspect_ratio = 16/9.0
        
        try:
            theme = kwargs['theme']
        except KeyError:
            theme = Resources.get_default_theme()
        
        if render_mode == RenderMode.HTML:
            buffers = html_sr.HtmlSongRenderer(locale=self.locale, theme=theme).write_buffers(song=self, css_mode=kwargs['css_mode'])
        elif render_mode == RenderMode.SVG:
            buffers = svg_sr.SvgSongRenderer(locale=self.locale, aspect_ratio=aspect_ratio, theme=theme).write_buffers(song=self, css_mode=kwargs['css_mode'])
        elif render_mode == RenderMode.PNG:
            buffers = png_sr.PngSongRenderer(locale=self.locale, aspect_ratio=aspect_ratio, theme=theme).write_buffers(song=self)
        elif render_mode == RenderMode.MIDI:
            buffers = midi_sr.MidiSongRenderer(self.locale, kwargs['song_bpm']).write_buffers(song=self)
        elif render_mode == RenderMode.SKYJSON:
            buffers = skyjson_sr.SkyjsonSongRenderer(self.locale, kwargs['song_bpm']).write_buffers(song=self)    
        else:  # Ascii
            buffers = ascii_sr.AsciiSongRenderer(self.locale).write_buffers(song=self, render_mode=render_mode)

        return buffers
       
        
