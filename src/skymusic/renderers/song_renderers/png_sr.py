import io
import textwrap
from . import song_renderer
from src.skymusic.renderers.instrument_renderers.png_ir import PngInstrumentRenderer
from src.skymusic.resources import Resources


try:
    from PIL import Image, ImageDraw, ImageFont

    no_PIL_module = False
except (ImportError, ModuleNotFoundError):
    no_PIL_module = True



class PngSongRenderer(song_renderer.SongRenderer):

    def __init__(self, locale=None, aspect_ratio=16/9.0, theme=list(Resources.THEMES)[0]):
        
        super().__init__(locale)
        
        self.harp_AspectRatio = 1.455
        self.harp_relspacings = (0.13, 0.1)  # Fraction of the harp width that will be allocated to the spacing between harps

        self.aspect_ratio = aspect_ratio
        self.maxIconsPerLine = round(10*aspect_ratio/(16/9.0))
        self.maxFiles = Resources.MAX_NUM_FILES

        if not no_PIL_module:
            Resources.load_theme(theme)
            png_instrument_renderer = PngInstrumentRenderer(self.locale)
            self.png_size = (round(self.aspect_ratio*750 * 2), 750 * 2)  # must be an integer tuple
            self.png_margins = (13, 7)
            self.png_harp_size0 = png_instrument_renderer.get_png_chord_size()  # A tuple
            self.png_harp_spacings0 = (int(self.harp_relspacings[0] * self.png_harp_size0[0]),
                                       int(self.harp_relspacings[1] * self.png_harp_size0[1]))
            self.png_harp_size = None
            self.png_harp_spacings = None
            self.png_line_width = int(self.png_size[0] - 2*self.png_margins[0])  # self.png_lyric_relheight = instruments.Voice().lyric_relheight
            self.png_lyric_size0 = (self.png_harp_size0[0], png_instrument_renderer.get_lyric_height())
            self.png_lyric_size = None
            self.png_dpi = (96 * 2, 96 * 2)
            self.png_compress = Resources.png_compress
            self.font_color = Resources.font_color
            self.png_color = Resources.png_color
            self.png_font_size = Resources.png_font_size
            self.png_title_font_size = Resources.png_title_font_size
            self.png_font_path = Resources.font_path


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
    
        if filenum == 0:

            title = meta['title'][1]
            fnt = ImageFont.truetype(self.png_font_path, self.png_title_font_size)
            title, numlines = self.wrap_text(title, fnt.getsize(title)[0], int(self.png_line_width/harp_rescale))               
            h = self.get_png_text_height(fnt)
            title_header = Image.new('RGBA', (int(self.png_line_width/harp_rescale), int(h*numlines)))
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
                    fnt = ImageFont.truetype(self.png_font_path, self.png_font_size)
                    meta_text, numlines = self.wrap_text(meta_text, fnt.getsize(meta_text)[0], int(self.png_line_width/harp_rescale))
                    h = self.get_png_text_height(fnt)
                    header = Image.new('RGBA', (int(self.png_line_width/harp_rescale), int(h*numlines)))
                    draw = ImageDraw.Draw(header)
                    draw.text((0, 0), meta_text, font=fnt, fill=self.font_color)
                    if harp_rescale != 1:
                        header = header.resize((int(header.size[0] * harp_rescale), int(header.size[1] * harp_rescale)),
                                               resample=Image.LANCZOS)
                    song_render = self.trans_paste(song_render, header, (int(x_in_png), int(y_in_png)))
                    y_in_png += (h+1) * numlines * harp_rescale
        else:
            fnt = ImageFont.truetype(self.png_font_path, self.png_font_size)
            h = self.get_png_text_height(fnt)
            title_header = Image.new('RGBA', (int(self.png_line_width), int(h)))
            draw = ImageDraw.Draw(title_header)
            draw.text((0, 0), meta['title'][1] + '(page ' + str(filenum + 1) + ')', font=fnt, fill=self.font_color)
            if harp_rescale != 1:
                title_header = title_header.resize(
                    (int(title_header.size[0] * harp_rescale), int(title_header.size[1] * harp_rescale)),
                    resample=Image.LANCZOS)
            song_render = self.trans_paste(song_render, title_header, (int(x_in_png), int(y_in_png)))
            y_in_png += 2 * h * harp_rescale + self.png_harp_spacings[1]    
    
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
        
        instrument_renderer = PngInstrumentRenderer(self.locale)
        
        # Determines png size as a function of the numer of chords per line
        self.set_png_harp_size(song.get_max_instruments_per_line())
        self.set_png_voice_size()
        harp_rescale = self.get_png_harp_rescale()
        song_render = Image.new('RGBA', self.png_size, self.png_color)

        # Horizontal line drawing, to be used several times later
        hr_line = Image.new('RGBA', (int(self.png_line_width), 3))
        draw = ImageDraw.Draw(hr_line)
        draw = draw.line(((0, 1), (self.png_line_width, 1)), fill=(150, 150, 150), width=1)

        x_in_png = int(self.png_margins[0])
        y_in_png = int(self.png_margins[0])
        
        (song_render, x_in_png, y_in_png) = self.write_header(song_render, filenum, song, x_in_png, y_in_png)

        ysong = y_in_png
        instrument_index = 0
        end_row = song.get_num_lines()
        end_col = 0
        ncols = self.maxIconsPerLine
        page_break = False
        
        # Creating a new song image, located at x_in_song, yline_in_song
        xline_in_song = x_in_png
        yline_in_song = ysong
        for row in range(start_row, end_row):

            line = song.get_line(row)
            if row > start_row:
                start_col = 0            
            linetype = line[0].get_type()
            ncols = len(line) - start_col
            end_col = len(line)
            
            # Line
            if linetype.lower().strip() == 'voice':
                line_render = Image.new('RGBA', (int(self.png_line_width), int(self.png_lyric_size[1])), self.png_color)
            else:
                # Dividing line
                yline_in_song += self.png_harp_spacings[1] / 4.0
                song_render.paste(hr_line, (int(xline_in_song), int(yline_in_song)))
                yline_in_song += hr_line.size[1] + self.png_harp_spacings[1] / 2.0

                line_render = Image.new('RGBA', (int(self.png_line_width), int(self.png_harp_size[1])), self.png_color)

            # Creating a new instrument image, starting at x=0 (in line) and y=0 (in line)           
            sub_line = 0
            x = 0
            y = 0
            for col in range(start_col, end_col):

                instrument = song.get_instrument(row, col)
                instrument.set_index(instrument_index)
                
                # Creating a new line if max number is exceeded
                if x + self.png_harp_size[0] + self.png_harp_spacings[0] / 2.0 > self.png_line_width:
                    x = 0
                    song_render = self.trans_paste(song_render, line_render, (int(xline_in_song), int(yline_in_song)))
                    yline_in_song += line_render.size[1] + self.png_harp_spacings[1] / 2.0
                    if linetype.lower() != 'voice':
                        yline_in_song += self.png_harp_spacings[1] / 2.0

                    sub_line += 1
                    # New Line
                    if linetype.lower().strip() == 'voice':
                        line_render = Image.new('RGBA', (int(self.png_line_width), int(self.png_lyric_size[1])),
                                                self.png_color)
                    else:
                        line_render = Image.new('RGBA', (int(self.png_line_width), int(self.png_harp_size[1])),
                                                self.png_color)

                #NEW
                if linetype.lower().strip() == 'voice':
                    ypredict = yline_in_song + (self.png_lyric_size[1] + self.png_harp_spacings[1] )
                else:
                    ypredict = yline_in_song + (self.png_harp_size[1] + self.png_harp_spacings[1])

                if ypredict > (self.png_size[1] - self.png_margins[1]):
                    page_break = True
                    end_col = col
                    break

                # INSTRUMENT RENDER
                instrument_render = instrument_renderer.render(instrument, harp_rescale)
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
            if linetype.lower().strip() != 'voice':
                yline_in_song += self.png_harp_spacings[1] / 2.0

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
