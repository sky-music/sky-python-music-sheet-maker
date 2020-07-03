import re, io
from . import song_renderer
from src.skymusic.renderers.instrument_renderers.ascii_ir import AsciiInstrumentRenderer
from src.skymusic.resources import Resources


class AsciiSongRenderer(song_renderer.SongRenderer):

    def __init__(self, locale=None):
        
        super().__init__(locale) 
        
    def write_buffers(self, song, render_mode):

        meta = song.get_meta()
        ascii_buffer = io.StringIO()

        note_parser = render_mode.get_note_parser(locale=self.locale)
        instrument_renderer = AsciiInstrumentRenderer(self.locale)
        
        ascii_buffer.write(f"{Resources.COMMENT_DELIMITER}{meta['title'][1]}\n")

        for k in meta:
            if k != 'title':
                ascii_buffer.write(f"{Resources.COMMENT_DELIMITER}{meta[k][0]}{meta[k][1]}\n")

        if render_mode.get_is_chromatic():
            ascii_buffer.write(Resources.COMMENT_DELIMITER+'\nCAUTION: Conversion to a text file with a song key different from C (do, 1) is not supported yet. We assumed it was C.')
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
                    instrument_render += Resources.REPEAT_INDICATOR + str(repeat)
                line_render += instrument_render + re.sub('\\\\s', ' ', Resources.ICON_DELIMITER)
                line_render = line_render.rstrip(Resources.ICON_DELIMITER)
                instrument_index += 1
            song_render += '\n' + line_render

        ascii_buffer.write(song_render)
        ascii_buffer.seek(0)

        return [ascii_buffer]

