from . import instrument_renderer
from skymusic.resources import Resources
from skymusic.renderers.note_renderers import png_nr
from skymusic.modes import GamePlatform

try:
    from PIL import Image, ImageDraw, ImageFont
    no_PIL_module = False
except ModuleNotFoundError:
    no_PIL_module = True
except ImportError as err:
    no_PIL_module = True
    print(err)


class PngInstrumentRenderer(instrument_renderer.InstrumentRenderer):
    
    def __init__(self, locale=None, harp_type='harp', platform_name=GamePlatform.get_default().get_name(), gamepad=None):
        super().__init__(locale)
        self.gamepad = gamepad
        self.platform_name = platform_name
        
        #Gaps, must end with V or H
        self.gamepad_gaps = {'note-gapH': 0.43, 'note-gapV': 0.4, 'quaver-gapH': 0.2, 'line-gapV': 2, 'pauseH': 0.7-0.43} #Relative to note size
        
        self.broken_png = Resources.PNGS[platform_name]['broken-symbol']
        self.silent_png = Resources.PNGS[platform_name]['silent-symbol']

        self.text_bkg = Resources.PNG_SETTINGS['text_bkg']  # Transparent white
        self.song_bkg = Resources.PNG_SETTINGS['song_bkg'] # White paper sheet
        self.font_color = Resources.PNG_SETTINGS['font_color']       
        self.font_path = Resources.PNG_SETTINGS['font_path']
        self.harp_font_size = Resources.PNG_SETTINGS['harp_font_size']
        self.font_size = Resources.PNG_SETTINGS['font_size']
        self.h1_font_size = Resources.PNG_SETTINGS['h1_font_size']
        self.h2_font_size = Resources.PNG_SETTINGS['h2_font_size']
        self.font_path = Resources.PNG_SETTINGS['font_path']
        self.repeat_height = None
        self.voice_font_size = Resources.PNG_SETTINGS['voice_font_size']
        self.hr_color = Resources.PNG_SETTINGS['hr_color']  # Grey or White
        if not no_PIL_module:
            try:
                self.voice_font = ImageFont.truetype(self.font_path, self.voice_font_size)
                self.harp_font = ImageFont.truetype(self.font_path, self.harp_font_size)
                self.h1_font = ImageFont.truetype(self.font_path, self.h1_font_size)
                self.h2_font = ImageFont.truetype(self.font_path, self.h2_font_size)
                self.text_font = ImageFont.truetype(self.font_path, self.font_size)
            except OSError:
                self.voice_font = ImageFont.load_default()
                self.harp_font = ImageFont.load_default()
                self.h1_font = ImageFont.load_default()
                self.h2_font = ImageFont.load_default()
                self.text_font = ImageFont.load_default()

        self.harp_size = None
        self.gp_note_size = None
        self.harp_type = harp_type
        self.empty_harp_png = Resources.PNGS[platform_name][f'empty-{harp_type}']
        self.unhighlighted_harp_png = Resources.PNGS[platform_name][f'unhighlighted-{harp_type}']

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

 
    def set_harp_size(self):
        """ Sets the size of the instrument image from the .png file """
        if self.harp_size is None:
            self.harp_size = Image.open(self.unhighlighted_harp_png).size

    def get_harp_size(self):
        """ Returns the size of the instrument image, or sets it if None """
        if self.harp_size is None:
            self.set_harp_size()
        return self.harp_size

    def set_gp_note_size(self, rescale=1):
        self.gp_note_size = png_nr.PngNoteRenderer(platform_name=self.platform_name, gamepad=self.gamepad).get_note_size(rescale=rescale)
        return self.gp_note_size

    def get_gp_note_size(self, rescale=1):
        '''Gets note size'''
        if self.gp_note_size is None: self.set_gp_note_size(rescale=rescale)
        return self.gp_note_size


    def get_repeat_png(self, instrument, fit_size, rescale=1):
        """Returns an image of the repeat number xN"""
        repeat = instrument.get_repeat()
        repeat_str = 'x'+str(repeat) #e.g. x14
        
        if self.gamepad and instrument.get_is_silent():
            pause_im = self._render_gamepad_pause_()
            
            repeat_im = Image.new('RGBA', (pause_im.size[0]*(repeat-1), pause_im.size[1]))
            for i in range(1, repeat):
                x = (i-1)*pause_im.size[0]
                self.trans_paste(pause_im, repeat_im, (x,0))
            
        else:
            #fnt = ImageFont.truetype(self.font_path, self.harp_font_size)
            fnt = self.harp_font
            Hsize, Vsize = self.get_text_size(fnt,repeat_str)
            repeat_im = Image.new('RGBA', (Hsize, Vsize), color=self.text_bkg)
            draw = ImageDraw.Draw(repeat_im)
            draw.text((0, repeat_im.size[1] - 1.05 * Vsize), repeat_str, font=fnt, fill=self.font_color)
            rescale = rescale * min(min(1, fit_size[0] / Hsize), fit_size[1] / Vsize)

        if rescale != 1 and rescale > 0:
            repeat_im = repeat_im.resize((round(repeat_im.size[0] * rescale), round(repeat_im.size[1] * rescale)), resample=Image.LANCZOS)

        return repeat_im


    def get_gamepad_size(self, instrument, rescale=1):
        '''Get typical size of a gamepad layout'''
        if self.gp_note_size is None:  
            self.gp_note_size = png_nr.PngNoteRenderer(platform_name=self.platform_name, gamepad=self.gamepad).get_note_size(rescale=rescale)
            
        num_buttons = max(1,instrument.get_skygrid().get_max_num_by_frame()) #rows
        num_frames = max(1,instrument.get_skygrid().get_num_frames()) # cols
        
        if instrument.get_is_silent(): return (round(self.gamepad_gaps['pauseH']*self.gp_note_size[0]), round(self.gp_note_size[1]))
        
        return ( round((num_frames + self.gamepad_gaps['quaver-gapH']*(num_frames-1))*self.gp_note_size[0]),
                 round((num_buttons + self.gamepad_gaps['note-gapV']*(num_buttons-1))*self.gp_note_size[1]) )

       
    def get_gamepad_gaps(self):
        if self.gp_note_size is None:  
            self.gp_note_size = png_nr.PngNoteRenderer(platform_name=self.platform_name, gamepad=self.gamepad).get_note_size()        
        
        return {k:round(v*(self.gp_note_size[0] if k.endswith('H') else self.gp_note_size[1])) for k,v in self.gamepad_gaps.items()}
        

    def get_text_size(self, fnt=None, text='HQfgjyp', rescale=1):
        """Calculates the height of the voices based on a standard text and the font size"""
        #fnt = ImageFont.truetype(self.font_path, self.voice_font_size)
        fnt = fnt if fnt else self.voice_font
        sz = fnt.getsize(text)
        return (round(sz[0]*rescale), round(sz[1]*rescale))

    def __scaled_font__(self, font_size, rescale):
        return ImageFont.truetype(self.font_path, round(font_size*rescale))
   
    def render_ruler(self, ruler, rescale=1.0, max_size=None): # Should add options
        """Renders an horizontal ruler"""
        #harp_size = self.get_harp_size() # Will be replaced by option
        hr_render = Image.new('RGBA', (round(max_size[0]), round(max_size[1])),
                             color=self.text_bkg)

        draw = ImageDraw.Draw(hr_render)
        
        rulerH = 2
        rulerW = round(max_size[0])
        
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
                fnt = self.__scaled_font__(self.h1_font_size, rescale)
            elif emphasis == 'h2':
                fnt = self.__scaled_font__(self.h2_font_size, rescale)   
            else:
                fnt = self.__scaled_font__(self.font_size, rescale)
                
            draw.text((0, 6*rulerH), text, font=fnt, fill=self.font_color)
        
        return hr_render

    def render_layer(self,*args,**kwargs):
        return self.render_ruler(*args,**kwargs)

    def render_voice(self, instrument, rescale=1.0, max_size=None):
        """Renders the lyrics text in PNG"""
        lyric = instrument.get_lyric(strip_html=True)
        #harp_size = self.get_harp_size()
        if 0.3 < rescale < 3: #Safety margins
            fnt = self.__scaled_font__(self.voice_font_size, rescale)
        else:
            fnt = self.voice_font
            
        lyric_width, lyric_height = self.get_text_size(fnt, lyric)

        voice_render = Image.new('RGBA', (lyric_width, lyric_height), color=self.text_bkg)
        draw = ImageDraw.Draw(voice_render)
        # Draws left-aligned text that can spill over the next harp
        draw.text((0, 0), lyric, font=fnt, fill=self.font_color)

        # Rescaling
        if max_size is not None:
            rescale =  min(1,max_size[0]/voice_render.size[0])
            rescale =  min(1,max_size[1]/voice_render.size[1])
        if rescale != 1 and rescale > 0:
            voice_render = voice_render.resize((round(voice_render.size[0] * rescale), round(voice_render.size[1] * rescale)),
                                       resample=Image.LANCZOS)
        
        return voice_render

    def _render_gamepad_pause_(self):
        
        symbol = Image.open(self.silent_png)
        #harp_render = self.trans_paste(harp_render, symbol, ( round((harp_size[0] - symbol.size[0]) / 2.0),  round((harp_size[1] - symbol.size[1]) / 2.0)) )
        pause_rescale = self.gamepad_gaps.get('pauseH', 1)
        symbol = symbol.resize((round(symbol.size[0] * pause_rescale), round(symbol.size[1])), resample=Image.LANCZOS)
        
        return symbol

    def _render_gamepad_harp_(self, instrument, rescale=1.0):

        harp_silent = instrument.get_is_silent()
        harp_broken = instrument.get_is_broken()
        
        note_renderer = png_nr.PngNoteRenderer(platform_name=self.platform_name, gamepad=self.gamepad)
        
        # Required to get gamepad button name from note coord in the Skygrid
        note_parser = self.gamepad.get_note_parser(locale=self.locale, shape=instrument.get_shape()) #Cannot be sooner because we need instrument shape
        
        # No background harp image: size is determined from number of notes
        
        note_size = note_renderer.get_note_size()
        harp_size = self.get_gamepad_size(instrument)
        
        harp_render = Image.new('RGB', harp_size, self.song_bkg)  # Empty image
        
        if harp_broken:  # '?' in the middle of the image (no harp around)
            symbol = Image.open(self.broken_png)
            harp_render = self.trans_paste(harp_render, symbol, (
                round((harp_size[0] - symbol.size[0]) / 2.0), round((harp_size[1] - symbol.size[1]) / 2.0)))
        elif harp_silent:  # In gamepad layout, pauses are a blank
            harp_render = self._render_gamepad_pause_()
        else:
            
            xn0 = 0
            yn0 = 0
            xn = xn0
            yn = yn0
            row_gap = self.gamepad_gaps['note-gapV'] * note_size[1]
            #column_gap = self.gamepad_gaps['column-gap'] * note_size[0]
            quaver_gap = self.gamepad_gaps['quaver-gapH'] * note_size[0]
            
            frames = instrument.get_skygrid().get_highlighted_frames()
            # Render harp in vertical layout mode
            for ix, frame in enumerate(frames): # cols
                coords = instrument.get_skygrid().get_highlighted_coords(frame)
                yn = yn0
                for iy, coord in enumerate(coords): #rows

                    note = instrument.get_note_from_coord(coord)
                    # NOTE RENDER
                    if len(note.get_highlighted_frames()) > 0:  # Only paste highlighted notes
                        note_render = note_renderer.render(note=note, rescale=1, note_parser=note_parser)
                        harp_render = self.trans_paste(harp_render, note_render, (round(xn), round(yn)))
        
                        yn += note_size[1] + row_gap
                
                if coords:
                    xn += note_size[0] + quaver_gap
        
        return harp_render



    def _render_mobile_harp_(self, instrument, rescale=1.0):
        '''Render the harp as a 3x5 skygrid for mobilme and desktop PC platforms'''
        
        harp_silent = instrument.get_is_silent()
        harp_broken = instrument.get_is_broken()
        (rows, cols) = instrument.get_shape()

        note_renderer = png_nr.PngNoteRenderer(platform_name=self.platform_name, gamepad=self.gamepad)


        harp_file = Image.open(self.unhighlighted_harp_png)  # loads default harp image into memory
        harp_size = harp_file.size

        harp_render = Image.new('RGB', harp_file.size, self.song_bkg)  # Empty image
        
        # Get a typical note to check that the size of the note png is consistent with the harp png                  
        #note_size = notes.Note(instrument).get_note_size()
        note_size = note_renderer.get_note_size()
        
        # Make sure note is not too large or too small compared to the harp
        note_rel_width = note_size[0] / harp_size[0]  # percentage of harp
        if note_rel_width > 1.0/instrument.get_num_columns() or note_rel_width < 0.05:
            note_rescale = 0.153 / note_rel_width
        else:
            note_rescale = 1

        if harp_broken:  # '?' in the middle of the image (no harp around)
            symbol = Image.open(self.broken_png)
            harp_render = self.trans_paste(harp_render, symbol, (
                int((harp_size[0] - symbol.size[0]) / 2.0), round((harp_size[1] - symbol.size[1]) / 2.0)))
        elif harp_silent:  # '.' in the middle of the image (no harp around)
            symbol = Image.open(self.silent_png)
            harp_render = self.trans_paste(harp_render, symbol, (
                int((harp_size[0] - symbol.size[0]) / 2.0), int((harp_size[1] - symbol.size[1]) / 2.0)))
        else:
            harp_render = self.trans_paste(harp_render, harp_file)  # default harp image
            
            adjustement = (instrument.get_aspect_ratio()/(5/3))**2
            xn0 = 0.13*adjustement # horizontal position of first note, relatively to the harp left border
            yn0 = 0.17*adjustement # vertical position of first note, relatively to the harp left border       
            
            # Render harp with 3x5 Skygrid of colored notes
            for row in range(rows):
                for col in range(cols):

                    note = instrument.get_note_from_coord((row, col))

                    # NOTE RENDER
                    if len(note.get_highlighted_frames()) > 0:  # Only paste highlighted notes
                        xn = ( xn0 + col * (1 - 2 * xn0) / (cols - 1) ) * harp_size[0] - note_size[0]/2.0
                        yn = ( yn0 + row * (1 - 2 * yn0) / (rows - 1) ) * harp_size[1] - note_size[1]/2.0
                        note_render = note_renderer.render(note=note, rescale=note_rescale)
                        harp_render = self.trans_paste(harp_render, note_render, (round(xn), round(yn)))


        return harp_render


    def render_harp(self, instrument, rescale=1.0, max_size=None):


        if self.gamepad is None:
            harp_render = self._render_mobile_harp_(instrument, rescale)
        else:
            harp_render = self._render_gamepad_harp_(instrument, rescale)

        # Rescaling
        if max_size is not None:
            rescale =  min(rescale,max_size[0]/harp_render.size[0])
            rescale =  min(rescale,max_size[1]/harp_render.size[1])


        if rescale != 1 and rescale > 0:
            harp_render = harp_render.resize((round(harp_render.size[0] * rescale), round(harp_render.size[1] * rescale)),
                                             resample=Image.LANCZOS)

        return harp_render
                














