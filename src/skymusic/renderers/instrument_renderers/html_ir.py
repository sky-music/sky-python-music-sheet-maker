#import re
from . import instrument_renderer
#from skymusic.resources import Resources
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
        lyric = instrument.get_lyric()
        emphasis = instrument.emphasis
        
        if emphasis:
            lyric = f'<{emphasis}>'+lyric+f'</{emphasis}>'
        
        voice_render = f'<div class="lyrics">{lyric}</div>'
        return voice_render

    def render_ruler(self, ruler):
        """Renders the markdown specials"""
        code = ruler.get_code()
        if code == '__':
            hr_render = '<hr class="solid" />'
        elif code == '--':
            hr_render = '<hr class="dashed" />'            
        elif code == '==':    
            hr_render = '<hr class="double" />'
        #TODO : add text below if there is text
        text = ruler.get_text()
        if text:
            emphasis = ruler.get_emphasis()
            hr_render += f'<p><{emphasis}>'+text+f'</{emphasis}></p>'        
            
        return hr_render
        
    def render_layer(self,*args,**kwargs):
        return self.render_ruler(*args,**kwargs)        
        
