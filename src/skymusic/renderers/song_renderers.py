import re, io
import json
from src.skymusic.modes import RenderMode, CSSMode
from src.skymusic import Lang
from src.skymusic.resources import Resources
from src.skymusic.renderers.instrument_renderers import InstrumentHTMLRenderer, InstrumentSVGRenderer, \
InstrumentPNGRenderer, InstrumentMIDIRenderer, InstrumentSKYJSONRenderer, InstrumentASCIIRenderer

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



class SongRenderer():
    
    def __init__(self, locale=None):
        
        if locale is None:
            self.locale = Lang.guess_locale()
            print(f"**WARNING: Song self.maker has no locale. Reverting to: {self.locale}")
        else:
            self.locale = locale


    def write_buffers(self, song, **kwargs):
        
        return


class SongHTMLRenderer(SongRenderer):

    def __init__(self, locale=None):
        
        super().__init__(locale)
        self.HTML_note_width = '1em'

    def write_headers(self, html_buffer, song, css_mode, rel_css_path):
        
        meta = song.get_meta()
        css_path = Resources.css_path

        html_buffer.write(f'<!DOCTYPE html>'
                          f'\n<html xmlns:svg="http://www.w3.org/2000/svg">'
                          f"\n<head>\n<title>{meta['title'][1]}</title>")

        if css_mode == CSSMode.EMBED:
            try:
                with open(css_path, 'r', encoding='utf-8', errors='ignore') as css_file:
                    css_file = css_file.read()
            except FileNotFoundError as e:
                print(e)
                print("\n***Warning: could not open CSS file to embed it in HTML.\n")
                css_file = ''
            html_buffer.write('\n<style type="text/css">\n')
            html_buffer.write(css_file)
            html_buffer.write('\n</style>')
        elif css_mode == CSSMode.IMPORT:
            html_buffer.write('\n<style type="text/css">')
            html_buffer.write("@import url(\'%s\');</style>" % rel_css_path.replace('\\','/'))
        elif css_mode == CSSMode.XML:
            html_buffer.write(f'\n<link href="{rel_css_path}" rel="stylesheet" />')

        html_buffer.write('\n<meta charset="utf-8"/></head>\n<body>')
        html_buffer.write(f"\n<h1>{meta['title'][1]}</h1>")

        for k in meta:
            if k != 'title':
                html_buffer.write(f"\n<p> <b>{meta[k][0]}</b>{meta[k][1]}</p>")

        html_buffer.write('\n<div id="transcript">\n')
        
        return html_buffer


    def write_footer(self, html_buffer):
        
        html_buffer.write('\n</div>'
                          '\n</body>'
                          '\n</html>')
       
        return html_buffer        


    def write_buffers(self, song, css_mode=CSSMode.EMBED, rel_css_path='css/main.css'):    
        
        html_buffer = io.StringIO()

        self.write_headers(html_buffer, song, css_mode, rel_css_path)      

        song_render = ''
        instrument_index = 0
        song_lines = song.get_lines()
        instrument_renderer = InstrumentHTMLRenderer(self.locale)
        
        for line in song_lines:
            if len(line) > 0:
                if line[0].get_type() == 'voice':
                    song_render += '\n<br />'
                else:
                    song_render += '\n<hr />'

                line_render = '\n'
                for instrument in line:
                    instrument.set_index(instrument_index)
                    #instrument_render = instrument.render_in_html(self.HTML_note_width)
                    instrument_render = instrument_renderer.render(instrument, self.HTML_note_width)
                    instrument_render += ' '
                    instrument_index += 1
                    line_render += instrument_render

                song_render += line_render

        html_buffer.write(song_render)

        self.write_footer(html_buffer)

        return [html_buffer]

 

