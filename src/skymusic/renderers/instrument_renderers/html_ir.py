#import os
#import io
from . import instrument_renderer
from src.skymusic.renderers.note_renderers.html_nr import HtmlNoteRenderer

class HtmlInstrumentRenderer(instrument_renderer.InstrumentRenderer):
    
    def __init__(self, locale=None):
        super().__init__(locale)

    def render_harp(self, instrument):
        """
        Renders the Instrument in HTML
        """
        harp_silent = instrument.get_is_silent()
        harp_broken = instrument.get_is_broken()

        note_renderer = HtmlNoteRenderer()

        if harp_broken:
            class_suffix = " broken"
        elif harp_silent:
            class_suffix = " silent"
        else:
            class_suffix = ""

        harp_render = f'<table class="harp harp-{instrument.get_index()}{class_suffix}">'

        for row in range(instrument.get_row_count()):

            harp_render += '<tr>'
            for col in range(instrument.get_column_count()):
                note = instrument.get_note_from_position((row, col))
                note_render = note_renderer.render(note)                
                harp_render += f'<td>{note_render}</td>'
            harp_render += '</tr>'

        harp_render += '</table>'

        if instrument.get_repeat() > 1:
            harp_render += (f'<table class="harp-{instrument.get_index()} repeat">'
                            f'<tr><td>x{instrument.get_repeat()}</td></tr>'
                            f'</table>')

        return harp_render

    def render_voice(self, instrument):
        """Renders the lyrics text in HTML inside an invisible table"""
        chord_render = f'<table class="voice"><tr><td>{instrument.lyric}</td></tr></table>'
        return chord_render
