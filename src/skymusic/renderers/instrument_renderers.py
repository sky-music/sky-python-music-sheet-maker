#import os
#import io
from src.skymusic import notes
from src.skymusic.resources import Resources
from src.skymusic import Lang
from src.skymusic.instruments import Harp, Voice

try:
    from PIL import Image, ImageDraw, ImageFont

    no_PIL_module = False
except (ImportError, ModuleNotFoundError):
    no_PIL_module = True

try:
    import mido

    no_mido_module = False
except (ImportError, ModuleNotFoundError):
    no_mido_module = True


class InstrumentRenderer():

    def __init__(self, locale=None):
        
        if locale is None:
            self.locale = Lang.guess_locale()
            print(f"**WARNING: Song self.maker has no locale. Reverting to: {self.locale}")
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
            

class InstrumentHTMLRenderer(InstrumentRenderer):
    
    def __init__(self, locale=None):
        super().__init__(locale)

    def render_harp(self, instrument, note_width='1em'):
        """
        Renders the Instrument in HTML
        """
        harp_silent = instrument.get_is_silent()
        harp_broken = instrument.get_is_broken()

        if harp_broken:
            class_suffix = "broken"
        elif harp_silent:
            class_suffix = "silent"
        else:
            class_suffix = ''

        harp_render = f'<table class="harp harp-{instrument.get_index()} {class_suffix}">'

        for row in range(instrument.get_row_count()):

            harp_render += '<tr>'
            for col in range(instrument.get_column_count()):
                note = instrument.get_note_from_position((row, col))
                note_render = note.render_in_html(note_width)                
                harp_render += f'<td>{note_render}</td>'
            harp_render += '</tr>'

        harp_render += '</table>'

        if instrument.get_repeat() > 1:
            harp_render += (f'<table class="harp-{instrument.get_index()} repeat">'
                            f'<tr><td>x{instrument.get_repeat()}</td></tr>'
                            f'</table>')

        return harp_render

    def render_voice(self, instrument, note_width):
        """Renders the lyrics text in HTML inside an invisible table"""
        chord_render = f'<table class="voice"><tr><td>{instrument.lyric}</td></tr></table>'
        return chord_render



class InstrumentSVGRenderer(InstrumentRenderer):
    
    def __init__(self, locale=None):
        super().__init__(locale)

    def render_voice(self, instrument, x, width: str, height: str, aspect_ratio):
        """Renders the lyrics text in SVG"""
        voice_render = (f'\n<svg x="{x :.2f}" y="0" width="100%" height="{height}" class="voice voice-{instrument.get_index()}">'
                        f'\n<text x="0%" y="50%" class="voice voice-{instrument.get_index()}">{instrument.lyric}</text>'
                        f'\n</svg>')

        return voice_render


    def render_harp(self, instrument, x, harp_width, harp_height, aspect_ratio):
        """
        Renders the Instrument in SVG
        """
        harp_silent = instrument.get_is_silent()
        harp_broken = instrument.get_is_broken()

        if harp_broken:
            class_suffix = "broken"
        elif harp_silent:
            class_suffix = "silent"
        else:
            class_suffix = ''

        # The chord SVG container
        harp_render = f'\n<svg x="{x :.2f}" y="0" width="{harp_width}" height="{harp_height}" class="instrument-harp harp-{instrument.get_index()} {class_suffix}">'

        # The chord rectangle with rounded edges
        harp_render += f'\n<rect x="0.7%" y="0.7%" width="98.6%" height="98.6%" rx="7.5%" ry="{7.5 * aspect_ratio :.2f}%" class="harp harp-{instrument.get_index()}"/>'

        for row in range(instrument.get_row_count()):
            for col in range(instrument.get_column_count()):
                note = instrument.get_note_from_position((row, col))
                # note.set_position(row, col)

                note_width = 0.21
                xn = 0.12 + col * (1 - 2 * 0.12) / (instrument.get_column_count() - 1) - note_width / 2.0
                yn = 0.15 + row * (1 - 2 * 0.16) / (instrument.get_row_count() - 1) - note_width / 2.0

                # NOTE RENDER
                harp_render += note.render_in_svg(f"{100*note_width :.2f}%", f"{100*xn :.2f}%", f"{100*yn :.2f}%")

        harp_render += '</svg>'

        return harp_render