class SongSVGRenderer(SongRenderer):

    def __init__(self, locale=None, aspect_ratio=16/9.0):
        
        super().__init__(locale)

        self.harp_AspectRatio = 1.455
        self.harp_relspacings = (0.13, 0.1)  # Fraction of the harp width that will be allocated to the spacing between harps

        self.aspect_ratio = aspect_ratio
        self.maxIconsPerLine = round(10*aspect_ratio/(16/9.0))
        self.maxLinesPerFile = 10
        self.maxFiles = 10

        self.SVG_viewPort = (0.0, 0.0, 750*self.aspect_ratio, 750.0)
        minDim = self.SVG_viewPort[2] * 0.01
        self.SVG_viewPortMargins = (13.0, 7.5)
        self.pt2px = 96.0 / 72
        self.fontpt = 12
        self.SVG_text_height = self.fontpt * self.pt2px  # In principle this should be in em
        self.SVG_line_width = self.SVG_viewPort[2] - self.SVG_viewPortMargins[0]
        SVG_harp_width = max(minDim, (self.SVG_viewPort[2] - self.SVG_viewPortMargins[0]) / (
                1.0 * self.maxIconsPerLine * (1 + self.harp_relspacings[0])))
        self.SVG_harp_size = (SVG_harp_width, max(minDim, SVG_harp_width / self.harp_AspectRatio))
        self.SVG_harp_spacings = (
            self.harp_relspacings[0] * SVG_harp_width,
            self.harp_relspacings[1] * SVG_harp_width / self.harp_AspectRatio)

    def get_voice_SVG_height(self):
        """Tries to predict the height of the lyrics text when rendered in SVG"""
        return self.fontpt * self.pt2px

    def write_headers(self, svg_buffer, filenum, song, css_mode, rel_css_path):
         
        css_path = Resources.css_path
        meta = song.get_meta()                 
        # SVG/XML headers
        svg_buffer.write('<?xml version="1.0" encoding="utf-8" ?>')

        if css_mode == CSSMode.HREF:
            svg_buffer.write(f'\n<?xml-stylesheet href="{rel_css_path}" type="text/css" alternate="no" media="all"?>')

        SVG_viewPort_str = ' '.join((str(self.SVG_viewPort[0]), str(self.SVG_viewPort[1]), str(self.SVG_viewPort[2]),str(self.SVG_viewPort[3])))
        svg_buffer.write(f'\n<svg baseProfile="full" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:ev="http://www.w3.org/2001/xml-events" xmlns:xlink="http://www.w3.org/1999/xlink"'
                         f' width="100%" height="100%"'
                         f' viewBox="{SVG_viewPort_str}" preserveAspectRatio="xMinYMin">')

        if css_mode == CSSMode.EMBED:
            try:
                with open(css_path, 'r', encoding='utf-8', errors='ignore') as css_file:
                    css_file = css_file.read()
            except:
                print("\n***Warning: could not open CSS file to embed it in SVG.\n")
                css_file = ''
                pass
            svg_buffer.write('\n<defs><style type="text/css"><![CDATA[\n')
            svg_buffer.write(css_file)
            svg_buffer.write('\n]]></style></defs>')
        elif css_mode == CSSMode.IMPORT:
            svg_buffer.write('\n<defs><style type="text/css">')
            svg_buffer.write("@import url(\'%s\');</style></defs>" % rel_css_path.replace('\\','/'))
        else:
            svg_buffer.write('\n<defs></defs>')

        svg_buffer.write(f"\n<title>{meta['title'][1]}-{filenum}</title>")        


    def write_buffers(self, song, css_mode=CSSMode.EMBED, rel_css_path='css/main.css', start_row=0, start_col=0, buffer_list=None):

        if buffer_list is None:
            buffer_list = []
        if len(buffer_list) > self.maxFiles:
            print(f"\nYour song is too long. Stopping at {self.maxFiles} files.")
            return buffer_list

        instrument_renderer = InstrumentSVGRenderer(self.locale)

        svg_buffer = io.StringIO()
        filenum = len(buffer_list)
        meta = song.get_meta()

        self.write_headers(svg_buffer, filenum, song, css_mode, rel_css_path)             
       
        # Header SVG container
        song_header = (f'\n<svg x="{self.SVG_viewPortMargins[0] :.2f}" y="{self.SVG_viewPortMargins[1] :.2f}"'
                       f' width="{self.SVG_line_width :.2f}" height="{(self.SVG_viewPort[3] - self.SVG_viewPortMargins[1]) :.2f}">'
                       )

        x = 0
        y = self.SVG_text_height  # Because the origin of text elements of the bottom-left corner

        if filenum == 0:
            song_header += f"\n<text x=\"{x :.2f}\" y=\"{y :.2f}\" class=\"title\">{meta['title'][1]}</text>"           
            
            for k in meta:
                if k != 'title':
                    y += 2 * self.SVG_text_height
                    song_header += f'\n<text x="{x :.2f}" y="{y :.2f}" class="headers">{meta[k][0]} {meta[k][1]}</text>'
                    
        else:
            song_header += f"\n<text x=\"{x :.2f}\" y=\"{y :.2f}\" class=\"title\">{meta['title'][1]} (page {(filenum + 1)})</text>"

        # Dividing line
        y += self.SVG_text_height
                
        song_header += (f'\n<svg x="0" y="{y :.2f}" width="{self.SVG_line_width :.2f}" height="{(self.SVG_harp_spacings[1] / 2.0) :.2f}">'
                        f'\n<line x1="0" y1="50%" x2="100%" y2="50%" class="divide"/> '
                        f'\n</svg>')
                
        y += self.SVG_text_height

        song_header += '\n</svg>'

        svg_buffer.write(song_header)

        # Song SVG container
        ysong = y

        song_render = (f'\n<svg x="{self.SVG_viewPortMargins[0] :.2f}" y="{y :.2f}"'
                       f' width="{self.SVG_line_width :.2f}" height="{(self.SVG_viewPort[3] - y) :.2f}" class="song">'
                      )
        y = 0  # Because we are nested in a new SVG
        x = 0
        instrument_index = 0
        # end_row = min(start_row+self.maxLinesPerFile,len(self.lines))
        end_row = song.get_num_lines()
        end_col = 0
        ncols = self.maxIconsPerLine
        page_break = False
        for row in range(start_row, end_row):

            line = song.get_line(row)
            if row > start_row:
                start_col = 0
            linetype = line[0].get_type()
            ncols = len(line) - start_col
            end_col = len(line)
            
            # Line SVG container
            if linetype.lower().strip() == 'voice':
                
                song_render += (f'\n<svg x="0" y="{y :.2f}" width="{self.SVG_line_width :.2f}" height="{self.SVG_text_height :.2f}"'
                                f' class="instrument-line line-{row}">'
                               )
                y += self.SVG_text_height + self.SVG_harp_spacings[1] / 2.0
                
            else:
                # Dividing line
                y += self.SVG_harp_spacings[1] / 4.0
                song_render += (f'\n<svg x="0" y="{y :.2f}" width="{self.SVG_line_width :.2f}" height="{(self.SVG_harp_spacings[1] / 2.0) :.2f}">'
                                f'\n<line x1="0" y1="50%" x2="100%" y2="50%" class="divide"/>'
                                f'\n</svg>'
                               )
                y += self.SVG_harp_spacings[1] / 4.0

                y += self.SVG_harp_spacings[1] / 2.0

                song_render += (f'\n<svg x="0" y="{y :.2f}" width="{self.SVG_line_width :.2f}" height="{self.SVG_harp_size[1] :.2f}"'
                                f' class="instrument-line line-{row}">'
                                )

                y += self.SVG_harp_size[1] + self.SVG_harp_spacings[1] / 2.0


            line_render = ''
            sub_line = 0
            x = 0
            for col in range(start_col, end_col):

                instrument = song.get_instrument(row, col)
                instrument.set_index(instrument_index)

                #NEW
                if linetype.lower().strip() == 'voice':
                    ypredict = y + ysong + (self.SVG_text_height + self.SVG_harp_spacings[1] / 2.0) + self.SVG_harp_spacings[1] / 2.0                
                else:
                    ypredict = y + ysong + (self.SVG_harp_size[1] + self.SVG_harp_spacings[1]) + self.SVG_harp_spacings[1] / 2.0

                if ypredict > (self.SVG_viewPort[3] - self.SVG_viewPortMargins[1]):
                    page_break = True
                    end_col = col
                    break


                # Creating a new line if max number is exceeded
                if (int(1.0 * (col-start_col+1) / self.maxIconsPerLine) - sub_line) > 0:

                    
                    # Closing previous instrument-line
                    line_render += '\n</svg>'
                    sub_line += 1
                    x = 0

                     # print('max reached at row=' + str(row) + ' col=' + str(col))
                    # New Line SVG placeholder
                    if linetype.lower().strip() == 'voice':
                        line_render += (f'\n<svg x="0" y="{y :.2f}" width="{self.SVG_line_width :.2f}" height="{self.SVG_text_height :.2f}"'
                                        f' class="instrument-line line-{row}-{sub_line}">'
                                        )
                        y += self.SVG_text_height + self.SVG_harp_spacings[1] / 2.0
                    else:
                        y += self.SVG_harp_spacings[1] / 2.0

                        line_render += (f'\n<svg x="0" y="{y :.2f}" width="{self.SVG_line_width :.2f}" height="{self.SVG_harp_size[1] :.2f}"'
                                        f' class="instrument-line line-{row}-{sub_line}">'
                                        )

                        y += self.SVG_harp_size[1] + self.SVG_harp_spacings[1] / 2.0

                # INSTRUMENT RENDER
