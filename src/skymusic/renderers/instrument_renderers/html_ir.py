#import re
from . import instrument_renderer
#from skymusic.resources import Resources
from skymusic.renderers.note_renderers.html_nr import HtmlNoteRenderer

class HtmlInstrumentRenderer(instrument_renderer.InstrumentRenderer):
    
    def __init__(self, locale=None, gamepad=None):
        super().__init__(locale)
        self.gamepad = gamepad


    def _render_mobile_harp_(self, instrument):

        instr_repeat = instrument.get_repeat()
        (rows, cols) = instrument.get_shape()  

        note_renderer = HtmlNoteRenderer(gamepad=self.gamepad)

        if instrument.get_is_broken():
            instr_state = "broken"
        elif instrument.get_is_silent():
            instr_state = "silent"
        else:
            instr_state = ""
        
        css_class = " ".join(filter(None,["instr", instrument.get_type(), instr_state])) # e.g. instr drum silent
        
        harp_render = f'<div class="{css_class}" id="instr-{instrument.get_index()}">'

        for row in range(rows):
            #harp_render += '\n'
            for col in range(cols):
                note = instrument.get_note_from_coord((row, col))
                note_render = note_renderer.render(note)   
                if note_render is not None: harp_render += note_render
        harp_render += '</div>' 

        if instr_repeat > 1: harp_render += self.render_repeat(instr_repeat)      
        
        return harp_render


    def _render_gamepad_harp_(self, instrument):

        instr_silent = instrument.get_is_silent()
        instr_broken = instrument.get_is_broken()
        #instr_type = instrument.get_type()
        instr_repeat = instrument.get_repeat()
        (rows, cols) = instrument.get_shape()        

        note_renderer = HtmlNoteRenderer(gamepad=self.gamepad)

        if instr_broken:
            instr_state = "broken"
        elif instr_silent:
            instr_state = "silent"
        else:
            instr_state = ""

        # Required to get gamepad button name from note coord in the Skygrid
        note_parser = self.gamepad.get_note_parser(locale=self.locale, shape=(rows,cols)) #Cannot be sooner because we need instrument shape
        
        num_frames = instrument.get_skygrid().get_num_frames()
        num_buttons = instrument.get_skygrid().get_max_num_by_frame()
        if instr_silent:
            class_type = "gp grid11"
        elif instr_broken:
            class_type = "gp grid11"
        else:
            class_type = "gp grid{:0d}{:0d}".format(num_buttons, num_frames)
        
        css_class = " ".join(filter(None,["instr", class_type, instr_state])) # e.g. instr drum silent
        
        harp_render = f'<div class="{css_class}" id="instr-{instrument.get_index()}">'
        
        # Notes sorted by frames ; 1 row = 1 frame         
        html_grid = list(instrument.get_inverse_grid().values())
        
        if html_grid:
            # Fill with Nones
            for f,frame in enumerate(html_grid):
                # DEBUG
                if len(frame) > num_buttons:
                    raise ValueError(f"ERROR: more notes in frame {f} than in 'num_buttons'")
                html_grid[f] += [None]*(num_buttons-len(frame))
                        
            for row in range(0,num_buttons):
                for col in range(0, num_frames):
                    note_coord = html_grid[col][row] #yes, rows and cols are inverted
                    note = instrument.get_note_from_coord(note_coord)
                    
                    harp_render += note_renderer.render(note,note_parser)
                    
        if instr_silent or instr_broken: #Draws a blank or a red question mark
            note = instrument.get_note_from_coord(instrument.get_middle_coord())
            harp_render += note_renderer.render(note, note_parser)               
            
        harp_render += '</div>' 
        
        if instr_repeat > 1:
            if instr_silent:
                # In gamepad layout, pauses are repetead blanks
                harp_render = ''.join([harp_render]*instr_repeat)
            else:
                harp_render += self.render_repeat(instr_repeat)   
                
        return harp_render


    def render_harp(self, instrument):
        """
        Renders the Instrument in HTML
        """
        if self.gamepad is None: # Normal Grid
            harp_render = self._render_mobile_harp_(instrument)
        else : #Gamepad
            harp_render = self._render_gamepad_harp_(instrument)

        return harp_render


    def render_repeat(self, instr_repeat):
        return '<div class="{}repeat">x{:0d}</div>'.format('gp ' if self.gamepad else '', instr_repeat)

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
        text = ruler.get_text()
        if text:
            emphasis = ruler.get_emphasis()
            hr_render += f'<p><{emphasis}>'+text+f'</{emphasis}></p>'        
            
        return hr_render
        
    def render_layer(self,*args,**kwargs):
        return self.render_ruler(*args,**kwargs)        
        
