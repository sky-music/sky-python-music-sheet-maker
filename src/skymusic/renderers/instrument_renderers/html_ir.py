from . import instrument_renderer
from skymusic.renderers.note_renderers.html_nr import HtmlNoteRenderer

class HtmlInstrumentRenderer(instrument_renderer.InstrumentRenderer):
    
    def __init__(self, locale=None):
        super().__init__(locale)

    def render_harp(self, instrument):
        """
        Renders the Instrument in HTML
        """
        instr_silent = instrument.get_is_silent()
        instr_broken = instrument.get_is_broken()
        instr_type = instrument.get_type()

        note_renderer = HtmlNoteRenderer()

        if instr_broken:
            instr_state = "broken"
        elif instr_silent:
            instr_state = "silent"
        else:
            instr_state = ""
        
        css_class = " ".join(filter(None,["instr", instr_type, instr_state]))
        
        harp_render = f'<div class="{css_class}" id="instr-{instrument.get_index()}">'

        (rows, cols) = instrument.get_shape()

        for row in range(rows):
            #harp_render += '\n'
            for col in range(cols):
                note = instrument.get_note_from_position((row, col))
                note_render = note_renderer.render(note)   
                harp_render += note_render
        harp_render += '</div>' 

        if instrument.get_repeat() > 1:
            harp_render += (f'<div class="repeat">x{instrument.get_repeat()}</div>')

        return harp_render

    def render_voice(self, instrument):
        """Renders the lyrics text in HTML inside an invisible table"""
        voice_render = f'<div class="lyrics">{instrument.get_lyric()}</div>'
        return voice_render