#                instrument_render = instrument.render_in_svg(x, f"{(100.0 * self.SVG_harp_size[0] / self.SVG_line_width)}%", "100%", self.harp_AspectRatio)
                instrument_render = instrument_renderer.render(instrument, x, f"{(100.0 * self.SVG_harp_size[0] / self.SVG_line_width)}%", "100%", self.harp_AspectRatio)

                # REPEAT
                if instrument.get_repeat() > 1:

                    instrument_render += (f'\n<svg x="{(x + self.SVG_harp_size[0]) :.2f}" y="0%" class="repeat"'
                                          f' width="{(100.0 * self.SVG_harp_size[0] / self.SVG_line_width) :.2f}%" height="100%">'
                                         )
                    instrument_render += f'\n<text x="2%" y="98%" class="repeat">x{instrument.get_repeat()} </text></svg>'

                    x += self.SVG_harp_spacings[0]

                line_render += instrument_render
                instrument_index += 1
                x += self.SVG_harp_size[0] + self.SVG_harp_spacings[0]

            #end loop on cols: closing line
            line_render += '\n</svg>'  # Close instrument-line SVG
            song_render += line_render

            if page_break:
                end_row = row
                break

        #End loop on rows                
        song_render += '\n</svg>'  # Close song-class SVG
        
        svg_buffer.write(song_render)
        svg_buffer.write('\n</svg>')  # Close file SVG

        buffer_list.append(svg_buffer)

        # Open new file
        if end_row < song.get_num_lines() or end_col < ncols:
            buffer_list = self.write_buffers(song, css_mode, rel_css_path, end_row, end_col, buffer_list)

        return buffer_list


