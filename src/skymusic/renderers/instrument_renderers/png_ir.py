from . import instrument_renderer
from skymusic.resources import Resources
from skymusic.renderers.note_renderers import png_nr


try:
    from PIL import Image, ImageDraw, ImageFont

    no_PIL_module = False
except (ImportError, ModuleNotFoundError):
    no_PIL_module = True


class PngInstrumentRenderer(instrument_renderer.InstrumentRenderer):
    
    def __init__(self, locale=None, harp_type='harp', gamepad=None):
        super().__init__(locale)
        self.gamepad = gamepad
        
        self.broken_png = Resources.PNGS['broken-symbol']
        self.silent_png = Resources.PNGS['silent-symbol']

        self.text_bkg = Resources.PNG_SETTINGS['text_bkg']  # Transparent white
        self.song_bkg = Resources.PNG_SETTINGS['song_bkg'] # White paper sheet
        self.font_color = Resources.PNG_SETTINGS['font_color']       
        self.font_path = Resources.PNG_SETTINGS['font_path']
        self.harp_font_size = Resources.PNG_SETTINGS['harp_font_size']
        self.png_font_size = Resources.PNG_SETTINGS['png_font_size']
        self.png_h1_font_size = Resources.PNG_SETTINGS['png_h1_font_size']
        self.png_h2_font_size = Resources.PNG_SETTINGS['png_h2_font_size']
        self.png_font_path = Resources.PNG_SETTINGS['font_path']
        self.repeat_height = None
        self.voice_font_size = Resources.PNG_SETTINGS['voice_font_size']
        self.hr_color = Resources.PNG_SETTINGS['hr_color']  # Transparent white
        try:
            self.voice_font = ImageFont.truetype(self.font_path, self.voice_font_size)
            self.harp_font = ImageFont.truetype(self.font_path, self.harp_font_size)
            self.h1_font = ImageFont.truetype(self.png_font_path, self.png_h1_font_size)
            self.h2_font = ImageFont.truetype(self.png_font_path, self.png_h2_font_size)
            self.text_font = ImageFont.truetype(self.png_font_path, self.png_font_size)
        except OSError:
            self.voice_font = ImageFont.load_default()
            self.harp_font = ImageFont.load_default()
            self.h1_font = ImageFont.load_default()
            self.h2_font = ImageFont.load_default()
            self.text_font = ImageFont.load_default()

        self.png_harp_size = None
        self.harp_type = harp_type
        self.empty_harp_png = Resources.PNGS[f'empty-{harp_type}']
        self.unhighlighted_harp_png = Resources.PNGS[f'unhighlighted-{harp_type}']

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

 
    def set_png_harp_size(self):
        """ Sets the size of the instrument image from the .png file """
        if self.png_harp_size is None:
            self.png_harp_size = Image.open(self.unhighlighted_harp_png).size

    def get_png_harp_size(self):
        """ Returns the size of the instrument image, or sets it if None """
        if self.png_harp_size is None:
            self.set_png_harp_size()
        return self.png_harp_size

    def get_repeat_png(self, instrument, max_rescaled_width, rescale=1):
        """Returns an image of the repeat number xN"""
        repeat_im = Image.new('RGBA', (int(max_rescaled_width / rescale), int(self.get_png_harp_size()[1])),
                              color=self.text_bkg)
        draw = ImageDraw.Draw(repeat_im)
        #fnt = ImageFont.truetype(self.font_path, self.harp_font_size)
        fnt = self.harp_font
        draw.text((0, repeat_im.size[1] - 1.05 * fnt.getsize(str(instrument.get_repeat()))[1]), 'x' + str(instrument.get_repeat()), font=fnt,
                  fill=self.font_color)

        if rescale != 1:
            repeat_im = repeat_im.resize((int(repeat_im.size[0] * rescale), int(repeat_im.size[1] * rescale)),
                                         resample=Image.LANCZOS)

        return repeat_im


    def get_lyric_height(self):
        """Calculates the height of the lyrics based on a standard text and the font size"""
        #fnt = ImageFont.truetype(self.font_path, self.voice_font_size)
        fnt = self.voice_font
        return fnt.getsize('HQfgjyp')[1] #Uppercase H and characters with tails

    def __scaled_font__(self, font_size, rescale):
        return ImageFont.truetype(self.png_font_path, int(font_size*rescale))
   
    def render_ruler(self, ruler, rescale=1.0, max_size=None): # Should add options
        """Renders an horizontal ruler"""
        #harp_size = self.get_png_harp_size() # Will be replaced by option
        hr_render = Image.new('RGBA', (int(max_size[0]), int(max_size[1])),
                             color=self.text_bkg)
        draw = ImageDraw.Draw(hr_render)
        
        rulerH = 2
        rulerW = int(max_size[0])
        
        code = ruler.get_code()
        if code == '__':
            draw.line([(0,0),(rulerW,0)], fill=self.hr_color, width=rulerH)
        elif code == '--':
            xl = 0
            dashW = max(1,rulerW/200)
            dashS = dashW # 50% dash
            while xl < rulerW:
                draw.line([(xl,0),(xl+dashW,0)], fill=self.hr_color, width=rulerH)
                xl += dashW + dashS
            
        elif code == '==':
            draw.line([(0,0),(rulerW,0)], fill=self.hr_color, width=rulerH)
            draw.line([(0,4*rulerH),(rulerW,4*rulerH)], fill=self.hr_color, width=rulerH)
        else:
            raise KeyError(code)

        # No rescaling for the ruler (which is 1D and should extend to the full page width)
        text = ruler.get_text()
        emphasis = ruler.get_emphasis().lower()
        if text: 
            if emphasis == 'h1':
                fnt = self.__scaled_font__(self.png_h1_font_size, rescale)
            elif emphasis == 'h2':
                fnt = self.__scaled_font__(self.png_h2_font_size, rescale)   
            else:
                fnt = self.__scaled_font__(self.png_font_size, rescale)
                
            draw.text((0, 6*rulerH), text, font=fnt, fill=self.font_color)
        
        return hr_render

    def render_layer(self,*args,**kwargs):
        return self.render_ruler(*args,**kwargs)

    def render_voice(self, instrument, rescale=1.0, max_size=None):
        """Renders the lyrics text in PNG"""
        lyric = instrument.get_lyric(strip_html=True)
        harp_size = self.get_png_harp_size()
        #fnt = ImageFont.truetype(self.font_path, int(self.voice_font_size))
        fnt = self.voice_font
        lyric_width = fnt.getsize(lyric)[0]

        lyric_render = Image.new('RGBA', (int(max(harp_size[0], lyric_width)), int(self.get_lyric_height())),
                             color=self.text_bkg)
        draw = ImageDraw.Draw(lyric_render)

        if lyric_width < harp_size[0]:
            # Draws centered text
            draw.text((int((harp_size[0] - lyric_width) / 2.0), 0), lyric, font=fnt, fill=self.font_color)
        else:
            # Draws left-aligned text that spilles over the next icon
            draw.text((0, 0), lyric, font=fnt, fill=self.font_color)

        # Rescaling
        if max_size is not None:
            rescale =  min(rescale,max_size[0]/lyric_render.size[0])
            rescale =  min(rescale,max_size[1]/lyric_render.size[1])

        if rescale != 1:
            lyric_render = lyric_render.resize((int(lyric_render.size[0] * rescale), int(lyric_render.size[1] * rescale)),
                                       resample=Image.LANCZOS)
        return lyric_render


    def render_harp(self, instrument, rescale=1.0, max_size=None):

        harp_silent = instrument.get_is_silent()
        harp_broken = instrument.get_is_broken()

        note_renderer = png_nr.PngNoteRenderer(gamepad=self.gamepad)

        harp_file = Image.open(self.unhighlighted_harp_png)  # loads default harp image into memory
        harp_size = harp_file.size

        harp_render = Image.new('RGB', harp_file.size, self.song_bkg)  # Empty image
        
        # Get a typical note to check that the size of the note png is consistent with the harp png                  
        #note_size = notes.Note(instrument).get_png_size()
        note_size = png_nr.PngNoteRenderer(gamepad=self.gamepad).get_png_size()
        
        note_rel_width = note_size[0] / harp_size[0]  # percentage of harp
        if note_rel_width > 1.0 / instrument.get_num_columns() or note_rel_width < 0.05:
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
            
            adjustement = (instrument.get_aspect_ratio()/(5/3))**2
            xn0 = 0.13*adjustement
            yn0 = 0.17*adjustement            
            
            for row in range(instrument.get_num_rows()):
                for col in range(instrument.get_num_columns()):

                    note = instrument.get_note_from_position((row, col))
                    # note.set_position(row, col)

                    # NOTE RENDER
                    if len(note.get_highlighted_frames()) > 0:  # Only paste highlighted notes
                        xn = (xn0 + col * (1 - 2 * xn0) / (instrument.get_num_columns() - 1)) * harp_size[0] - note_size[
                            0] / 2.0
                        yn = (yn0 + row * (1 - 2 * yn0) / (instrument.get_num_rows() - 1)) * harp_size[1] - note_size[
                            1] / 2.0
                        note_render = note_renderer.render(note=note, rescale=note_rescale)
                        harp_render = self.trans_paste(harp_render, note_render, (int(round(xn)), int(round(yn))))

        # Rescaling
        if max_size is not None:
            rescale =  min(rescale,max_size[0]/harp_render.size[0])
            rescale =  min(rescale,max_size[1]/harp_render.size[1])

        if rescale != 1:
            harp_render = harp_render.resize((int(harp_render.size[0] * rescale), int(harp_render.size[1] * rescale)),
                                             resample=Image.LANCZOS)

            
        return harp_render
                


