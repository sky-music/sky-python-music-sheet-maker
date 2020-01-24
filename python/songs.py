from modes import RenderModes, CSSModes
import instruments
import os
import parsers
import re

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


class Song():

    def __init__(self, music_key='C'):

        if isinstance(music_key, str):
            self.music_key = music_key
        else:
            print('Warning: Invalid song key: using C instead')
            self.music_key = 'C'

        self.lines = []
        self.title = 'Untitled'
        self.headers = [['Original Artist(s):', 'Transcript:', 'Musical key:'], ['', '', '']]
        self.maxIconsPerLine = 10
        self.maxLinesPerFile = 10
        self.maxFiles = 10
        self.harp_AspectRatio = 1.455
        self.harp_relspacings = (
        0.13, 0.1)  # Fraction of the harp width that will be allocated to the spacing between harps

        self.HTML_note_width = '1em'

        self.SVG_viewPort = (0.0, 0.0, 1334.0, 750.0)
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
        self.harp_relspacings[0] * SVG_harp_width, self.harp_relspacings[1] * SVG_harp_width / self.harp_AspectRatio)

        if no_PIL_module == False:
            self.png_size = (1334 * 2, 750 * 2)  # must be an integer tuple
            self.png_margins = (13, 7)
            self.png_harp_size0 = instruments.Harp().render_in_png().size  # A tuple
            self.png_harp_spacings0 = (int(self.harp_relspacings[0] * self.png_harp_size0[0]),
                                       int(self.harp_relspacings[1] * self.png_harp_size0[1]))
            self.png_harp_size = None
            self.png_harp_spacings = None
            self.png_line_width = int(self.png_size[0] - self.png_margins[
                0])  # self.png_lyric_relheight = instruments.Voice().lyric_relheight
            self.png_lyric_size0 = (self.png_harp_size0[0], instruments.Voice().get_lyric_height())
            self.png_lyric_size = None
            self.png_dpi = (96 * 2, 96 * 2)
            self.png_compress = 6
            self.font_color = (0, 0, 0)
            self.png_color = (255, 255, 255)
            # self.font_color = (0, 0, 0)   #Discord colors
            # self.png_color = (54, 57, 63)    #Discord colors
            self.png_font_size = 36
            self.png_title_font_size = 48
            self.png_font = 'fonts/NotoSansCJKjp-Regular.otf'

        if no_mido_module == False:
            # WARNING: instrument codes correspond to General Midi codes (see Wikipedia) minus 1
            # Instrument will sound very strange if played outside its natural pitch range
            midi_instruments = {'piano': 0, 'guitar': 24, 'flute': 73, 'pan': 75}
            self.midi_note_duration = 0.3  # note duration is seconds for 120 bpm
            self.midi_bpm = 120  # Beats per minute
            self.midi_instrument = midi_instruments['piano']
            try:
                self.midi_key = re.sub(r'#', '#m', self.music_key)  # For mido sharped keys are minor
            except:
                print('Warning: Invalid music key passed to the MIDI renderer: using C instead')
                self.midi_key = 'C'

    def add_line(self, line):
        '''Adds a line of Instrument to the Song'''
        if len(line) > 0:
            if isinstance(line[0], instruments.Instrument):
                self.lines.append(line)

    def get_line(self, row):
        '''Returns line #row, if row is in the Song, or else returns an empty list'''
        try:
            return self.lines[row]
        except:
            return [[]]

    def get_music_key(self):

        return self.music_key

    def get_song(self):
        '''Returns the Song, a list of lists of Instruments'''
        return self.lines

    def get_instrument(self, row, col):
        '''Returns the Instrument object at row, col in the Song'''
        try:
            return self.lines[row][col]
        except:
            return []

    def get_num_lines(self):
        '''Returns the number of lines n the Song'''
        return len(self.lines)

    def __len__(self):
        return self.get_num_instruments()

    def __str__(self):
        return '<Song \'' + self.title + '\', ' + str(self.get_num_lines()) + ' lines, ' \
               + str(self.get_num_instruments()) + ' instruments, ' + str(self.get_num_broken()) + ' errors>'

    def get_num_instruments(self):
        '''Returns the number of instruments in the Song'''
        c = 0
        for line in self.lines:
            c += len(line)
        return c

    def get_num_broken(self):
        '''Returns the number of broken instruments in the Song'''
        b = 0
        for line in self.lines:
            for instr in line:
                try:
                    b += int(instr.get_is_broken())
                except:
                    pass
        return b

    def get_max_instruments_per_line(self):
        '''Returns the number of instruments in the longest line'''
        if len(self.lines) > 0:
            return max(list(map(len, self.lines)))
        else:
            return 0

    def set_title(self, title):
        self.title = title

    def set_headers(self, original_artists='', transcript_writer='', musical_key=''):
        self.headers[1] = [original_artists, transcript_writer, musical_key]

    def get_voice_SVG_height(self):
        '''Tries to predict the height of the lyrics text when rendered in SVG'''
        return self.fontpt * self.pt2px

    def set_png_harp_size(self):
        '''Shrinks the Harp image, so that the longest line fits up to max_instruments_per_line instruments'''
        if self.png_harp_size == None or self.png_harp_spacings == None:
            Nmax = max(1, min(self.maxIconsPerLine, self.get_max_instruments_per_line()))
            new_harp_width = min(self.png_harp_size0[0],
                                 (self.png_size[0] - self.png_margins[0]) / (Nmax * (1.0 + self.harp_relspacings[0])))
            self.png_harp_size = (new_harp_width, new_harp_width / self.harp_AspectRatio)
            self.png_harp_spacings = (
            self.harp_relspacings[0] * self.png_harp_size[0], self.harp_relspacings[1] * self.png_harp_size[1])
            self.png_lyric_size = (self.png_harp_size[0], (self.png_harp_size[1] / self.png_harp_size0[1]))

    def set_png_voice_size(self):
        self.png_lyric_size = (
        self.png_lyric_size0[0] * self.get_png_harp_rescale(), self.png_lyric_size0[1] * self.get_png_harp_rescale())

    def get_png_harp_rescale(self):
        '''Gets the rescale factor to from the original .png Harp image'''
        if self.png_harp_size[0] != None:
            return 1.0 * self.png_harp_size[0] / self.png_harp_size0[0]
        else:
            return 1.0

    def get_png_text_height(self, fnt):
        '''Calculates the text height in PNG for a standard text depending on the input font size'''
        return fnt.getsize('HQfgjyp')[1]

    def write_html(self, file_path, css_mode=CSSModes.EMBED, css_path='css/main.css'):

        try:
            html_file = open(file_path, 'w+', encoding='utf-8', errors='ignore')
        except:
            print('Could not create text file.')
            return ''

        html_file.write('<!DOCTYPE html>'
                        '\n<html xmlns:svg=\"http://www.w3.org/2000/svg\">')
        html_file.write('\n<head>\n<title>' + self.title + '</title>')

        if css_mode == CSSModes.EMBED:
            try:
                with open(css_path, 'r', encoding='utf-8', errors='ignore') as css_file:
                    css_file = css_file.read()
            except:
                print('Could not open CSS file to embed it in HTML.')
                css_file = ''
            html_file.write('\n<style type=\"text/css\">\n')
            html_file.write(css_file)
            html_file.write('\n</style>')
        elif css_mode == CSSModes.IMPORT:
            html_file.write('\n<style type=\"text/css\">')
            html_file.write("@import url(\'" + os.path.relpath(css_path, start=os.path.dirname(file_path)).replace('\\',
                                                                                                                   '/') + "\');</style>")
        elif css_mode == CSSModes.XML:
            html_file.write('\n<link href=\"' + os.path.relpath(css_path, start=os.path.dirname(
                file_path)) + '\" rel=\"stylesheet\" />')

        html_file.write('\n<meta charset="utf-8"/></head>\n<body>')
        html_file.write('\n<h1> ' + self.title + ' </h1>')

        for i in range(len(self.headers[0])):
            html_file.write('\n<p> <b>' + self.headers[0][i] + '</b> ' + self.headers[1][i] + ' </p>')

        html_file.write('\n<div id="transcript">\n')

        song_render = ''
        instrument_index = 0
        for line in self.lines:
            if len(line) > 0:
                if line[0].get_type() == 'voice':
                    song_render += '\n<br />'
                else:
                    song_render += '\n<hr />'

                line_render = '\n'
                for instrument in line:
                    instrument.set_index(instrument_index)
                    instrument_render = instrument.render_in_html(self.HTML_note_width)
                    instrument_render += ' '
                    instrument_index += 1
                    line_render += instrument_render

                song_render += line_render

        html_file.write(song_render)

        html_file.write('\n</div>'
                        '\n</body>'
                        '\n</html>')

        return file_path

    def write_ascii(self, file_path, render_mode=RenderModes.SKYASCII):

        try:
            ascii_file = open(file_path, 'w+', encoding='utf-8', errors='ignore')
        except:
            print('Could not create text file.')
            return ''

        if render_mode == RenderModes.SKYASCII:
            note_parser = parsers.SkyNoteParser()
        elif render_mode == RenderModes.ENGLISHASCII:
            note_parser = parsers.EnglishNoteParser()
        elif render_mode == RenderModes.JIANPUASCII:
            note_parser = parsers.JianpuNoteParser()
        elif render_mode == RenderModes.DOREMIASCII:
            note_parser = parsers.DoremiNoteParser()
        else:
            note_parser = parsers.SkyNoteParser()

        ascii_file.write('#' + self.title + '\n')

        for i in range(len(self.headers[0])):
            ascii_file.write('#' + self.headers[0][i] + ' ' + self.headers[1][i] + '\n')

        song_render = '\n'
        instrument_index = 0
        for line in self.lines:
            line_render = ''
            for instrument in line:
                instrument.set_index(instrument_index)
                instrument_render = instrument.render_in_ascii(note_parser)
                instrument_index += 1
                line_render += instrument_render + ' '
            song_render += '\n' + line_render

        ascii_file.write(song_render)

        return file_path

    def write_svg(self, file_path0, css_mode=CSSModes.EMBED, css_path='css/main.css', start_row=0, filenum=0):

        if filenum > self.maxFiles:
            print('\nYour song is too long. Stopping at ' + str(self.maxFiles) + ' files.')
            return filenum, file_path0

        if filenum > 0:
            (file_base, file_ext) = os.path.splitext(file_path0)
            file_path = file_base + str(filenum) + file_ext
        else:
            file_path = file_path0

        try:
            svg_file = open(file_path, 'w+', encoding='utf-8', errors='ignore')
        except:
            print('Could not create SVG file.')
            return filenum, ''

        # SVG/XML headers
        svg_file.write('<?xml version=\"1.0\" encoding=\"utf-8\" ?>')

        if css_mode == CSSModes.HREF:
            svg_file.write('\n<?xml-stylesheet href=\"' + os.path.relpath(css_path, start=os.path.dirname(
                file_path)) + '\" type=\"text/css\" alternate=\"no\" media=\"all\"?>')

        svg_file.write(
            '\n<svg baseProfile=\"full\" version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:ev=\"http://www.w3.org/2001/xml-events\" xmlns:xlink=\"http://www.w3.org/1999/xlink\"'
            ' width=\"100%\" height=\"100%\"'
            ' viewBox=\"' + ' '.join((str(self.SVG_viewPort[0]), str(self.SVG_viewPort[1]), str(self.SVG_viewPort[2]),
                                      str(self.SVG_viewPort[3]))) + '\" preserveAspectRatio=\"xMinYMin\">')

        if css_mode == CSSModes.EMBED:
            try:
                with open(css_path, 'r', encoding='utf-8', errors='ignore') as css_file:
                    css_file = css_file.read()
            except:
                print('Could not open CSS file to embed it in SVG.')
                css_file = ''
                pass
            svg_file.write('\n<defs><style type=\"text/css\"><![CDATA[\n')
            svg_file.write(css_file)
            svg_file.write('\n]]></style></defs>')
        elif css_mode == CSSModes.IMPORT:
            svg_file.write('\n<defs><style type=\"text/css\">')
            svg_file.write("@import url(\'" + os.path.relpath(css_path, start=os.path.dirname(file_path)).replace('\\',
                                                                                                                  '/') + "\');</style></defs>")
        else:
            svg_file.write('\n<defs></defs>')

        svg_file.write('\n<title>' + self.title + '-' + str(filenum) + '</title>')

        # Header SVG container
        song_header = ('\n<svg x=\"' + '%.2f' % self.SVG_viewPortMargins[0] + '\" y=\"' + '%.2f' %
                       self.SVG_viewPortMargins[1] + \
                       '\" width=\"' + '%.2f' % self.SVG_line_width + '\" height=\"' + '%.2f' % (
                                   self.SVG_viewPort[3] - self.SVG_viewPortMargins[1]) + '\">')

        x = 0
        y = self.SVG_text_height  # Because the origin of text elements of the bottom-left corner

        if filenum == 0:
            song_header += '\n<text x=\"' + str(x) + '\" y=\"' + str(y) + '\" class=\"title\">' + self.title + '</text>'
            for i in range(len(self.headers[0])):
                y += 2 * self.SVG_text_height
                song_header += '\n<text x=\"' + str(x) + '\" y=\"' + str(y) + '\" class=\"headers\">' + self.headers[0][
                    i] + ' ' + self.headers[1][i] + '</text>'
        else:
            song_header += '\n<text x=\"' + str(x) + '\" y=\"' + str(
                y) + '\" class=\"title\">' + self.title + ' (page ' + str(filenum + 1) + ')</text>'

        # Dividing line
        y += self.SVG_text_height
        song_header += (
                    '\n<svg x=\"0" y=\"' + '%.2f' % y + '\" width=\"' + '%.2f' % self.SVG_line_width + '\" height=\"' + '%.2f' % (
                        self.SVG_harp_spacings[1] / 2.0) + '\">'
                                                           '\n<line x1=\"0\" y1=\"50%\" x2=\"100%\" y2=\"50%\" class=\"divide\"/>'
                                                           '\n</svg>')
        y += self.SVG_text_height

        song_header += '\n</svg>'

        svg_file.write(song_header)

        # Song SVG container
        ysong = y
        song_render = '\n<svg x=\"' + '%.2f' % self.SVG_viewPortMargins[
            0] + '\" y=\"' + '%.2f' % y + '\" width=\"' + '%.2f' % self.SVG_line_width + '\" height=\"' + '%.2f' % (
                                  self.SVG_viewPort[3] - y) + '\" class=\"song\">'
        y = 0  # Because we are nested in a new SVG
        x = 0

        instrument_index = 0
        # end_row = min(start_row+self.maxLinesPerFile,len(self.lines))
        end_row = len(self.lines)
        for row in range(start_row, end_row):

            line = self.get_line(row)
            linetype = line[0].get_type()
            ncols = len(line)
            nsublines = int(1.0 * ncols / self.maxIconsPerLine)

            if linetype == 'voice':
                ypredict = y + ysong + (self.SVG_text_height + self.SVG_harp_spacings[1] / 2.0) * (nsublines + 1) + \
                           self.SVG_harp_spacings[1] / 2.0
            else:
                ypredict = y + ysong + (self.SVG_harp_size[1] + self.SVG_harp_spacings[1]) * (nsublines + 1) + \
                           self.SVG_harp_spacings[1] / 2.0

            if ypredict > (self.SVG_viewPort[3] - self.SVG_viewPortMargins[1]):
                end_row = row
                break

            line_render = ''
            sub_line = 0
            x = 0

            # Line SVG container
            if linetype == 'voice':
                song_render += '\n<svg x=\"0" y=\"' + '%.2f' % y + '\" width=\"' + '%.2f' % self.SVG_line_width + '\" height=\"' + '%.2f' % self.SVG_text_height + '\" class=\"instrument-line line-' + str(
                    row) + '\">'
                y += self.SVG_text_height + self.SVG_harp_spacings[1] / 2.0
            else:
                # Dividing line
                y += self.SVG_harp_spacings[1] / 4.0
                song_render += '\n<svg x=\"0" y=\"' + '%.2f' % y + '\" width=\"' + '%.2f' % self.SVG_line_width + '\" height=\"' + '%.2f' % (
                            self.SVG_harp_spacings[1] / 2.0) + '\">'
                song_render += '\n<line x1=\"0\" y1=\"50%\" x2=\"100%\" y2=\"50%\" class=\"divide\"/>'
                song_render += '\n</svg>'
                y += self.SVG_harp_spacings[1] / 4.0

                y += self.SVG_harp_spacings[1] / 2.0
                song_render += '\n<svg x=\"0" y=\"' + '%.2f' % y + '\" width=\"' + '%.2f' % self.SVG_line_width + '\" height=\"' + '%.2f' % \
                               self.SVG_harp_size[1] + '\" class=\"instrument-line line-' + str(row) + '\">'
                y += self.SVG_harp_size[1] + self.SVG_harp_spacings[1] / 2.0

            for col in range(ncols):

                instrument = self.get_instrument(row, col)
                instrument.set_index(instrument_index)

                # Creating a new line if max number is exceeded
                if (int(1.0 * col / self.maxIconsPerLine) - sub_line) > 0:
                    line_render += '\n</svg>'
                    sub_line += 1
                    x = 0
                    # print('max reached at row=' + str(row) + ' col=' + str(col))
                    # New Line SVG placeholder
                    if linetype == 'voice':
                        line_render += '\n<svg x=\"0" y=\"' + '%.2f' % y + '\" width=\"' + '%.2f' % self.SVG_line_width + '\" height=\"' + '%.2f' % self.SVG_text_height + '\" class=\"instrument-line line-' + str(
                            row) + '-' + str(sub_line) + '\">'
                        y += self.SVG_text_height + self.SVG_harp_spacings[1] / 2.0
                    else:
                        y += self.SVG_harp_spacings[1] / 2.0
                        line_render += '\n<svg x=\"0" y=\"' + '%.2f' % y + '\" width=\"' + '%.2f' % self.SVG_line_width + '\" height=\"' + '%.2f' % \
                                       self.SVG_harp_size[1] + '\" class=\"instrument-line line-' + str(
                            row) + '-' + str(sub_line) + '\">'
                        y += self.SVG_harp_size[1] + self.SVG_harp_spacings[1] / 2.0

                # INSTRUMENT RENDER
                instrument_render = instrument.render_in_svg(x, '%.2f' % (
                            100.0 * self.SVG_harp_size[0] / self.SVG_line_width) + '%', '100%', self.harp_AspectRatio)

                # REPEAT
                if instrument.get_repeat() > 1:
                    instrument_render += '\n<svg x=\"' + '%.2f' % (
                                x + self.SVG_harp_size[0]) + '\" y=\"0%\" class=\"repeat\" width=\"' + '%.2f' % (
                                                     100.0 * self.SVG_harp_size[
                                                 0] / self.SVG_line_width) + '%' + '\" height=\"100%\">'
                    instrument_render += '\n<text x=\"2%\" y=\"98%\" class=\"repeat\">x' + str(
                        instrument.get_repeat()) + '</text></svg>'
                    x += self.SVG_harp_spacings[0]

                line_render += instrument_render
                instrument_index += 1
                x += self.SVG_harp_size[0] + self.SVG_harp_spacings[0]

            song_render += line_render
            song_render += '\n</svg>'  # Close line SVG

        song_render += '\n</svg>'  # Close song SVG
        svg_file.write(song_render)

        svg_file.write('\n</svg>')  # Close file SVG

        # Open new file
        if end_row < len(self.lines):
            filenum, file_path = self.write_svg(file_path0, css_mode, css_path, end_row, filenum + 1)

        return filenum, file_path

    def write_png(self, file_path0, start_row=0, filenum=0):
        global no_PIL_module

        if no_PIL_module == True:
            print('\n**** WARNING: PNG was not rendered because PIL module was not found. ****\n')
            return 0, ''

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

        if filenum > self.maxFiles:
            print('\nYour song is too long. Stopping at ' + str(self.maxFiles) + ' files.')
            return filenum, file_path0

        if filenum > 0:
            (file_base, file_ext) = os.path.splitext(file_path0)
            file_path = file_base + str(filenum) + file_ext
        else:
            file_path = file_path0

        # Determines png size as a function of the numer of chords per line
        self.set_png_harp_size()
        self.set_png_voice_size()
        harp_rescale = self.get_png_harp_rescale()
        song_render = Image.new('RGBA', self.png_size, self.png_color)

        # Horizontal line drawing, to be used several times later
        hr_line = Image.new('RGBA', (int(self.png_line_width), 3))
        draw = ImageDraw.Draw(hr_line)
        draw = draw.line(((0, 1), (self.png_line_width, 1)), fill=(150, 150, 150), width=1)

        x_in_png = int(self.png_margins[0])
        y_in_png = int(self.png_margins[0])

        if filenum == 0:

            fnt = ImageFont.truetype(self.png_font, self.png_title_font_size)
            h = self.get_png_text_height(fnt)
            title_header = Image.new('RGBA', (int(self.png_line_width), int(h)))
            draw = ImageDraw.Draw(title_header)
            draw.text((0, 0), self.title, font=fnt, fill=self.font_color)
            if harp_rescale != 1:
                title_header = title_header.resize(
                    (int(title_header.size[0] * harp_rescale), int(title_header.size[1] * harp_rescale)),
                    resample=Image.LANCZOS)
            song_render = trans_paste(song_render, title_header, (int(x_in_png), int(y_in_png)))
            y_in_png += h * 2 * harp_rescale

            for i in range(len(self.headers[0])):
                fnt = ImageFont.truetype(self.png_font, self.png_font_size)
                h = self.get_png_text_height(fnt)
                header = Image.new('RGBA', (int(self.png_line_width), int(h)))
                draw = ImageDraw.Draw(header)
                draw.text((0, 0), self.headers[0][i] + ' ' + self.headers[1][i], font=fnt, fill=self.font_color)
                if harp_rescale != 1:
                    header = header.resize((int(header.size[0] * harp_rescale), int(header.size[1] * harp_rescale)),
                                           resample=Image.LANCZOS)
                song_render = trans_paste(song_render, header, (int(x_in_png), int(y_in_png)))
                y_in_png += h * 2 * harp_rescale
        else:
            fnt = ImageFont.truetype(self.png_font, self.png_font_size)
            h = self.get_png_text_height(fnt)
            title_header = Image.new('RGBA', (int(self.png_line_width), int(h)))
            draw = ImageDraw.Draw(title_header)
            draw.text((0, 0), self.title + '(page ' + str(filenum + 1) + ')', font=fnt, fill=self.font_color)
            if harp_rescale != 1:
                title_header = title_header.resize(
                    (int(title_header.size[0] * harp_rescale), int(title_header.size[1] * harp_rescale)),
                    resample=Image.LANCZOS)
            song_render = trans_paste(song_render, title_header, (int(x_in_png), int(y_in_png)))
            y_in_png += 2 * h + self.png_harp_spacings[1]

        ysong = y_in_png
        instrument_index = 0
        end_row = len(self.lines)

        # Creating a new song image, located at x_in_song, yline_in_song
        xline_in_song = x_in_png
        yline_in_song = ysong
        for row in range(start_row, end_row):

            line = self.get_line(row)
            linetype = line[0].get_type()
            ncols = len(line)
            nsublines = int(1.0 * ncols / self.maxIconsPerLine)  # to be changed

            if linetype.lower() == 'voice':
                ypredict = yline_in_song + (self.png_lyric_size[1] + self.png_harp_spacings[1] / 2.0) * (
                            nsublines + 1) + self.png_harp_spacings[1] / 2.0
            else:
                ypredict = yline_in_song + (self.png_harp_size[1] + self.png_harp_spacings[1]) * (nsublines + 1) + \
                           self.png_harp_spacings[1] / 2.0

            if ypredict > (self.png_size[1] - self.png_margins[1]):
                end_row = row
                break  # Bottom of image is reached, pausing line rendering

            sub_line = 0
            # Line
            if linetype.lower() == 'voice':
                line_render = Image.new('RGBA', (int(self.png_line_width), int(self.png_lyric_size[1])), self.png_color)
            else:
                # Dividing line
                yline_in_song += self.png_harp_spacings[1] / 4.0
                song_render.paste(hr_line, (int(xline_in_song), int(yline_in_song)))
                yline_in_song += hr_line.size[1] + self.png_harp_spacings[1] / 2.0

                line_render = Image.new('RGBA', (int(self.png_line_width), int(self.png_harp_size[1])), self.png_color)

            # Creating a new instrument image, starting at x=0 (in line) and y=0 (in line)
            x = 0
            y = 0
            for col in range(ncols):

                instrument = self.get_instrument(row, col)
                instrument.set_index(instrument_index)

                # Creating a new line if max number is exceeded
                if x + self.png_harp_size[0] + self.png_harp_spacings[0] / 2.0 > self.png_line_width:
                    x = 0
                    song_render = trans_paste(song_render, line_render, (int(xline_in_song), int(yline_in_song)))
                    yline_in_song += line_render.size[1] + self.png_harp_spacings[1] / 2.0
                    if linetype.lower() != 'voice':
                        yline_in_song += self.png_harp_spacings[1] / 2.0

                    sub_line += 1
                    # print('max reached at row=' + str(row) + ' col=' + str(col))
                    # New Line
                    if linetype.lower() == 'voice':
                        line_render = Image.new('RGBA', (int(self.png_line_width), int(self.png_lyric_size[1])),
                                                self.png_color)
                    else:
                        line_render = Image.new('RGBA', (int(self.png_line_width), int(self.png_harp_size[1])),
                                                self.png_color)

                # INSTRUMENT RENDER
                instrument_render = instrument.render_in_png(harp_rescale)
                line_render = trans_paste(line_render, instrument_render, (int(x), int(y)))
                    
                x += max(self.png_harp_size[0],instrument_render.size[0])

                # REPEAT
                if instrument.get_repeat() > 1:
                    repeat_im = instrument.get_repeat_png(self.png_harp_spacings[0], harp_rescale)
                    line_render = trans_paste(line_render, repeat_im,
                                              (int(x), int(y + self.png_harp_size[1] - repeat_im.size[1])))
                    x += max(repeat_im.size[0], self.png_harp_spacings[0])
                else:
                    x += self.png_harp_spacings[0]

                instrument_index += 1

            song_render = trans_paste(song_render, line_render,
                                      (int(xline_in_song), int(yline_in_song)))  # Paste line in song
            yline_in_song += line_render.size[1] + self.png_harp_spacings[1] / 2.0
            if linetype.lower() != 'voice':
                yline_in_song += self.png_harp_spacings[1] / 2.0

        song_render.save(file_path, dpi=self.png_dpi, compress_level=self.png_compress)

        # Open new file
        if end_row < len(self.lines):
            filenum, file_path = self.write_png(file_path0, end_row, filenum + 1)

        return filenum, file_path

    def write_midi(self, file_path):
        global no_mido_module

        if no_mido_module == True:
            print('\n**** WARNING: MIDI was not created because mido module was not found. ****\n')
            return ''

        mid = mido.MidiFile(type=0)
        track = mido.MidiTrack()
        mid.tracks.append(track)

        try:
            tempo = mido.bpm2tempo(self.midi_bpm)
            track.append(mido.MetaMessage('set_tempo', tempo=tempo))
        except ValueError:
            print('Warning: invalid tempo passed to MIDI renderer. Using 120 bpm instead.')
            tempo = mido.bpm2tempo(120)
            track.append(mido.MetaMessage('set_tempo', tempo=tempo))

        sec = mido.second2tick(1, ticks_per_beat=mid.ticks_per_beat, tempo=tempo)  # 1 second in ticks
        note_ticks = self.midi_note_duration * sec * 120 / self.midi_bpm  # note duration in ticks

        try:
            track.append(mido.MetaMessage('key_signature', key=self.midi_key))
        except ValueError:
            print('Warning: invalid key passed to MIDI renderer. Using C instead.')
            track.append(mido.MetaMessage('key_signature', key='C'))
        try:
            track.append(mido.Message('program_change', program=self.midi_instrument, time=0))
        except ValueError:
            print('Warning: invalid instrument passed to MIDI renderer. Using piano instead.')
            track.append(mido.Message('program_change', program=1, time=0))

        for line in self.lines:
            if len(line) > 0:
                if line[0].get_type() != 'voice':
                    instrument_index = 0
                    for instrument in line:
                        instrument.set_index(instrument_index)
                        instrument_render = instrument.render_in_midi(note_duration=note_ticks,
                                                                      music_key=self.music_key)
                        for i in range(0, instrument.get_repeat()):
                            for note_render in instrument_render:
                                track.append(note_render)
                            instrument_index += 1

        mid.save(file_path)

        return file_path