class SongPNGRenderer(SongRenderer):

    def __init__(self, locale=None, aspect_ratio=16.0/9):
        
        super().__init__(locale)
        
        self.harp_AspectRatio = 1.455
        self.harp_relspacings = (0.13, 0.1)  # Fraction of the harp width that will be allocated to the spacing between harps

        self.aspect_ratio = aspect_ratio
        self.maxIconsPerLine = round(10*aspect_ratio/(16/9.0))
        self.maxFiles = 10

        if not no_PIL_module:
            self.png_size = (round(self.aspect_ratio*750 * 2), 750 * 2)  # must be an integer tuple
            self.png_margins = (13, 7)
            self.png_harp_size0 = InstrumentPNGRenderer(self.locale).get_png_chord_size()  # A tuple
            self.png_harp_spacings0 = (int(self.harp_relspacings[0] * self.png_harp_size0[0]),
                                       int(self.harp_relspacings[1] * self.png_harp_size0[1]))
            self.png_harp_size = None
            self.png_harp_spacings = None
            self.png_line_width = int(self.png_size[0] - self.png_margins[0])  # self.png_lyric_relheight = instruments.Voice().lyric_relheight
            self.png_lyric_size0 = (self.png_harp_size0[0], InstrumentPNGRenderer(self.locale).get_lyric_height())
            self.png_lyric_size = None
            self.png_dpi = (96 * 2, 96 * 2)
            self.png_compress = Resources.png_compress
            self.font_color = (0, 0, 0)
            self.png_color = (255, 255, 255)
            # self.font_color = (0, 0, 0)   #Discord colors
            # self.png_color = (54, 57, 63)    #Discord colors
            self.png_font_size = Resources.png_font_size
            self.png_title_font_size = Resources.png_title_font_size
            self.png_font = Resources.font_path


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


    def write_header(self, song_render, filenum, song, x_in_png, y_in_png):
    
        meta = song.get_meta()
        harp_rescale = self.get_png_harp_rescale()
    
        if filenum == 0:

            fnt = ImageFont.truetype(self.png_font, self.png_title_font_size)
            h = self.get_png_text_height(fnt)
            title_header = Image.new('RGBA', (int(self.png_line_width), int(h)))
            draw = ImageDraw.Draw(title_header)
            draw.text((0, 0), meta['title'][1], font=fnt, fill=self.font_color)
            if harp_rescale != 1:
                title_header = title_header.resize(
                    (int(title_header.size[0] * harp_rescale), int(title_header.size[1] * harp_rescale)),
                    resample=Image.LANCZOS)
            song_render = self.trans_paste(song_render, title_header, (int(x_in_png), int(y_in_png)))
            y_in_png += h * 2 * harp_rescale

            for k in meta:
                if k != 'title':
                    fnt = ImageFont.truetype(self.png_font, self.png_font_size)
                    h = self.get_png_text_height(fnt)
                    header = Image.new('RGBA', (int(self.png_line_width), int(h)))
                    draw = ImageDraw.Draw(header)
                    draw.text((0, 0), meta[k][0] + ' ' + meta[k][1], font=fnt, fill=self.font_color)
                    if harp_rescale != 1:
                        header = header.resize((int(header.size[0] * harp_rescale), int(header.size[1] * harp_rescale)),
                                               resample=Image.LANCZOS)
                    song_render = self.trans_paste(song_render, header, (int(x_in_png), int(y_in_png)))
                    y_in_png += h * 2 * harp_rescale
        else:
            fnt = ImageFont.truetype(self.png_font, self.png_font_size)
            h = self.get_png_text_height(fnt)
            title_header = Image.new('RGBA', (int(self.png_line_width), int(h)))
            draw = ImageDraw.Draw(title_header)
            draw.text((0, 0), meta['title'][1] + '(page ' + str(filenum + 1) + ')', font=fnt, fill=self.font_color)
            if harp_rescale != 1:
                title_header = title_header.resize(
                    (int(title_header.size[0] * harp_rescale), int(title_header.size[1] * harp_rescale)),
                    resample=Image.LANCZOS)
            song_render = self.trans_paste(song_render, title_header, (int(x_in_png), int(y_in_png)))
            y_in_png += 2 * h + self.png_harp_spacings[1]    
    
        return (song_render, x_in_png, y_in_png)
    

    def write_buffers(self, song, start_row=0, start_col=0, buffer_list=None):
        
        if buffer_list is None:
            buffer_list = []
        global no_PIL_module

        if no_PIL_module:
            print("\n***WARNING: PNG was not rendered because PIL module was not found. ***\n")
            return None
     
        filenum = len(buffer_list)
        if len(buffer_list) > self.maxFiles:
            print(f"\nYour song is too long. Stopping at {self.maxFiles} files.")
            return buffer_list
        
        instrument_renderer = InstrumentPNGRenderer(self.locale)
        
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
            if min([ncols, self.maxIconsPerLine])*(self.png_harp_size[0] + self.png_harp_spacings[0]) > self.png_line_width:
                nsublines_predict = 2
            else:
                nsublines_predict = 1
            sub_line = 0
            x = 0
            y = 0
            for col in range(start_col, end_col):

                instrument = song.get_instrument(row, col)
                instrument.set_index(instrument_index)
                
                #NEW
                if linetype.lower().strip() == 'voice':
                    ypredict = yline_in_song + (self.png_lyric_size[1] + self.png_harp_spacings[1] / 2.0)* nsublines_predict + self.png_harp_spacings[1] / 2.0
                else:
                    ypredict = yline_in_song + (self.png_harp_size[1] + self.png_harp_spacings[1])*nsublines_predict + self.png_harp_spacings[1] / 2.0
    
                if ypredict > (self.png_size[1] - self.png_margins[1]):
                    page_break = True
                    end_col = col
                    break

                # Creating a new line if max number is exceeded
                if x + self.png_harp_size[0] + self.png_harp_spacings[0] / 2.0 > self.png_line_width:
                    x = 0
                    song_render = self.trans_paste(song_render, line_render, (int(xline_in_song), int(yline_in_song)))
                    yline_in_song += line_render.size[1] + self.png_harp_spacings[1] / 2.0
                    if linetype.lower() != 'voice':
                        yline_in_song += self.png_harp_spacings[1] / 2.0

                    sub_line += 1
                    # print('max reached at row=' + str(row) + ' col=' + str(col))
                    # New Line
                    if linetype.lower().strip() == 'voice':
                        line_render = Image.new('RGBA', (int(self.png_line_width), int(self.png_lyric_size[1])),
                                                self.png_color)
                    else:
                        line_render = Image.new('RGBA', (int(self.png_line_width), int(self.png_harp_size[1])),
                                                self.png_color)

                # INSTRUMENT RENDER
                #instrument_render = instrument.render_in_png(harp_rescale)
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

        buffer_list.append(song_buffer)

        # Open new file
        if end_row < song.get_num_lines() or end_col < ncols:
            buffer_list = self.write_buffers(song, end_row, end_col, buffer_list)

        return buffer_list


