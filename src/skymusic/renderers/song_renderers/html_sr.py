import io, datetime
from . import song_renderer, ascii_sr
from skymusic.renderers.instrument_renderers.html_ir import HtmlInstrumentRenderer
from skymusic.resources import Resources
from skymusic.modes import CSSMode, RenderMode

class HtmlSongRenderer(song_renderer.SongRenderer):

    def __init__(self, locale=None, theme=Resources.get_default_theme()):
        
        super().__init__(locale)
        Resources.load_theme(theme)
        #self.HTML_note_width = '1em'

    def write_headers(self, html_buffer, song, css_mode):
        
        meta = song.get_meta()
        rel_css_path = Resources.rel_css_path
        script_buffers = Resources.script_buffers

        html_buffer.write(f'<!DOCTYPE html>'
                          f'\n<html xmlns:svg="http://www.w3.org/2000/svg" lang="{self.locale}">'
                          )
        utc_now = str(datetime.datetime.utcnow())
        html_buffer.write(f'\n<head>'
                          f'\n<meta charset="utf-8"/>'
                          f'\n<meta name="date.created" content="{utc_now}"/>'
                          f"\n<title>{meta['title'][1]}</title>"
                          )
        # Includes links to javascript that only appear online @ sky-music.github.io
        for script_url in Resources.online_scripts_urls:
            html_buffer.write(f'\n<script type="text/javascript" src="{script_url}"></script>')
        
        # Includes javascripts that can be run offline
        for script_buffer in script_buffers:
            html_buffer.write('\n<script type="text/javascript">\n')
            html_buffer.write(script_buffer.getvalue())
            html_buffer.write('</script>')

        if css_mode == CSSMode.EMBED:
            html_buffer.write('\n<style type="text/css">\n')
            html_buffer.write(Resources.CSS['common'].getvalue())
            html_buffer.write(Resources.CSS['html'].getvalue())
            html_buffer.write('\n</style>')
           
        elif css_mode == CSSMode.IMPORT:
            html_buffer.write('\n<style type="text/css">')
            html_buffer.write("@import url(\'%s\');</style>" % rel_css_path.replace('\\','/'))
        elif css_mode == CSSMode.XML:
            html_buffer.write(f'\n<link href="{rel_css_path}" rel="stylesheet" />')

        html_buffer.write(f'</head>'
                          f'\n<body>\n'
                          )
                
        html_buffer.write(f"<h1>{meta['title'][1]}</h1>")

        for k in meta:
            if k != 'title':
                html_buffer.write(f"\n<p><b>{meta[k][0]}</b>{meta[k][1]}</p>")
        
        html_buffer.write("\n<!-- Embedded video tag goes here (Youtube: share/embed/iframe) -->")
        
        return html_buffer


    def write_footer(self, html_buffer):
        
        html_buffer.write('\n</body>'
                          '\n</html>')
       
        return html_buffer        

    def write_ascii(self, html_buffer, song):
        
        ascii_buffers = ascii_sr.AsciiSongRenderer(self.locale).write_buffers(song, RenderMode.SKYASCII)
        html_buffer.write('\n<div id="ascii" style="display:none;" hidden>')
        for ascii_buffer in ascii_buffers:
            html_buffer.write('\n'+ascii_buffer.getvalue())
        html_buffer.write('\n</div>')       


    def write_buffers(self, song, css_mode=CSSMode.EMBED):    
        
        html_buffer = io.StringIO()

        self.write_headers(html_buffer, song, css_mode)
        self.write_ascii(html_buffer, song)

        html_buffer.write('\n<div id="transcript">')

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
                    instrument_render += '\n'
                    instrument_index += 1
                    line_render += instrument_render

                song_render += line_render

        html_buffer.write(song_render)
        html_buffer.write('\n</div>')

        self.write_footer(html_buffer)
        
        html_buffer.seek(0)

        return [html_buffer]
    
