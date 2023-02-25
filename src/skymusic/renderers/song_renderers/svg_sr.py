import io, re
from . import song_renderer
#from skymusic import instruments
from skymusic.renderers.instrument_renderers.svg_ir import SvgInstrumentRenderer
from skymusic.modes import CSSMode, GamePlatform
from skymusic.resources import Resources


class SvgSongRenderer(song_renderer.SongRenderer):

    def __init__(self, locale=None, aspect_ratio=16/9.0, gamepad=None, theme=Resources.get_default_theme()):
        
        super().__init__(locale)
        platform = gamepad.platform if gamepad else GamePlatform.get_default()
        self.platform_name = platform.get_name()
        self.gamepad = gamepad
        
        if Resources.BYPASS_GAMEPAD_SVG:
            self.gamepad = None
            self.platform_name = GamePlatform.get_default().get_name()
        
        Resources.load_theme(theme, self.platform_name)

        self.aspect_ratio = aspect_ratio
        self.max_harps_line = round(Resources.SVG_SETTINGS['max_harps_line']*aspect_ratio/(16/9.0))
        self.max_gp_notes_line = round(Resources.SVG_SETTINGS['max_gp_notes_line']*aspect_ratio/(16/9.0))
        
        self.SVGviewPort = (0.0, 0.0, 750*self.aspect_ratio, 750.0)
        self.minDim = self.SVGviewPort[2] * 0.01
        self.SVGviewPort_margins = (13.0, 7.5)       
        self.line_width = self.SVGviewPort[2] - self.SVGviewPort_margins[0]
        
        self.pt2px = 96.0 / 72
        self.fontpt = Resources.SVG_SETTINGS['font_size']
        self.text_height = self.fontpt * self.pt2px  # In principle this should be in em
        self.rule_height = self.fontpt * self.pt2px*0.15
        self.layer_height = self.fontpt * self.pt2px
        self.maxFiles = Resources.MAX_NUM_FILES
        
        self.harp_rels_pacings = Resources.PNG_SETTINGS['harp_rel_spacings']# Fraction of the harp width that will be allocated to the spacing between harps
        self.gamepad_relspacings = self.set_gamepad_spacings(absolute=False) #Relative instrument spacing
        
        self.harp_width = max(self.minDim, (self.SVGviewPort[2] - self.SVGviewPort_margins[0]) / (
                1.0 * self.max_harps_line * (1 + self.harp_rels_pacings[0])))

        self.gamepad_rescale = 1
        self.gamepad_spacings = tuple()
        self.set_gamepad_rescale()
        #Absolute instrument spacing
        self.set_gamepad_spacings(rescale=self.gamepad_rescale)
        
        self.harp_relAspectRatio = Resources.SVG_SETTINGS['harp_aspect_ratio']/(5/3)
        #self.harp_AspectRatio = 1.455       
        self.set_harp_AspectRatio(5/3, self.harp_relAspectRatio)
        
        self.SVG_defs = self.load_svg_template()        


    def load_svg_template(self):
        '''Loads the symbols inside resources/svg/theme/template.svg '''
        svg_template = Resources.SVG[self.platform_name].getvalue()
        match = re.search("<defs[^>]*>(.*(?=</defs>))", svg_template, re.DOTALL)
        try:
            return match.group(1)
        except (TypeError, IndexError):
            return ""

    def set_gamepad_rescale(self):
        
        gp_note_width = max(self.minDim, (self.SVGviewPort[2] - self.SVGviewPort_margins[0]) / (
                1.0 * self.max_gp_notes_line * (1 + self.gamepad_relspacings[0])))

        note_size0 = SvgInstrumentRenderer(locale=self.locale, platform_name=self.platform_name, gamepad=self.gamepad).get_gp_note_size(absolute=True)        
        self.gamepad_rescale = min(self.max_gp_notes_line, max(0.1, gp_note_width/note_size0[0]))
  
        return self.gamepad_rescale

    def set_harp_AspectRatio(self, harp_AspectRatio, harp_relAspectRatio=1):
        
        self.harp_AspectRatio = harp_AspectRatio*harp_relAspectRatio
        self.harp_size = (self.harp_width, max(self.minDim, self.harp_width / self.harp_AspectRatio))
        self.harp_spacings = (
            self.harp_rels_pacings[0] * self.harp_width,
            self.harp_rels_pacings[1] * self.harp_width / self.harp_AspectRatio)
        self.nontonal_spacings =  (self.harp_size[0], self.harp_size[1]/4.0)
 
    def set_gamepad_spacings(self, absolute=True, rescale=1):
        
        instrument_renderer = SvgInstrumentRenderer(locale=self.locale, platform_name=self.platform_name, gamepad=self.gamepad)
        gaps = instrument_renderer.get_gamepad_gaps(absolute=absolute, rescale=rescale)
        self.gamepad_spacings = (gaps['note-gapH'], gaps['line-gapV'])
        self.nontonal_spacings = (gaps['note-gapH'], gaps['note-gapV'])
        return self.gamepad_spacings

    def get_instr_spacings(self):
        if self.gamepad is None:
            return self.harp_spacings
        else:
            return self.gamepad_spacings             
                     
                                                                  
    def get_voice_height(self):
        """Tries to predict the height of the lyrics text when rendered in SVG"""
        return self.fontpt * self.pt2px

    def write_headers(self, svg_buffer, filenum, song, css_mode):
         
        rel_css_path = Resources.rel_css_path
        meta = song.get_meta()                 
        # SVG/XML headers
        svg_buffer.write('<?xml version="1.0" encoding="utf-8" ?>')

        if css_mode == CSSMode.HREF:
            svg_buffer.write(f'\n<?xml-stylesheet href="{rel_css_path}" type="text/css" alternate="no" media="all"?>')

        svg_buffer.write(f'\n<svg baseProfile="full" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:ev="http://www.w3.org/2001/xml-events" xmlns:xlink="http://www.w3.org/1999/xlink"'
                         f' width="100%" height="100%"'
                         f' viewBox="{self.SVGviewPort[0] :.2f} {self.SVGviewPort[1] :.2f} {self.SVGviewPort[2] :.2f} {self.SVGviewPort[3] :.2f}" preserveAspectRatio="xMinYMin">')

        svg_buffer.write('\n<defs>')
        svg_buffer.write(self.SVG_defs) #SVG definitions to be reused: <symbol>, 
        if css_mode == CSSMode.EMBED:
            svg_buffer.write('\n<style type="text/css"><![CDATA[\n')
            svg_buffer.write(Resources.CSS['svg'].getvalue())
            svg_buffer.write('\n]]></style>')
        elif css_mode == CSSMode.IMPORT:
            svg_buffer.write('\n<style type="text/css">')
            svg_buffer.write("@import url(%s);</style></defs>" % rel_css_path.replace('\\','/'))
        else:
            pass
        svg_buffer.write('</defs>')
        svg_buffer.write(f"\n<title>{meta['title'][1]}-{filenum}</title>")        


    def write_buffers(self, song, css_mode=CSSMode.EMBED, start_row=0, start_col=0, buffer_list=None):

        if buffer_list is None:
            buffer_list = []
        if len(buffer_list) >= self.maxFiles:
            print(f"\n***WARNING: Your song is too long. Stopping at {self.maxFiles} files.")
            return buffer_list

        instrument_renderer = SvgInstrumentRenderer(self.locale,gamepad=self.gamepad)
        self.set_harp_AspectRatio(song.get_harp_aspect_ratio(), self.harp_relAspectRatio)
        #self.set_harp_AspectRatio(1.455)

        instrument_spacings = self.get_instr_spacings()
        nontonal_spacings = self.nontonal_spacings

        svg_buffer = io.StringIO()
        filenum = len(buffer_list)
        meta = song.get_meta()

        # Open file SVG and write standard SVG headers
        self.write_headers(svg_buffer, filenum, song, css_mode)             
       
        # Song metadata SVG container
        song_header = (f'\n<svg x="{self.SVGviewPort_margins[0] :.2f}" y="{self.SVGviewPort_margins[1] :.2f}"'
                       f' width="{self.line_width :.2f}" height="{(self.SVGviewPort[3] - self.SVGviewPort_margins[1]) :.2f}">'
                       )

        x = 0
        y = self.text_height  # Because the origin of text elements of the bottom-left corner

        if filenum == 0:
            song_header += f"\n<text x=\"{x :.2f}\" y=\"{y :.2f}\" class=\"title\">{meta['title'][1]}</text>"           
            
            for k in meta:
                if k != 'title':
                    y += 2 * self.text_height
                    song_header += f'\n<text x="{x :.2f}" y="{y :.2f}" class="headers">{meta[k][0]} {meta[k][1]}</text>'
                    
        else:
            song_header += f"\n<text x=\"{x :.2f}\" y=\"{y :.2f}\" class=\"title\">{meta['title'][1]} (page {(filenum + 1)})</text>"
        
        """
        # Dividing line after title
        y += self.text_height
        
        # Special code to check whether the next line is not a layer or rule drawing an horizontal line
        if song.get_num_lines() > 0:
            line = song.get_line(start_row)
            linetype = line[0].get_type().lower().strip()
            if linetype not in ('layer', 'ruler'):
                song_header += (f'\n<svg x="0" y="{y :.2f}" width="{self.line_width :.2f}" height="{(instrument_spacings[1] / 2.0) :.2f}">'
                                f'\n<line x1="0" y1="50%" x2="100%" y2="50%" class="sep" /> '
                                f'\n</svg>')
        """
        y += 2*self.text_height
        
        song_header += '\n</svg>'

        svg_buffer.write(song_header)

        # Song SVG container
        ysong = y
        song_render = (f'\n<svg x="{self.SVGviewPort_margins[0] :.2f}" y="{y :.2f}"'
                       f' width="{self.line_width :.2f}" height="{(self.SVGviewPort[3] - y) :.2f}" class="song">'
                      )
        y = 0  # Because we are nested in a new SVG
        x = 0
        instrument_index = 0
        num_lines = song.get_num_lines()
        end_row = num_lines
        end_col = 0
        ncols = self.max_harps_line
        page_break = False
        
        non_voice_row = 1
        prev_line0 = None
        
        for row in range(start_row, end_row):

            line = song.get_line(row)
            line0 = line[0]
            linetype = line0.get_type()
            if row > start_row:
                start_col = 0
            ncols = len(line) - start_col
            end_col = len(line)
            
            # Line SVG container
            if line0.get_is_textual():
                
                instr_size = (self.text_height*len(str(line0)), self.text_height)
                gp_grid_size = (1,1)
                song_render += (f'\n<svg x="0" y="{y :.2f}" width="{self.line_width :.2f}" height="{self.text_height :.2f}"'
                                f' class="line" id="line-{row}">')
                y += self.text_height + nontonal_spacings[1] / 2.0
                
            elif linetype == 'ruler':
                
                instr_size = (self.line_width, self.rule_height)
                gp_grid_size = (1,1)
                song_render += (f'\n<svg x="0" y="{y :.2f}" width="{self.line_width :.2f}" height="{3*self.rule_height :.2f}"'
                                f' class="line" id="line-{row}">')
                y += 3*self.rule_height + nontonal_spacings[1] / 2.0

            elif linetype == 'layer':
                
                instr_size = (self.line_width, self.layer_height)
                gp_grid_size = (1,1)
                song_render += (f'\n<svg x="0" y="{y :.2f}" width="{self.line_width :.2f}" height="{3*self.layer_height :.2f}"'
                                f' class="line" id="line-{row}">')
                y += 3*self.layer_height + nontonal_spacings[1] / 2.0
                
            elif line0.get_is_tonal(): #Tonal instrument
                
                if not self.gamepad:
                    instr_size = self.harp_size
                    gp_grid_size = tuple()
                else:
                    # Special calculation for gamepad
                    gp_instr_sizes = [instrument_renderer.get_gamepad_size(instr, rescale=self.gamepad_rescale) for instr in line]
                    
                    gp_grid_sizes = [instrument_renderer.get_grid_size(instr) for instr in line]
                    
                    gapH = self.gamepad_spacings[0]
                    lineW_predict = 0
                    instr_size = (0,0)
                    gp_grid_size = (1,1)
                    
                    for sz, grd in zip(gp_instr_sizes, gp_grid_sizes):
                        instr_size = (max(instr_size[0], sz[0]), max(instr_size[1], sz[1]))
                        gp_grid_size = (max(gp_grid_size[0], grd[0]), max(gp_grid_size[1], grd[1]))
                        lineW_predict += instr_size[0] + gapH
                        if lineW_predict > self.line_width:
                            break
                
                prev_linetype = 'ruler' if not prev_line0 else prev_line0.get_type()
                if prev_linetype not in ('ruler', 'layer'):
                    # Dividing line
                    y += nontonal_spacings[1] / 4.0
                    song_render += (f'\n<svg x="0" y="{y :.2f}" width="{self.line_width :.2f}" height="{(instrument_spacings[1] / 2.0) :.2f}">'
                                    f'\n<line x1="0" y1="50%" x2="100%" y2="50%" class="sep"/>'
                                    f'\n</svg>')
                    y += nontonal_spacings[1] / 4.0
                
                if prev_line0:
                    if line0.get_is_tonal():
                        y += instrument_spacings[1] / 2
                    else:
                        y += nontonal_spacings[1] / 2
                
                # Instrument-line opening
                if prev_line0:
                    if line0.get_is_tonal():
                        y += instrument_spacings[1] / 2
                    else:
                        y += nontonal_spacings[1] / 2
                
                song_render += (f'\n<svg x="0" y="{y :.2f}" width="{self.line_width :.2f}" height="{instr_size[1] :.2f}"'
                                f' class="line" id="line-{row}">')
                y += instr_size[1]
                if line0.get_is_tonal():
                    y += instrument_spacings[1] / 2
                else:
                    y += nontonal_spacings[1] / 2

            line_render = ''
            sub_line = 0
            x = 0
            
            for col in range(start_col, end_col):

                instrument = song.get_instrument(row, col)
                instrument.set_index(instrument_index)

                #1. Creating a new line if max number is exceeded
                if (int(1.0 * (col-start_col) / self.max_harps_line) - sub_line) > 0:
                    # Closes previous instrument-line SVG
                    line_render += '\n</svg>'
                    sub_line += 1
                    x = 0

                    # Creating a new line SVG
                    if line0.get_is_textual():
                        line_render += (f'\n<svg x="{x :.2f}" y="{y :.2f}" width="{self.line_width :.2f}" height="{self.text_height :.2f}"'
                                        f' class="line-{row}-{sub_line}">')
                        y += self.text_height + nontonal_spacings[1] / 2.0
                        
                    elif linetype == 'ruler':
                        line_render += (f'\n<svg x="{x :.2f}" y="{y :.2f}" width="{self.line_width :.2f}" height="{3*self.rule_height :.2f}"'
                                        f' class="line-{row}-{sub_line}">')
                        y += 3*self.rule_height + nontonal_spacings[1] / 2.0

                    elif linetype == 'layer':
                        line_render += (f'\n<svg x="{x :.2f}" y="{y :.2f}" width="{self.line_width :.2f}" height="{3*self.layer_height :.2f}"'
                                        f' class="line-{row}-{sub_line}">')
                        y += 3*self.layer_height + nontonal_spacings[1] / 2.0
                        
                    elif line0.get_is_tonal():
                        y += instrument_spacings[1] / 2.0
                        line_render += (f'\n<svg x="{x :.2f}" y="{y :.2f}" width="{self.line_width :.2f}" height="{instr_size[1] :.2f}"'
                                        f' class="line-{row}-{sub_line}">')
                        y += instr_size[1] + instrument_spacings[1] / 2.0

                #2. Page break
                ypredict = y + ysong
                
                if ypredict > (self.SVGviewPort[3] - self.SVGviewPort_margins[1]):
                    page_break = True
                    end_col = col
                    break

                #3. INSTRUMENT RENDER
                if not self.gamepad:
                    instrument_render = instrument_renderer.render(instrument, x, f"{(100.0 * instr_size[0] / self.line_width) :.2f}%", "100%", self.harp_AspectRatio)
                else:
                    instrument_render = instrument_renderer.render(instrument, x, f"{(100.0 * instr_size[0] / self.line_width) :.2f}%", "100%", gp_grid_size)

                #4. Repeat number
                if instrument.get_repeat() > 1:
                    #Todo: change that to give more information on widths, note wodths etc
                    line_render += instrument_renderer.render_repeat(instrument, x + instr_size[0], f'{(100.0 * instr_size[0] / self.line_width) :.2f}%')

                    x += instrument_spacings[0]

                line_render += "\n" + instrument_render
                instrument_index += 1
                x += instr_size[0] + instrument_spacings[0]

            #end loop on cols
            
            if num_lines > 10 and line0.get_is_tonal():
                line_num_str = f'{non_voice_row :d}'
                line_render += (f'\n<svg x="{x :.2f}" y="0%" width="{len(line_num_str)}em" height="100%">'
                               )
                               
                if self.gamepad:
                    num_ypos = '50%'
                else:
                    num_ypos = '98%'
                               
                line_render += f'\n<text x="2%" y="{num_ypos}" class="num">{line_num_str}</text>'
                line_render += '</svg>\n'
                x += self.text_height*3/2
                non_voice_row += 1
            
            line_render += '\n</svg>'  # Closes last instrument-line SVG
            song_render += line_render
            prev_line0 = line0
            
            if page_break:
                end_row = row
                break
        #End loop on rows  
              
        song_render += '\n</svg>'  # Close song SVG
        
        svg_buffer.write(song_render)
        svg_buffer.write('\n</svg>')  # Close file SVG

        svg_buffer.seek(0)
        buffer_list.append(svg_buffer)

        
        # Open new file
        if end_row < song.get_num_lines() or 0 < end_col < ncols:
            buffer_list = self.write_buffers(song, css_mode, end_row, end_col, buffer_list)

        return buffer_list


