class SongMIDIRenderer(SongRenderer):

    def __init__(self, locale=None, song_bpm=120):
        
        super().__init__(locale)
        
        if not no_mido_module:
            # WARNING: instrument codes correspond to General Midi codes (see Wikipedia) minus 1
            # An instrument will sound very strange if played outside its natural pitch range
            midi_instruments = {'piano': 0, 'guitar': 24, 'flute': 73, 'pan': 75}
            self.midi_note_duration = 0.3  # note duration is seconds for 120 bpm
            self.midi_bpm = song_bpm  # Beats per minute
            self.midi_instrument = midi_instruments['piano']
            self.midi_key = None


    def write_header(self, mid, track, tempo):
                
        track.append(mido.MetaMessage('set_tempo', tempo=tempo))

        try:
            track.append(mido.MetaMessage('key_signature', key=self.midi_key))
        except ValueError:
            print("\n***Warning: invalid key passed to MIDI renderer. Using C instead.\n")
            track.append(mido.MetaMessage('key_signature', key='C'))
        try:
            track.append(mido.Message('program_change', program=self.midi_instrument, time=0))
        except ValueError:
            print("\n***Warning: invalid instrument passed to MIDI renderer. Using piano instead.\n")
            track.append(mido.Message('program_change', program=1, time=0))      


    def write_buffers(self, song):
        global no_mido_module

        if no_mido_module:
            print("\n***WARNING: MIDI was not created because mido module was not found. ***\n")
            return None
    
        try:
            self.midi_key = re.sub(r'#', '#m', song.get_music_key())  # For mido sharped keys are minor
        except TypeError:
            print("\n***Warning: Invalid music key passed to the MIDI renderer: using C instead\n")
            self.midi_key = 'C'

        try:
            tempo = mido.bpm2tempo(self.midi_bpm)
        except ValueError:
            print("\n***Warning: invalid tempo passed to MIDI renderer. Using 120 bpm instead.\n")
            tempo = mido.bpm2tempo(120)

        mid = mido.MidiFile(type=0)
        track = mido.MidiTrack()
        mid.tracks.append(track)

        sec = mido.second2tick(1, ticks_per_beat=mid.ticks_per_beat, tempo=tempo)  # 1 second in ticks
        note_ticks = self.midi_note_duration * sec * 120 / self.midi_bpm  # note duration in ticks
                        
        self.write_header(mid, track, tempo)

        instrument_renderer = InstrumentMIDIRenderer(self.locale)
        song_lines = song.get_lines()
        for line in song_lines:
            if len(line) > 0:
                if line[0].get_type().lower().strip() != 'voice':
                    instrument_index = 0
                    for instrument in line:
                        instrument.set_index(instrument_index)
                        #instrument_render = instrument.render_in_midi(note_duration=note_ticks,
                        #                                              music_key=song.get_music_key())
                        instrument_render = instrument_renderer.render(instrument, note_duration=note_ticks,
                                                                      music_key=song.get_music_key())
                        for i in range(0, instrument.get_repeat()):
                            for note_render in instrument_render:
                                track.append(note_render)
                            instrument_index += 1
        
        midi_buffer = io.BytesIO()
        mid.save(file=midi_buffer)

        return [midi_buffer]

