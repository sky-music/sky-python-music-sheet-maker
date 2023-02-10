from skymusic import instruments, Lang
from skymusic.renderers.song_renderers import html_sr, svg_sr, png_sr, midi_sr, skyjson_sr, ascii_sr
from skymusic.modes import RenderMode
from skymusic.resources import Resources

class Song():

    def __init__(self, locale=None, music_key=Resources.DEFAULT_KEY):

        if isinstance(music_key, str):
            self.music_key = music_key
        else:
            self.music_key = Resources.DEFAULT_KEY
            print("\n***ERROR: Invalid song key passed to Song(): using {self.music_key} instead")            

        self.locale = locale

        self.lines = []        
        self.meta = {
                    'title': [Lang.get_string("song_meta/title", self.locale) + ': ', Lang.get_string("song_meta/untitled", self.locale)],
                    'artist': [Lang.get_string("song_meta/artist", self.locale) + ': ', ''],
                    'transcript': [Lang.get_string("song_meta/transcript", self.locale) + ': ', ''],
                    'song_key': [Lang.get_string("song_meta/musical_key", self.locale) + ': ', '']}
        
        self.is_meta_changed = False
        
    def get_title(self):

        return self.meta['title'][1]

    def add_line(self, line):
        """Adds a line of Instrument to the Song"""
        if len(line) > 0: self.lines.append(line)

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
        return f"<{self.__class__.__name__} '{self.get_title()}', {self.get_num_lines()} lines, {self.get_num_instruments()} instruments, {self.get_num_broken()} errors>"

    def get_num_instruments(self):
        """Returns the number of instruments in the Song"""
        c = 0
        for line in self.lines:
            c += len(line)
        return c

    def get_harp_aspect_ratio(self):        
        
        aspect_ratio = 1
        
        if self.get_num_instruments() == 0:
            return aspect_ratio
        
        for line in self.lines:
            harp = line[0]
            try:
                aspect_ratio = harp.get_aspect_ratio()
                break
            except AttributeError:
                pass
                
        return aspect_ratio

    def get_harp_type(self):

        for line in self.lines:
            if line[0].get_type().lower() in instruments.HARPS:
                return line[0].get_type()
        
        return 'harp'            

    def get_num_broken(self):
        """Returns the number of broken instruments in the Song"""
        b = 0
        for line in self.lines:
            for harp in line:
                try:
                    b += int(harp.get_is_broken())
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

    def set_meta_changed(self, has_changed):
        
        self.is_meta_changed = has_changed

    def get_meta_changed(self):
        
        return self.is_meta_changed
                
    def set_meta(self, **kwargs):
        
        for k in kwargs:
            val = kwargs[k]
            try:
                if val and str(val).lower().strip():
                    self.meta[k][1] = val
            except KeyError:
                pass
                #self.meta[key] = kwargs[k]

            
    def render(self, render_mode, **kwargs):

        try:
            aspect_ratio = kwargs['aspect_ratio'].get_ratio()
        except (KeyError, AttributeError):
            aspect_ratio = 16/9.0
        
        theme = kwargs.get('theme', Resources.get_default_theme())
        
        gamepad = kwargs.get('gamepad', None)
        
        if render_mode == RenderMode.HTML:
            buffers = html_sr.HtmlSongRenderer(locale=self.locale, gamepad=gamepad, theme=theme).write_buffers(song=self, css_mode=kwargs['css_mode'])
        elif render_mode == RenderMode.SVG:
            buffers = svg_sr.SvgSongRenderer(locale=self.locale, gamepad=gamepad, aspect_ratio=aspect_ratio, theme=theme).write_buffers(song=self, css_mode=kwargs['css_mode'])
        elif render_mode == RenderMode.PNG:
            buffers = png_sr.PngSongRenderer(locale=self.locale, gamepad=gamepad, aspect_ratio=aspect_ratio, theme=theme).write_buffers(song=self)
        elif render_mode == RenderMode.MIDI:
            buffers = midi_sr.MidiSongRenderer(self.locale, kwargs['song_bpm']).write_buffers(song=self)
        elif render_mode == RenderMode.SKYJSON:
            buffers = skyjson_sr.SkyjsonSongRenderer(self.locale, kwargs['song_bpm']).write_buffers(song=self)    
        else:  # Ascii
            buffers = ascii_sr.AsciiSongRenderer(self.locale).write_buffers(song=self, render_mode=render_mode)

        return buffers
       
        
