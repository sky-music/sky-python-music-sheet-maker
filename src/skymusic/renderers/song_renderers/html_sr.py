import io
from . import song_renderer
from src.skymusic.renderers.instrument_renderers.html_ir import HtmlInstrumentRenderer
from src.skymusic.resources import Resources
from src.skymusic.modes import CSSMode

class HtmlSongRenderer(song_renderer.SongRenderer):

    def __init__(self, locale=None):
        
        super().__init__(locale)
        #self.HTML_note_width = '1em'

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
                print("\n***ERROR: could not open CSS file to embed it in HTML.")
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
                html_buffer.write(f"\n<p><b>{meta[k][0]}</b>{meta[k][1]}</p>")

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
        instrument_renderer = HtmlInstrumentRenderer(self.locale)
        
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
                    instrument_render = instrument_renderer.render(instrument)
                    instrument_render += ' '
                    instrument_index += 1
                    line_render += instrument_render

                song_render += line_render

        html_buffer.write(song_render)

        self.write_footer(html_buffer)
        
        html_buffer.seek(0)

        return [html_buffer]
    
