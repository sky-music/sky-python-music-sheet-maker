from . import instrument_renderer
from src.skymusic import notes
from src.skymusic.resources import Resources

try:
    from PIL import Image, ImageDraw, ImageFont

    no_PIL_module = False
except (ImportError, ModuleNotFoundError):
    no_PIL_module = True


class PngInstrumentRenderer(instrument_renderer.InstrumentRenderer):
    
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
        self.harp_font_size = Resources.harp_font_size
        self.repeat_height = None

        self.voice_font_size = Resources.voice_font_size
        # self.text_bkg = (255, 255, 255, 0)#Uncomment to make it different from the inherited class
        # self.font_color = (255,255,255)#Uncomment to make it different from the inherited class
        # self.font = 'fonts/NotoSansCJKjp-Regular.otf'

    def trans_paste(self, bg, fg, box=(0, 0)):
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
            harp_render = self.trans_paste(harp_render, symbol, (
                int((harp_size[0] - symbol.size[0]) / 2.0), int((harp_size[1] - symbol.size[1]) / 2.0)))
        elif harp_silent:  # '.' in the middle of the image (no harp around)
            symbol = Image.open(self.silent_png)
            harp_render = self.trans_paste(harp_render, symbol, (
                int((harp_size[0] - symbol.size[0]) / 2.0), int((harp_size[1] - symbol.size[1]) / 2.0)))
        else:
            harp_render = self.trans_paste(harp_render, harp_file)  # default harp image
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
                        harp_render = self.trans_paste(harp_render, note_render, (int(round(xn)), int(round(yn))))

        if rescale != 1:
            harp_render = harp_render.resize((int(harp_render.size[0] * rescale), int(harp_render.size[1] * rescale)),
                                             resample=Image.LANCZOS)

        return harp_render
                