class InstrumentPNGRenderer(InstrumentRenderer):
    
    def __init__(self, locale=None):
        super().__init__(locale)
        
        self.empty_chord_png = Resources.empty_chord_png
        self.unhighlighted_chord_png = Resources.unhighlighted_chord_png
        self.broken_png = Resources.broken_png
        self.silent_png = Resources.silent_png

        self.png_chord_size = None
        self.text_bkg = (255, 255, 255, 0)  # Transparent white
        self.song_bkg = (255, 255, 255)  # White paper sheet
        self.font_color = (0, 0, 0)
        
        self.font = Resources.font_path
        self.harp_font_size = 38
        self.repeat_height = None

        self.voice_font_size = 32
        # self.text_bkg = (255, 255, 255, 0)#Uncomment to make it different from the inherited class
        # self.font_color = (255,255,255)#Uncomment to make it different from the inherited class
        # self.font = 'fonts/NotoSansCJKjp-Regular.otf'

 
    def set_png_chord_size(self):
        """ Sets the size of the chord image from the .png file """
        if self.png_chord_size is None:
            self.png_chord_size = Image.open(self.unhighlighted_chord_png).size

    def get_png_chord_size(self):
        """ Returns the size of the chord image, or sets it if None """
        if self.png_chord_size is None:
            self.set_png_chord_size()
        return self.png_chord_size

    def get_repeat_png(self, instrument, max_rescaled_width, rescale=1):
        """Returns an image of the repeat number xN"""
        repeat_im = Image.new('RGBA', (int(max_rescaled_width / rescale), int(self.get_png_chord_size()[1])),
                              color=self.text_bkg)
        draw = ImageDraw.Draw(repeat_im)
        fnt = ImageFont.truetype(self.font, self.harp_font_size)
        draw.text((0, repeat_im.size[1] - 1.05 * fnt.getsize(str(instrument.get_repeat()))[1]), 'x' + str(instrument.get_repeat()), font=fnt,
                  fill=self.font_color)

        if rescale != 1:
            repeat_im = repeat_im.resize((int(repeat_im.size[0] * rescale), int(repeat_im.size[1] * rescale)),
                                         resample=Image.LANCZOS)

        return repeat_im


    def get_lyric_height(self):
        """Calculates the height of the lyrics based on a standard text and the font size"""
        fnt = ImageFont.truetype(self.font, self.voice_font_size)
        return fnt.getsize('HQfgjyp')[1] #Uppercase H and characters with tails
   

    def render_voice(self, instrument, rescale=1.0):
        """Renders the lyrics text in PNG"""
        lyric = instrument.get_lyric()
        chord_size = self.get_png_chord_size()
        fnt = ImageFont.truetype(self.font, int(self.voice_font_size))
        lyric_width = fnt.getsize(lyric)[0]

        lyric_im = Image.new('RGBA', (int(max(chord_size[0], lyric_width)), int(self.get_lyric_height())),
                             color=self.text_bkg)
        draw = ImageDraw.Draw(lyric_im)

        if lyric_width < chord_size[0]:
            # Draws centered text
            draw.text((int((chord_size[0] - lyric_width) / 2.0), 0), lyric, font=fnt, fill=self.font_color)
        else:
            # Draws left-aligned text that spilles over the next icon
            draw.text((0, 0), lyric, font=fnt, fill=self.font_color)

        if rescale != 1:
            lyric_im = lyric_im.resize((int(lyric_im.size[0] * rescale), int(lyric_im.size[1] * rescale)),
                                       resample=Image.LANCZOS)
        return lyric_im


    def render_harp(self, instrument, rescale=1.0):
        def trans_paste(bg, fg, box=(0, 0)):
            if fg.mode == 'RGBA':
                if bg.mode != 'RGBA':
                    bg = bg.convert('RGBA')
                fg_trans = Image.new('RGBA', bg.size)
                fg_trans.paste(fg, box, mask=fg)  # transparent foreground
                return Image.alpha_composite(bg, fg_trans)
            else:
                if bg.mode == 'RGBA':
                    bg = bg.convert('RGB')
                bg.paste(fg, box)
                return bg

        harp_silent = instrument.get_is_silent()
        harp_broken = instrument.get_is_broken()

        harp_file = Image.open(self.unhighlighted_chord_png)  # loads default harp image into memory
        harp_size = harp_file.size

        harp_render = Image.new('RGB', harp_file.size, self.song_bkg)  # Empty image

        # Get a typical note to check that the size of the note png is consistent with the harp png                  
        note_size = notes.Note(instrument).get_png_size()
        note_rel_width = note_size[0] / harp_size[0]  # percentage of harp
        if note_rel_width > 1.0 / instrument.get_column_count() or note_rel_width < 0.05:
            note_rescale = 0.153 / note_rel_width
        else:
            note_rescale = 1

        if harp_broken:  # '?' in the middle of the image (no harp around)
            symbol = Image.open(self.broken_png)
            harp_render = trans_paste(harp_render, symbol, (
                int((harp_size[0] - symbol.size[0]) / 2.0), int((harp_size[1] - symbol.size[1]) / 2.0)))
        elif harp_silent:  # '.' in the middle of the image (no harp around)
            symbol = Image.open(self.silent_png)
            harp_render = trans_paste(harp_render, symbol, (
                int((harp_size[0] - symbol.size[0]) / 2.0), int((harp_size[1] - symbol.size[1]) / 2.0)))
        else:
            harp_render = trans_paste(harp_render, harp_file)  # default harp image
            for row in range(instrument.get_row_count()):
                for col in range(instrument.get_column_count()):

                    note = instrument.get_note_from_position((row, col))
                    # note.set_position(row, col)

                    # NOTE RENDER
                    if len(note.get_highlighted_frames()) > 0:  # Only paste highlighted notes
                        xn = (0.13 + col * (1 - 2 * 0.13) / (instrument.get_column_count() - 1)) * harp_size[0] - note_size[
                            0] / 2.0
                        yn = (0.17 + row * (1 - 2 * 0.17) / (instrument.get_row_count() - 1)) * harp_size[1] - note_size[
                            1] / 2.0
                        note_render = note.render_in_png(note_rescale)
                        harp_render = trans_paste(harp_render, note_render, (int(round(xn)), int(round(yn))))

        if rescale != 1:
            harp_render = harp_render.resize((int(harp_render.size[0] * rescale), int(harp_render.size[1] * rescale)),
                                             resample=Image.LANCZOS)

        return harp_render
                

