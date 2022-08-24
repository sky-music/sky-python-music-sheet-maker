import re, io
from . import song_renderer
from skymusic.renderers.instrument_renderers.ascii_ir import AsciiInstrumentRenderer
from skymusic.resources import Resources


class AsciiSongRenderer(song_renderer.SongRenderer):

    def __init__(self, locale=None):
        
        super().__init__(locale) 
        
    def write_buffers(self, song, render_mode):

        meta = song.get_meta()
        ascii_buffer = io.StringIO()

        start_octave = Resources.RENDERING_START_OCTAVE
        note_parser = render_mode.get_note_parser(locale=self.locale, start_octave=start_octave)
        
        instrument_renderer = AsciiInstrumentRenderer(self.locale)        
        ascii_buffer.write(f"{Resources.DELIMITERS['metadata']}{meta['title'][0]}{meta['title'][1]}" + "\n")

        for k in meta:
            if k != 'title':
                ascii_buffer.write(f"{Resources.DELIMITERS['metadata']}{meta[k][0]}{meta[k][1]}" + "\n")

        if render_mode.get_is_chromatic():
            ascii_buffer.write("\n"+f"{Resources.DELIMITERS['metadata']}CAUTION: Conversion to a text file with a song key different from C (do, 1) is not supported yet. We assumed it was C."+"\n")
            ascii_buffer.write(f"{Resources.DELIMITERS['metadata']}We assumed the first octave of the instrument was: {start_octave}\n")
        song_render = ''
        instrument_index = 0
        for line in song.get_lines():
            line_render = ''
            for instrument in line:
                instrument.set_index(instrument_index)
                #instrument_render = instrument.render_in_ascii(note_parser)
                instrument_render = instrument_renderer.render(instrument, note_parser)                
                repeat = instrument.get_repeat()
                if repeat > 1:
                    instrument_render += Resources.DELIMITERS['repeat'] + str(repeat)
                line_render += instrument_render + re.sub('\\\\s', ' ', Resources.DELIMITERS['icon'])
                line_render = line_render.rstrip(Resources.DELIMITERS['icon'])
                instrument_index += 1
            song_render += '\n' + line_render

        ascii_buffer.write(song_render)
        ascii_buffer.seek(0)

        return [ascii_buffer]

