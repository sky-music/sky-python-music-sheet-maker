import io, textwrap
from . import song_renderer
#from skymusic import instruments
from skymusic.renderers.instrument_renderers.png_ir import PngInstrumentRenderer
from skymusic.resources import Resources
from skymusic.modes import GamePlatform
from skymusic.sheetlayout import Ruler

try:
    from PIL import Image, ImageDraw, ImageFont
    no_PIL_module = False
except ModuleNotFoundError:
    no_PIL_module = True
except ImportError as err:
    no_PIL_module = True
    print(err)


class PngSongRenderer(song_renderer.SongRenderer):

    def __init__(self, locale=None, aspect_ratio=16/9.0, gamepad=None, theme=Resources.get_default_theme()):
        
        super().__init__(locale)
        self.platform_name = gamepad.platform.get_name() if gamepad else GamePlatform.get_default().get_name()
        self.gamepad = gamepad
        self.aspect_ratio = aspect_ratio # Aspect ratio of the song sheet
        self.maxFiles = Resources.MAX_NUM_FILES 
        
        Resources.load_theme(theme, self.platform_name)
        
        self.sheet_margins = (13, 7)
        self.sheet_size = (round(self.aspect_ratio*750 * 2), 750 * 2)  # must be an integer tuple
        self.line_width = round(self.sheet_size[0] - 2*self.sheet_margins[0])
                    
        self.png_dpi = Resources.PNG_SETTINGS['png_dpi']
        self.png_compress = Resources.PNG_SETTINGS['png_compress']
        self.font_color = Resources.PNG_SETTINGS['font_color']
        self.dimmed_font_color = Resources.PNG_SETTINGS['dimmed_font_color']
        self.harp_color = Resources.PNG_SETTINGS['harp_color']
        self.font_size = Resources.PNG_SETTINGS['font_size']
        self.h1_font_size = Resources.PNG_SETTINGS['h1_font_size']
        self.h2_font_size = Resources.PNG_SETTINGS['h2_font_size']
        self.font_path = Resources.PNG_SETTINGS['font_path']
        self.text_bkg = Resources.PNG_SETTINGS['text_bkg']  # Transparent white
      
        if not no_PIL_module:    
            try:
                self.h1_font = ImageFont.truetype(self.font_path, self.h1_font_size)
                self.h2_font = ImageFont.truetype(self.font_path, self.h2_font_size)
                self.text_font = ImageFont.truetype(self.font_path, self.font_size)
                self.dimmed_text_font = ImageFont.truetype(self.font_path, self.font_size)
            except OSError:
                self.h1_font = ImageFont.load_default()
                self.h2_font = ImageFont.load_default()
                self.text_font = ImageFont.load_default()
                self.dimmed_text_font = ImageFont.load_default()


        # INSTRUMENT RESIZING
        self._max_harps_line_ = round(Resources.PNG_SETTINGS['max_harps_line']*aspect_ratio/(16/9.0))
        self._max_gp_notes_line_ = round(Resources.PNG_SETTINGS['max_gp_notes_line']*aspect_ratio/(16/9.0))

        self._harp_aspect_ratio_ = Resources.PNG_SETTINGS['harp_aspect_ratio']
        self._harp_rel_spacings_ = Resources.PNG_SETTINGS['harp_rel_spacings']  # Fraction of the harp width that will be allocated to the spacing between harps
                
        self._harp_size_ = tuple()
        self._harp_spacings_ = tuple()
        self._voice_height_ = 0
        self._harp_rescale_ = 1
        self._harp_max_upscale_ = 2
        self._gp_max_upscale_ = 1
        
        if not no_PIL_module:
            self.switch_harp('harp') #sets _harp_size0_, _harp_spacings0_, _voice_size0_
        
        
        self._gp_note_size_ = None
        self._gamepad_spacings_ = tuple()
        self._gamepad_rescale_ = 1
        self._nontonal_spacings_ = tuple()   
        
        #self.set_harp_rescale #Not mandatory: will be called depending on player's Song

        if not no_PIL_module:
            self.set_nontonal_spacings()
            self.set_gamepad_spacings()
            self.set_gamepad_rescale(self._max_gp_notes_line_) #Called once and for all   


    def switch_harp(self, harp_type):
        
        instrument_renderer = PngInstrumentRenderer(self.locale, harp_type=harp_type, platform_name=self.platform_name, gamepad=self.gamepad)            
        self._harp_size_ = instrument_renderer.get_harp_size()  # A tuple
        self._harp_spacings_ = (round(self._harp_rel_spacings_[0] * self._harp_size_[0]),
                                   round(self._harp_rel_spacings_[1] * self._harp_size_[1]))
        self._voice_height_ = instrument_renderer.get_text_size()[1]     
        

    def set_harp_rescale(self, harps_line=None, harp='harp'):
        '''Returns harp size fitting given harps_per_line.'''
        if harps_line:
            if not self._harp_size_: self.switch_harp(harp)
            Nmax = max(1, min(self._max_harps_line_, harps_line))
            harp_width = min(self._harp_size_[0],
                                 (self.sheet_size[0] - self.sheet_margins[0]) / (Nmax * (1.0 + self._harp_rel_spacings_[0])))
            #harp_size = (harp_width, harp_width / self._harp_aspect_ratio_)     
            self._harp_rescale_ = min(self._harp_max_upscale_,max(0.1, harp_width/self._harp_size_[0])) #safety bounds
        
        return self._harp_rescale_

    def set_gamepad_rescale(self, gp_notes_line=None):

        if gp_notes_line: 
            if not self._gp_note_size_:
                self._gp_note_size_ = PngInstrumentRenderer(locale=self.locale, platform_name=self.platform_name, gamepad=self.gamepad).get_gp_note_size()
        
            Nmax = max(1, min(self._max_gp_notes_line_, gp_notes_line))
            note_width_with_margins = (self.sheet_size[0] - self.sheet_margins[0]) / Nmax
            self._gamepad_rescale_ = min(self._gp_max_upscale_,max(0.1, note_width_with_margins/(self._gp_note_size_[0]+self._gamepad_spacings_[0]))) #safety bounds
        
        return self._gamepad_rescale_

    def get_instr_rescale(self):
        """Gets the rescale factor depending on gamepad"""
        if self.gamepad is None:       
            return self._harp_rescale_
        else:
            return self._gamepad_rescale_


    def get_harp_size(self, rescale=1):
        
        return (round(self._harp_size_[0]*rescale), round(self._harp_size_[1]*rescale))
    
    def get_harp_spacings(self, rescale=1):
            
        return (round(self._harp_spacings_[0]*rescale), round(self._harp_spacings_[1]*rescale))
        #self.harp_spacings = (
        #    self._harp_rel_spacings_[0] * self.harp_size[0], self._harp_rel_spacings_[1] * self.harp_size[1])

    def get_voice_height(self, rescale=1):
            
        return round(self._voice_height_*rescale)
        #self.voice_size = (self.harp_size[0], (self.harp_size[1] / self.harp_size0[1]))
            
        
    def set_gamepad_spacings(self):
       
       if not self._gamepad_spacings_:
           instrument_renderer = PngInstrumentRenderer(locale=self.locale, harp_type='harp', platform_name=self.platform_name, gamepad=self.gamepad)
           gaps = instrument_renderer.get_gamepad_gaps()
           self._gamepad_spacings_ = (gaps['note-gapH'], gaps['line-gapV'])
       return self._gamepad_spacings_

    def get_gamepad_spacings(self, rescale=1):
        
        return (round(self._gamepad_spacings_[0]*rescale), round(self._gamepad_spacings_[1]*rescale))

    def get_instr_spacings(self, rescale=1):
        if self.gamepad is None:
            return self.get_harp_spacings(rescale)
        else:
            return self.get_gamepad_spacings(rescale)
    
    def set_nontonal_spacings(self):
        
        if not self.gamepad:
            self._nontonal_spacings_ = (self._harp_size_[0], self._harp_size_[1]/4.0)
        else:
            if not self._gp_note_size_:
                self._gp_note_size_ = PngInstrumentRenderer(locale=self.locale, platform_name=self.platform_name, gamepad=self.gamepad).get_gp_note_size()
            self._nontonal_spacings_ = (self._gp_note_size_[0], self._gp_note_size_[1]/3.0)
            
        return self._nontonal_spacings_

    def get_nontonal_spacings(self, rescale=1):
        
        return (round(self._nontonal_spacings_[0]*rescale), round(self._nontonal_spacings_[1]*rescale))


    def get_text_height(self, fnt, rescale=1):
        """Calculates the text height in PNG for a standard text depending on the input font size"""
        return round(fnt.getsize('HQfgjyp')[1]*rescale)

                

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

    def wrap_text(self, text, width, target_width):
        
        if width < target_width:
            return text, 1
        else:
            maxlen = int((target_width/width)*len(text))
            splitted = textwrap.wrap(text, width=maxlen, break_long_words=True)
            return "\n".join(splitted), len(splitted)


    def get_num_png(self, num, fit_size=None, rescale=1):
        
        num_str = "%d" % int(num)
        w,h = self.text_font.getsize(num_str)
        num_im = Image.new('RGBA', (200*w, h), color=self.text_bkg)
        draw = ImageDraw.Draw(num_im)
        draw.text((0, num_im.size[1] - 1.05 * h), num_str, font=self.dimmed_text_font, fill=self.dimmed_font_color)
        
        if fit_size: rescale = rescale * min(min(1, fit_size[0] / w), fit_size[1] / h)

        if rescale != 1 and rescale > 0:
            num_im = num_im.resize((round(num_im.size[0] * rescale), round(num_im.size[1] * rescale)), resample=Image.LANCZOS)
        return num_im


    def write_header(self, song_render, filenum, song, x_in_png, y_in_png):
    
        #harp_type = song.get_harp_type()
        #self.switch_harp(harp_type)
        text_rescale = 1 #self.get_text_rescale() #Hard-coded value
        
        meta = song.get_meta()
        line_width = self.line_width
    
        if filenum == 0:

            title = meta['title'][1]
            fnt = self.h1_font
            title, numlines = self.wrap_text(title, fnt.getsize(title)[0], round(line_width/text_rescale))               
            h = self.get_text_height(fnt)
            title_header = Image.new('RGBA', (round(line_width/text_rescale), round(h*numlines)))
            draw = ImageDraw.Draw(title_header)
            draw.text((0, 0), title, font=fnt, fill=self.font_color)
            if text_rescale != 1 and text_rescale > 0:
                title_header = title_header.resize(
                    (int(title_header.size[0] * text_rescale), int(title_header.size[1] * text_rescale)),
                    resample=Image.LANCZOS)
            song_render = self.trans_paste(song_render, title_header, (int(x_in_png), int(y_in_png)))
            y_in_png += (h+1) * numlines * text_rescale

            for k in meta:
                if k != 'title':
                    meta_text = meta[k][0] + ' ' + meta[k][1]
                    #fnt = ImageFont.truetype(self.font_path, self.)
                    fnt = self.text_font
                    meta_text, numlines = self.wrap_text(meta_text, fnt.getsize(meta_text)[0], int(line_width/text_rescale))
                    h = self.get_text_height(fnt)
                    header = Image.new('RGBA', (int(line_width/text_rescale), int(h*numlines)))
                    draw = ImageDraw.Draw(header)
                    draw.text((0, 0), meta_text, font=fnt, fill=self.font_color)
                    if text_rescale != 1 and text_rescale > 0:
                        header = header.resize((int(header.size[0] * text_rescale), int(header.size[1] * text_rescale)),
                                               resample=Image.LANCZOS)
                    song_render = self.trans_paste(song_render, header, (int(x_in_png), int(y_in_png)))
                    y_in_png += (h+1) * numlines * text_rescale
            
            y_in_png += h * text_rescale
            
        else:
            #fnt = ImageFont.truetype(self.font_path, self.font_size)
            fnt = self.text_font
            h = self.get_text_height(fnt)
            title_header = Image.new('RGBA', (int(line_width), int(h)))
            draw = ImageDraw.Draw(title_header)
            draw.text((0, 0), f"{meta['title'][1]} (page {filenum+1 :d})", font=fnt, fill=self.font_color)
            if text_rescale != 1 and text_rescale > 0:
                title_header = title_header.resize(
                    (int(title_header.size[0] * text_rescale), int(title_header.size[1] * text_rescale)),
                    resample=Image.LANCZOS)
            song_render = self.trans_paste(song_render, title_header, (int(x_in_png), int(y_in_png)))
            y_in_png += h * text_rescale + self.get_nontonal_spacings(text_rescale)[1]*2
    
        return (song_render, x_in_png, y_in_png)
    

    def write_buffers(self, song, start_row=0, start_col=0, tonal_row=0, buffer_list=None):
        
        if buffer_list is None:
            buffer_list = []
        global no_PIL_module

        if no_PIL_module:
            print("\n***WARNING: PNG was not rendered because PIL module was not found, or its import generated an error. ***")
            return None
     
        filenum = len(buffer_list)
        if len(buffer_list) >= self.maxFiles:
            print(f"\n***WARNING: Your song is too long. Stopping at {self.maxFiles} files.")
            return buffer_list
        
        harp_type = song.get_harp_type()
        self.switch_harp(harp_type)
        instrument_renderer = PngInstrumentRenderer(locale=self.locale, harp_type=harp_type, platform_name=self.platform_name, gamepad=self.gamepad)
        
        # Determines png size as a function of the numer of icons per line
        if self.gamepad is None:
            instr_rescale = self.set_harp_rescale(song.get_max_instruments_per_line())
        else:
            instr_rescale = self.set_gamepad_rescale()
        
        text_rescale = instr_rescale**0.6  # A trick to avoid reducing the text too much
        
        voice_height = self.get_voice_height(text_rescale)
        
        instr_spacings = self.get_instr_spacings(instr_rescale)
        nontonal_spacings = self.get_nontonal_spacings(instr_rescale)
        
        text_font_height = self.get_text_height(self.text_font,text_rescale)
        h1_font_height = self.get_text_height(self.h1_font,text_rescale)
        h2_font_height = self.get_text_height(self.h2_font,text_rescale)
        
        song_render = Image.new('RGBA', self.sheet_size, self.harp_color)

        # Horizontal ruler drawing, to be used several times later
        rulerH = max(1,round(4*instr_rescale))
        hr_line = instrument_renderer.render_ruler(ruler=Ruler(code='__'), max_size= (self.line_width, round(3*rulerH/2)))

        x_in_png = round(self.sheet_margins[0])
        y_in_png = round(self.sheet_margins[0])
        
        (song_render, x_in_png, y_in_png) = self.write_header(song_render, filenum, song, x_in_png, y_in_png)

        ysong = y_in_png
        instrument_index = 0
        num_lines = song.get_num_lines()
        end_row = num_lines
        end_col = 0
        ncols = self._max_harps_line_
        page_break = False
        
        # Creating a new song image, located at x_in_song, yline_in_song
        xline_in_song = x_in_png
        yline_in_song = ysong
        prev_line0 = None
        
        for row in range(start_row, end_row):

            line = song.get_line(row)
            if row > start_row:
                start_col = 0 
            line0 = line[0]
            
            line_width = round(self.line_width)
            ncols = len(line) - start_col # remaining number of song instrument to render in the line
            end_col = len(line) #Last instrument number+1 in the line
            
            # Adds big spacing only between 2 instruments
            if prev_line0:
                if line0.get_is_tonal() and prev_line0.get_is_tonal():
                    yline_in_song += instr_spacings[1]/2
                elif line0.get_is_textual() and prev_line0.get_is_tonal():
                    yline_in_song += nontonal_spacings[1]/4
                else:
                    yline_in_song += nontonal_spacings[1]/2
            
            # Instrument(s) line
            if line0.get_is_textual():
                line_height = voice_height
            elif line0.get_is_textual():
                line_height = voice_height
            elif line0.get_is_decorative():
                line_height = voice_height
            elif line0.get_is_tonal(): #Harp or gamepad
                if self.gamepad is None:
                    line_height = self.get_harp_size(instr_rescale)[1]
                else:
                    # Special calculation for gamepad
                    gamepad_instr_sizes = [instrument_renderer.get_gamepad_size(instr) for instr in line]
                    gapH = instr_spacings[0]
                    lineW_predict = 0
                    line_height = 0
                    for instr_size in gamepad_instr_sizes:
                        lineW_predict += (instr_size[0] + gapH)*instr_rescale
                        if lineW_predict > line_width: break
                        line_height = max(line_height, instr_size[1])
                
                # Forced dividing line after each line of tonal instruments
                prev_linetype = '' if not prev_line0 else prev_line0.get_type()
                if prev_linetype not in ('ruler', 'layer'):
                    #yline_in_song += nontonal_spacings[1] / 2.0
                    song_render.paste(hr_line, (round(xline_in_song), round(yline_in_song)))
                    
                    yline_in_song += hr_line.size[1] + nontonal_spacings[1]
            else:
                raise TypeError("Unknown linetype type: "+line0.get_type())

            # More line height in case ruler or layer has text
            if line0.get_is_decorative() and line0.get_is_textual():
                if line0.get_text():
                    if line0.get_emphasis().lower() == 'h1':
                        line_height += h1_font_height
                    elif line0.get_emphasis().lower() == 'h2':
                        line_height += h2_font_height
                    else:
                        line_height += text_font_height

            # Line image
            line_render = Image.new('RGBA', (line_width, line_height), self.harp_color)
            
            # Pasting instrument images, starting at x=0 (in line) and y=0 (in line)           
            sub_line = 0
            x = 0
            y = 0
            
            for col in range(start_col, end_col):

                instrument = song.get_instrument(row, col)
                instrument.set_index(instrument_index)
                
                # Creating a new line if max number is exceeded
                x_predict = x + instr_spacings[0] / 2.0 + self.dimmed_text_font.getsize('99')[0]
                if self.gamepad is None or (not instrument.get_is_tonal()):
                    last_instr_size = self.get_harp_size(instr_rescale)
                    #TODO: predict text length instead of using generic length
                else:
                    last_instr_size = instrument_renderer.get_gamepad_size(instrument, instr_rescale)
                x_predict += last_instr_size[0]
                
                if x_predict > line_width:
                    x = 0
                                        
                    song_render = self.trans_paste(song_render, line_render, (round(xline_in_song), round(yline_in_song)))
                    
                    yline_in_song += line_render.size[1]
                    
                    if line0.get_is_tonal():
                        yline_in_song += instr_spacings[1]
                    else:
                        yline_in_song += nontonal_spacings[1]

                    sub_line += 1

                    # New line
                    line_render = Image.new('RGBA', (line_width, line_height), self.harp_color)
                
                #Predict V space taken by instrument renders, to anticipate line break
                ypredict = yline_in_song
                
                # Spacing prediction
                if line0.get_is_tonal():
                    ypredict += instr_spacings[1]/2
                else:
                    ypredict += nontonal_spacings[1]/2
                
                if line0.get_is_textual():
                    ypredict += voice_height
                elif line0.get_is_decorative():
                    ypredict += hr_line.size[1]
                elif line0.get_is_tonal():
                    ypredict += self.get_harp_size(instr_rescale)[1]
                else:
                    raise TypeError("Unkown linetype type: "+line0.get_type())
    
                if ypredict > (self.sheet_size[1] - self.sheet_margins[1]):
                    page_break = True
                    end_col = col
                    break

                # == INSTRUMENT RENDER ==
                render_rescale = instr_rescale if line0.get_is_tonal() else text_rescale
                instrument_render = instrument_renderer.render(instrument, render_rescale, max_size=(line_width,line_height))
                # should add a special case for horizontal ruler
                
                line_render = self.trans_paste(line_render, instrument_render, (round(x), round(y)))

                if self.gamepad is None:
                    x += max(self.get_harp_size(instr_rescale)[0], instrument_render.size[0])
                else:
                    x += instrument_render.size[0]

                # REPEAT
                if instrument.get_repeat() > 1:
                    repeat_im = instrument_renderer.get_repeat_png(instrument, (instr_spacings[0]*3, instrument_render.size[1]), text_rescale)
                    
                    line_render = self.trans_paste(line_render, repeat_im,
                                              (round(x), round(y + instrument_render.size[1] - repeat_im.size[1])))
                    
                    # Tighter layout for 3x5 skygrid
                    x += max(repeat_im.size[0], instr_spacings[0])
                    # Relaxed layout for gamepad
                    if self.gamepad and not instrument.get_is_silent(): x += instr_spacings[0]
                else:
                    x += instr_spacings[0]

                instrument_index += 1
            
                if col == end_col-1:
                    if line0.get_is_tonal(): tonal_row += 1
    
                    # Adds line number to line_render
                    if num_lines > 5 and line0.get_is_tonal():
                        num_im = self.get_num_png(tonal_row, (3*instr_spacings[0],instrument_render.size[1]), instr_rescale)
                        x += instr_spacings[0]
                        line_render = self.trans_paste(line_render, num_im,
                                              (round(x), round(y + instrument_render.size[1] - num_im.size[1])))
                
            #end loop on cols: pasting line
                        
            song_render = self.trans_paste(song_render, line_render,(round(xline_in_song), round(yline_in_song)))
            yline_in_song += line_render.size[1]
            
            # Actual space taken
            if line0.get_is_tonal():
                yline_in_song += instr_spacings[1]/2
            else:
                yline_in_song += nontonal_spacings[1]/2
                
            prev_line0 = line0
            if page_break:
                end_row = row
                break

        #End loop on Song rows
        song_buffer = io.BytesIO()
        song_render.save(song_buffer, format='PNG', dpi=self.png_dpi, compress_level=self.png_compress)

        song_buffer.seek(0)
        buffer_list.append(song_buffer)


        # Open new file
        if end_row < song.get_num_lines() or 0 < end_col < ncols:
            buffer_list = self.write_buffers(song, end_row, end_col, tonal_row, buffer_list)

        return buffer_list























