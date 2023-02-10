import io
import textwrap
from . import song_renderer
from skymusic import instruments
from skymusic.renderers.instrument_renderers.png_ir import PngInstrumentRenderer
from skymusic.resources import Resources
from skymusic.modes import GamePlatform

try:
    from PIL import Image, ImageDraw, ImageFont

    no_PIL_module = False
except (ImportError, ModuleNotFoundError):
    no_PIL_module = True



class PngSongRenderer(song_renderer.SongRenderer):

    def __init__(self, locale=None, aspect_ratio=16/9.0, gamepad=None, theme=Resources.get_default_theme()):
        
        super().__init__(locale)
        platform = gamepad.platform if gamepad else GamePlatform.get_default()
        self.gamepad = gamepad
        
        if Resources.BYPASS_GAMEPAD_PNG:
            self.gamepad = None
            platform = GamePlatform.get_default()
        
        self.harp_AspectRatio = 1.455
        self.harp_relspacings = (0.13, 0.1)  # Fraction of the harp width that will be allocated to the spacing between harps

        self.aspect_ratio = aspect_ratio
        self.maxIconsPerLine = round(10*aspect_ratio/(16/9.0))
        self.maxFiles = Resources.MAX_NUM_FILES

        if not no_PIL_module:
            Resources.load_theme(theme, platform)
            
            self.png_margins = (13, 7)
            self.png_size = (round(self.aspect_ratio*750 * 2), 750 * 2)  # must be an integer tuple
            self.png_line_width = int(self.png_size[0] - 2*self.png_margins[0])  # self.png_lyric_relheight = instruments.Voice().lyric_relheight
            
            self.png_lyric_size = None
            self.png_dpi = (96 * 2, 96 * 2)
            self.png_compress = Resources.PNG_SETTINGS['png_compress']
            self.font_color = Resources.PNG_SETTINGS['font_color']
            self.png_color = Resources.PNG_SETTINGS['png_color']
            self.png_font_size = Resources.PNG_SETTINGS['png_font_size']
            self.png_h1_font_size = Resources.PNG_SETTINGS['png_h1_font_size']
            self.png_h2_font_size = Resources.PNG_SETTINGS['png_h2_font_size']
            self.png_font_path = Resources.PNG_SETTINGS['font_path']
            
            try:
                self.h1_font = ImageFont.truetype(self.png_font_path, self.png_h1_font_size)
                self.h2_font = ImageFont.truetype(self.png_font_path, self.png_h2_font_size)
                self.text_font = ImageFont.truetype(self.png_font_path, self.png_font_size)
            except OSError:
                self.h1_font = ImageFont.load_default()
                self.h2_font = ImageFont.load_default()
                self.text_font = ImageFont.load_default()
                
            self.switch_harp('harp')            
            

    def switch_harp(self, harp_type):
        
            png_instrument_renderer = PngInstrumentRenderer(self.locale, harp_type=harp_type, gamepad=self.gamepad)            
            self.png_harp_size0 = png_instrument_renderer.get_png_harp_size()  # A tuple
            self.png_harp_spacings0 = (int(self.harp_relspacings[0] * self.png_harp_size0[0]),
                                       int(self.harp_relspacings[1] * self.png_harp_size0[1]))
            self.png_harp_size = None
            self.png_harp_spacings = None
            self.png_lyric_size0 = (self.png_harp_size0[0], png_instrument_renderer.get_lyric_height())        


    def set_png_harp_size(self, max_instruments_per_line):
        """Shrinks the Harp image, so that the longest line fits up to max_instruments_per_line instruments"""
        if self.png_harp_size is None or self.png_harp_spacings is None:
            Nmax = max(1, min(self.maxIconsPerLine, max_instruments_per_line))
            new_harp_width = min(self.png_harp_size0[0],
                                 (self.png_size[0] - self.png_margins[0]) / (Nmax * (1.0 + self.harp_relspacings[0])))
            self.png_harp_size = (new_harp_width, new_harp_width / self.harp_AspectRatio)
            self.png_harp_spacings = (
                self.harp_relspacings[0] * self.png_harp_size[0], self.harp_relspacings[1] * self.png_harp_size[1])
            self.png_lyric_size = (self.png_harp_size[0], (self.png_harp_size[1] / self.png_harp_size0[1]))

    def set_png_voice_size(self):
        self.png_lyric_size = (
            self.png_lyric_size0[0] * self.get_png_harp_rescale(),
            self.png_lyric_size0[1] * self.get_png_harp_rescale())

    def get_png_harp_rescale(self):
        """Gets the rescale factor to from the original .png Harp image"""
        if self.png_harp_size[0] is not None:
            return 1.0 * self.png_harp_size[0] / self.png_harp_size0[0]
        else:
            return 1.0

    def get_png_text_height(self, fnt):
        """Calculates the text height in PNG for a standard text depending on the input font size"""
        return fnt.getsize('HQfgjyp')[1]

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

    def write_header(self, song_render, filenum, song, x_in_png, y_in_png):
    
        meta = song.get_meta()
        harp_rescale = self.get_png_harp_rescale()
        line_width = self.png_line_width
    
        if filenum == 0:

            title = meta['title'][1]
            fnt = self.h1_font
            title, numlines = self.wrap_text(title, fnt.getsize(title)[0], int(line_width/harp_rescale))               
            h = self.get_png_text_height(fnt)
            title_header = Image.new('RGBA', (int(line_width/harp_rescale), int(h*numlines)))
            draw = ImageDraw.Draw(title_header)
            draw.text((0, 0), title, font=fnt, fill=self.font_color)
            if harp_rescale != 1:
                title_header = title_header.resize(
                    (int(title_header.size[0] * harp_rescale), int(title_header.size[1] * harp_rescale)),
                    resample=Image.LANCZOS)
            song_render = self.trans_paste(song_render, title_header, (int(x_in_png), int(y_in_png)))
            y_in_png += (h+1) * numlines * harp_rescale

            for k in meta:
                if k != 'title':
                    meta_text = meta[k][0] + ' ' + meta[k][1]
                    #fnt = ImageFont.truetype(self.png_font_path, self.)
                    fnt = self.text_font
                    meta_text, numlines = self.wrap_text(meta_text, fnt.getsize(meta_text)[0], int(line_width/harp_rescale))
                    h = self.get_png_text_height(fnt)
                    header = Image.new('RGBA', (int(line_width/harp_rescale), int(h*numlines)))
                    draw = ImageDraw.Draw(header)
                    draw.text((0, 0), meta_text, font=fnt, fill=self.font_color)
                    if harp_rescale != 1:
                        header = header.resize((int(header.size[0] * harp_rescale), int(header.size[1] * harp_rescale)),
                                               resample=Image.LANCZOS)
                    song_render = self.trans_paste(song_render, header, (int(x_in_png), int(y_in_png)))
                    y_in_png += (h+1) * numlines * harp_rescale
            
            y_in_png += h * harp_rescale
            
        else:
            #fnt = ImageFont.truetype(self.png_font_path, self.png_font_size)
            fnt = self.text_font
            h = self.get_png_text_height(fnt)
            title_header = Image.new('RGBA', (int(line_width), int(h)))
            draw = ImageDraw.Draw(title_header)
            draw.text((0, 0), f"{meta['title'][1]} (page {filenum+1 :d})", font=fnt, fill=self.font_color)
            if harp_rescale != 1:
                title_header = title_header.resize(
                    (int(title_header.size[0] * harp_rescale), int(title_header.size[1] * harp_rescale)),
                    resample=Image.LANCZOS)
            song_render = self.trans_paste(song_render, title_header, (int(x_in_png), int(y_in_png)))
            y_in_png += h * harp_rescale + self.png_harp_spacings[1]    
    
        return (song_render, x_in_png, y_in_png)
    

    def write_buffers(self, song, start_row=0, start_col=0, buffer_list=None):
        
        if buffer_list is None:
            buffer_list = []
        global no_PIL_module

        if no_PIL_module:
            print("\n***WARNING: PNG was not rendered because PIL module was not found. ***")
            return None
     
        filenum = len(buffer_list)
        if len(buffer_list) >= self.maxFiles:
            print(f"\n***WARNING: Your song is too long. Stopping at {self.maxFiles} files.")
            return buffer_list
        
        harp_type = song.get_harp_type()
        instrument_renderer = PngInstrumentRenderer(locale=self.locale, harp_type=harp_type, gamepad=self.gamepad)
        self.switch_harp(harp_type)
        
        # Determines png size as a function of the numer of icons per line
        self.set_png_harp_size(song.get_max_instruments_per_line())
        self.set_png_voice_size()
        
        text_font_height = self.get_png_text_height(self.text_font)
        h1_font_height = self.get_png_text_height(self.h1_font)
        h2_font_height = self.get_png_text_height(self.h2_font)
        
        harp_rescale = self.get_png_harp_rescale()
        song_render = Image.new('RGBA', self.png_size, self.png_color)

        # Horizontal ruler drawing, to be used several times later
        rulerH = max(1,int(4*harp_rescale))
        hr_line = Image.new('RGBA', (int(self.png_line_width), 3*rulerH))
        draw = ImageDraw.Draw(hr_line)
        draw = draw.line(
                        [(0, int(hr_line.size[1]/2)), (self.png_line_width, int(hr_line.size[1]/2))],
                        fill=(150, 150, 150),
                        width=rulerH)

        x_in_png = int(self.png_margins[0])
        y_in_png = int(self.png_margins[0])
        
        (song_render, x_in_png, y_in_png) = self.write_header(song_render, filenum, song, x_in_png, y_in_png)

        ysong = y_in_png
        instrument_index = 0
        num_lines = song.get_num_lines()
        end_row = num_lines
        end_col = 0
        ncols = self.maxIconsPerLine
        page_break = False
        
        # Creating a new song image, located at x_in_song, yline_in_song
        xline_in_song = x_in_png
        yline_in_song = ysong
        prev_line = ''
        for row in range(start_row, end_row):

            line = song.get_line(row)
            if row > start_row:
                start_col = 0            
            linetype = line[0].get_type().lower().strip()
            line_width = int(self.png_line_width)
            ncols = len(line) - start_col
            end_col = len(line)
            
            # Instrument(s) line
            if linetype in instruments.TEXT:
                line_height = int(self.png_lyric_size[1])
            elif linetype == 'ruler':
                line_height = int(self.png_lyric_size[1])
            elif linetype == 'layer':
                line_height = int(self.png_lyric_size[1]) 
            elif linetype in instruments.HARPS:
                line_height = int(self.png_harp_size[1])               

                # Forced dividing line after each line of harps
                if prev_line not in ('ruler', 'layer'):
                    yline_in_song += self.png_harp_spacings[1] / 4.0
                    song_render.paste(hr_line, (int(xline_in_song), int(yline_in_song)))
                    yline_in_song += hr_line.size[1] + self.png_harp_spacings[1] / 2.0
            else:
                raise TypeError("Unkown linetype type: "+linetype)

            # More line height in case ruler or layer has text
            if linetype in ('ruler', 'layer'):
                if line[0].get_text():
                    if line[0].get_emphasis().lower() == 'h1':
                        line_height += int(h1_font_height)
                    elif line[0].get_emphasis().lower() == 'h2':
                        line_height += int(h2_font_height)
                    else:
                        line_height += int(text_font_height) 

            # Line image
            line_render = Image.new('RGBA', (line_width, line_height), self.png_color)

            # Pasting instrument images, starting at x=0 (in line) and y=0 (in line)           
            sub_line = 0
            x = 0
            y = 0
            for col in range(start_col, end_col):

                instrument = song.get_instrument(row, col)
                instrument.set_index(instrument_index)
                
                # Creating a new line if max number is exceeded
                if x + self.png_harp_size[0] + self.png_harp_spacings[0] / 2.0 > line_width:
                    x = 0
                    song_render = self.trans_paste(song_render, line_render, (int(xline_in_song), int(yline_in_song)))
                    yline_in_song += line_render.size[1] + self.png_harp_spacings[1] / 2.0
                    if linetype in instruments.HARPS: yline_in_song += self.png_harp_spacings[1] / 2.0

                    sub_line += 1

                    # New line
                    line_render = Image.new('RGBA', (line_width, line_height), self.png_color)
                    
                #NEW
                ypredict = yline_in_song +  self.png_harp_spacings[1]
                
                if linetype in instruments.TEXT:
                    ypredict += self.png_lyric_size[1]
                elif linetype == 'ruler':
                    ypredict += hr_line.size[1]
                elif linetype == 'layer':
                    ypredict += hr_line.size[1]
                elif linetype in instruments.HARPS:
                    ypredict += self.png_harp_size[1]
                else:
                    raise TypeError("Unkown linetype type: "+linetype)
    
                if ypredict > (self.png_size[1] - self.png_margins[1]):
                    page_break = True
                    end_col = col
                    break

                # INSTRUMENT RENDER
                instrument_render = instrument_renderer.render(instrument, harp_rescale, max_size=(line_width,line_height))
                # should add a special case for horizontal ruler
                line_render = self.trans_paste(line_render, instrument_render, (int(x), int(y)))

                x += max(self.png_harp_size[0], instrument_render.size[0])

                # REPEAT
                if instrument.get_repeat() > 1:
                    repeat_im = instrument_renderer.get_repeat_png(instrument, self.png_harp_spacings[0], harp_rescale)
                    line_render = self.trans_paste(line_render, repeat_im,
                                              (int(x), int(y + self.png_harp_size[1] - repeat_im.size[1])))
                    x += max(repeat_im.size[0], self.png_harp_spacings[0])
                else:
                    x += self.png_harp_spacings[0]

                instrument_index += 1

            #end loop on cols: pasting line
            song_render = self.trans_paste(song_render, line_render,(int(xline_in_song), int(yline_in_song)))
            yline_in_song += line_render.size[1] + self.png_harp_spacings[1] / 2.0
            if linetype in instruments.HARPS:
                yline_in_song += self.png_harp_spacings[1] / 2.0

            prev_line = linetype
            if page_break:
                end_row = row
                break

        #End loop on rows
        song_buffer = io.BytesIO()
        song_render.save(song_buffer, format='PNG', dpi=self.png_dpi, compress_level=self.png_compress)

        song_buffer.seek(0)
        buffer_list.append(song_buffer)


        # Open new file
        if end_row < song.get_num_lines() or 0 < end_col < ncols:
            buffer_list = self.write_buffers(song, end_row, end_col, buffer_list)

        return buffer_list
