from . import instrument_renderer
from skymusic.renderers.note_renderers.svg_nr import SvgNoteRenderer

class SvgInstrumentRenderer(instrument_renderer.InstrumentRenderer):
    
    def __init__(self, locale=None, gamepad=None):
        super().__init__(locale)
        self.gamepad=gamepad
        #Gaps, must end with V or H
        self.gamepad_gaps = {'note-gapH': 0.43, 'note-gapV': 0.4, 'quaver-gapH': 0.2, 'line-gapV': 2, 'pauseH': 0.7-0.43} #Relative to note size

    def render_ruler(self, ruler, x, width: str, height: str, aspect_ratio):
        
        hr_render = f'\n<svg x="{x :.2f}" y="0" width="100%" height="{height}" class="ruler" id="ruler-{ruler.get_index()}">\n'
        
        code = ruler.get_code()
        if code == '__':
            hr_render += '<line x1="0%" y1="0%" x2="100%" y2="0%" class="solid" />'
        elif code == '--':
            hr_render += '<line x1="0%" y1="0%" x2="100%" y2="0%" class="dashed" />'
            #hr_render = '<line x1="0%" y1="0%" x2="95%" y2="0%" style="stroke:gray;stroke-width:1;stroke-dasharray=\'10,10\'" />'
        elif code == '==':
            hr_render += '<line x1="0%" y1="5%" x2="100%" y2="5%" class="double" />'
            hr_render += '<line x1="0%" y1="15%" x2="100%" y2="15%" class="double" />'
                        
        text = ruler.get_text()
        emphasis = ruler.get_emphasis()
        if text:
            class_suffix = ''
            if emphasis == 'b':
                class_suffix = ' bold'
            elif emphasis == 'i':
                class_suffix = ' italic'
            elif emphasis != None:
                class_suffix = ' '+emphasis
            
            text_render = (f'\n<text x="0%" y="55%" class="ruler text {class_suffix}">{text}</text>')        
            hr_render += text_render
        
        hr_render += '</svg>'            
        return hr_render

    def render_layer(self,*args,**kwargs):
        return self.render_ruler(*args,**kwargs)

    def render_voice(self, instrument, x, width: str, height: str, aspect_ratio):
        """Renders the lyrics text in SVG"""
        
        lyric = instrument.get_lyric(strip_html=True)
    
        class_suffix = ''
        if instrument.emphasis == 'b':
            class_suffix = ' bold'
        elif instrument.emphasis == 'i':
            class_suffix = ' italic'
        elif instrument.emphasis != None:
            class_suffix = ' '+instrument.emphasis
        
        voice_render = (f'\n<svg x="{x :.2f}" y="0" width="100%" height="{height}" class="voice" id="voice-{instrument.get_index()}">'
                        f'\n<text x="0%" y="50%" class="voice{class_suffix}">{lyric}</text>'
                        f'</svg>')

        return voice_render

    def render_harp(self, *args, **kwargs):
        if self.gamepad is None: # Normal Grid
            harp_render = self._render_mobile_harp_(*args, **kwargs)
        else : #Gamepad
            harp_render = self._render_gamepad_harp_(*args, **kwargs)

        return harp_render

    def _render_gamepad_harp_(self, instrument, x, harp_width, harp_height, note_aspectRatio):
        #TODO
        harp_silent = instrument.get_is_silent()
        harp_broken = instrument.get_is_broken()
        
        note_renderer = SvgNoteRenderer(gamepad=self.gamepad)
        
        # Required to get gamepad button name from note coord in the Skygrid
        note_parser = self.gamepad.get_note_parser(locale=self.locale, shape=instrument.get_shape()) #Cannot be sooner because we need instrument shape
        
        # The harp SVG container
        css_class = "gp instr"
        
        harp_render = f'<svg x="{x :.2f}" y="0" width="{harp_width}" height="{harp_height}" class="{css_class}" id="instr-{instrument.get_index()}">'
        
        xn0 = 0
        yn0 = 0
        
        frames = instrument.get_skygrid().get_highlighted_frames()
        num_frames = max(1, len(frames))
        num_buttons = max(1, instrument.get_skygrid().get_max_num_by_frame())
        
        note_width = 1/num_frames
        note_height = (1/num_buttons)*note_aspectRatio
        
        xn = xn0
        # Render harp in vertical layout mode
        for ix, frame in enumerate(frames): # cols
            harp_render += '\n'
            coords = instrument.get_skygrid().get_highlighted_coords(frame)
            yn = yn0
            for iy, coord in enumerate(coords): #rows

                note = instrument.get_note_from_coord(coord)
                # NOTE RENDER
                if len(note.get_highlighted_frames()) > 0:  # Only paste highlighted notes  
                    harp_render += note_renderer.render(note, xs=f"{xn :.2f}%", ys=f"{yn :.2f}%", widths=f"{100*note_width :.2f}%", heights=f"{100*note_height :.2f}%", note_parser=note_parser)
    
                    yn += note_height
                    
                if coords:
                    xn += note_width
        
        harp_render += '</svg>'
        return harp_render

    def _render_mobile_harp_(self, instrument, x, harp_width, harp_height, aspect_ratio):
        """
        Renders the Instrument in SVG
        """
        instr_silent = instrument.get_is_silent()
        instr_broken = instrument.get_is_broken()
        instr_type = instrument.get_type()

        if instr_broken:
            instr_state = "broken"
        elif instr_silent:
            instr_state = "silent"
        else:
            instr_state = ""
            
        css_class = " ".join(filter(None,["instr", instr_type, instr_state]))

        note_renderer = SvgNoteRenderer(gamepad=self.gamepad)

        # The harp SVG container
        harp_render = f'<svg x="{x :.2f}" y="0" width="{harp_width}" height="{harp_height}" class="{css_class}" id="instr-{instrument.get_index()}">'

        # The harp rectangle with rounded edges
        #harp_render += f'<rect x="0.7%" y="0.7%" width="98.6%" height="98.6%" rx="7.5%" ry="{7.5 * aspect_ratio :.2f}%" class="{instrument.get_type()} {instrument.get_type()}-{instrument.get_index()}"/>'
        if not instr_broken and not instr_silent:
            harp_render += '\n<use xlink:href="#instr" />'

        for row in range(instrument.get_num_rows()):
            harp_render += '\n'
            for col in range(instrument.get_num_columns()):
                note = instrument.get_note_from_coord((row, col))
                
                rescale_ratio = (instrument.get_aspect_ratio()/(5/3))**2
                note_width = 0.21*rescale_ratio
                xn0 = 0.12*rescale_ratio
                yn0 = 0.15*rescale_ratio
                xn = xn0 + col * (1 - 2 * xn0) / (instrument.get_num_columns() - 1) - note_width / 2.0
                yn = yn0 + row * (1 - 2 * yn0*1.07) / (instrument.get_num_rows() - 1) - note_width / 2.0

                # NOTE RENDER
                harp_render += note_renderer.render(note, xs=f"{100*xn :.2f}%", ys=f"{100*yn :.2f}%", widths=f"{100*note_width :.2f}%")
                
        harp_render += '\n</svg>'

        return harp_render