class InstrumentASCIIRenderer(InstrumentRenderer):
    
    def __init__(self, locale=None):
        super().__init__(locale)


    def render_harp(self, instrument, note_parser=None):

        ascii_chord = ''

        if instrument.get_is_broken():
            ascii_chord = 'X'
        elif instrument.get_is_silent():
            ascii_chord = '.'
        else:
            chord_skygrid = instrument.get_chord_skygrid()
            for k in chord_skygrid:  # Cycle over positions in a frame
                for f in chord_skygrid[k]:  # Cycle over triplets & quavers
                    if chord_skygrid[k][f]:  # Button is highlighted
                        ascii_chord += note_parser.get_note_from_coordinate(k)
        return ascii_chord


    def render_voice(self, instrument, render_mode):
        chord_render = "#%s " % instrument.get_lyric()  # Lyrics marked as comments in output text files
        return chord_render


class InstrumentMIDIRenderer(InstrumentRenderer):
    
    def __init__(self, locale=None):
        super().__init__(locale)

        self.midi_relspacing = 0.1  # Spacing between midi notes, as a ratio of note duration
        self.midi_pause_relduration = 1  # Spacing between midi notes, as a ratio of note duration
        self.midi_quaver_relspacing = 0.5

    def render_harp(self, instrument, note_duration=960, music_key='C'):
        harp_silent = instrument.get_is_silent()
        harp_broken = instrument.get_is_broken()

        if harp_broken:
            harp_render = [
                mido.Message('note_on', note=115, velocity=127, time=int(self.midi_relspacing * note_duration)),
                mido.Message('note_off', note=115, velocity=127, time=int(self.midi_relspacing * note_duration))]
        elif harp_silent:
            harp_render = [
                mido.Message('note_on', note=115, velocity=0, time=int(self.midi_relspacing * note_duration)),
                mido.Message('note_off', note=115, velocity=0, time=int(self.midi_pause_relduration * note_duration))]
        else:
            harp_render = []
            durations = [self.midi_relspacing * note_duration, note_duration]
            for i, event_type in enumerate(['note_on', 'note_off']):
                t = durations[i]
                for row in range(instrument.get_row_count()):
                    for col in range(instrument.get_column_count()):
                        note = instrument.get_note_from_position((row, col))
                        frames = note.get_highlighted_frames()

                        note_render = note.render_in_midi(event_type, t, music_key)

                        if isinstance(note_render, mido.Message):
                            harp_render.append(note_render)
                            # Below a complicated way to handle quavers
                            if frames[0] == 0 or event_type == 'note_off':
                                t = 0
                            elif frames[0] > 0 and event_type == 'note_on':
                                t = durations[0] + durations[1]
                            else:
                                t = durations[i]

        return harp_render


    def render_voice(self, *args, **kwargs):    

        return NotImplemented
        