class SongSKYJSONRenderer(SongRenderer):

    def __init__(self, locale=None, song_bpm=120):
        
        super().__init__(locale)
        self.song_bpm = song_bpm

    def write_buffers(self, song):

        meta = song.get_meta()
        dt = (60000/self.song_bpm) / 4
        
        #print('%%DEBUG')
        #print(dt)
    
        json_buffer = io.StringIO()

        instrument_renderer = InstrumentSKYJSONRenderer(self.locale)
        
        json_dict = {'name': meta['title'][1], 'songNotes': []}
    
        instrument_index = 0
        time = 0
        for line in song.get_lines():
            if len(line) > 0:
                if line[0].get_type().lower().strip() != 'voice':
                    for instrument in line:
                        instrument.set_index(instrument_index)
                        repeat = instrument.get_repeat()
                        for r in range(repeat):
                            time += dt
                            if not instrument.get_is_silent():
                                json_dict['songNotes'] += instrument_renderer.render(instrument, time)
  
                        instrument_index += 1

        print(json_dict)
        
        json.dump([json_dict], json_buffer)

        return [json_buffer]

class SongASCIIRenderer(SongRenderer):

    def __init__(self, locale=None):
        
        super().__init__(locale) 
        
    def write_buffers(self, song, render_mode):

        meta = song.get_meta()
        ascii_buffer = io.StringIO()

        note_parser = render_mode.get_note_parser()
        instrument_renderer = InstrumentASCIIRenderer(self.locale)
        
        ascii_buffer.write(f"{Resources.COMMENT_DELIMITER}{meta['title'][1]}\n")

        for k in meta:
            if k != 'title':
                ascii_buffer.write(f"{Resources.COMMENT_DELIMITER}{meta[k][0]}{meta[k][1]}\n")

        
        song_render = '\n'
        instrument_index = 0
        for line in song.get_lines():
            line_render = ''
            for instrument in line:
                instrument.set_index(instrument_index)
                #instrument_render = instrument.render_in_ascii(note_parser)
                instrument_render = instrument_renderer.render(instrument, note_parser)                
                repeat = instrument.get_repeat()
                if repeat > 1:
                    instrument_render += Resources.REPEAT_INDICATOR + str(repeat)
                line_render += instrument_render + re.sub('\\\\s', ' ', Resources.ICON_DELIMITER)
                instrument_index += 1
            song_render += '\n' + line_render

        ascii_buffer.write(song_render)

        return [ascii_buffer]

