from . import instrument_renderer
from skymusic.renderers.note_renderers.svg_nr import SvgNoteRenderer
from skymusic.modes import GamePlatform

class SvgInstrumentRenderer(instrument_renderer.InstrumentRenderer):
    
    def __init__(self, locale=None, platform_name=GamePlatform.get_default().get_name(), gamepad=None):
        super().__init__(locale)
        self.gamepad=gamepad
        self.platform_name = platform_name
        #Gaps, must end with V or H
        self.gamepad_gaps = {'note-gapH': 0.43, 'note-gapV': 0.4, 'quaver-gapH': 0.2, 'line-gapV': 2, 'pauseH': 0.7-0.43} #Relative to note size
        self.set_gp_note_size()

    def set_gp_note_size(self):
        self.gp_note_size = SvgNoteRenderer(platform_name=self.platform_name, gamepad=self.gamepad).get_gp_note_size()
        return self.gp_note_size

    def get_gp_note_size(self, absolute=True, rescale=1):
        '''Gets note size'''
        if self.gp_note_size is None: self.set_gp_note_size()
        if absolute:
            return (self.gp_note_size[0]*rescale, self.gp_note_size[1]*rescale)
        else:
            return (1, self.gp_note_size[1]/self.gp_note_size[0])

    def get_gamepad_gaps(self, absolute=True, rescale=1):
        '''Get horizontal and vertical spacings'''
        gp_note_size = self.get_gp_note_size(absolute=absolute, rescale=rescale)
        return {k:v*(gp_note_size[0] if k.endswith('H') else gp_note_size[1]) for k,v in self.gamepad_gaps.items()}

    def get_gamepad_size(self, instrument, absolute=True, rescale=1):
        '''Get typical size of a gamepad layout'''
        gp_note_size =  self.get_gp_note_size(absolute=absolute, rescale=rescale)
        
        num_buttons, num_frames = self.get_grid_size(instrument)
        
        if instrument.get_is_silent(): return (round(self.gamepad_gaps['pauseH']*gp_note_size[0]), round(gp_note_size[1]))
        
        return ( round((num_frames + self.gamepad_gaps['quaver-gapH']*(num_frames-1))*gp_note_size[0]),
                 round((num_buttons + self.gamepad_gaps['note-gapV']*(num_buttons-1))*gp_note_size[1]) )
                 
    def get_grid_size(self, instrument):
        
        num_buttons = max(1,instrument.get_skygrid().get_max_num_by_frame()) #rows
        num_frames = max(1,instrument.get_skygrid().get_num_frames()) # cols
        
        return (num_buttons, num_frames)

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
            
            text_render = (f'\n<text x="0%" y="75%" class="ruler text {class_suffix}">{text}</text>')        
            hr_render += text_render
        
        hr_render += '</svg>'            
        return hr_render


    def render_layer(self,*args,**kwargs):
        return self.render_ruler(*args,**kwargs)


    def render_repeat(self, instrument, x):
        
        repeat = instrument.get_repeat()
        
        if repeat == 1: return ''
            
        repeat_render = (f'\n<svg x="{x :.2f}" y="0%"'
                        f' width="{len(str(repeat)):d}em" height="100%">'
                                         )
        repeat_render += f'\n<text x="2%" y="{50 if self.gamepad else 98}%" class="repeat">x{repeat:d}</text></svg>'
            
        return repeat_render
        

    def render_voice(self, instrument, x, width: str, height: str, aspect_ratio=1):
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

    def _render_gamepad_broken_(self, instrument, x, harp_width, harp_height, grid_size):
        # The harp SVG container
        css_class = "gp instr broken"
        
        harp_render = f'<svg x="{x :.2f}" y="0" width="{harp_width}" height="{harp_height}" class="{css_class}" id="instr-{instrument.get_index()}">'
        
        nr = SvgNoteRenderer(platform_name=self.platform_name, gamepad=self.gamepad)
        
        harp_render += nr.get_broken_svg('0%', '0%', widths='100%', heights='100%')
        
        harp_render += '</svg>'
        
        return harp_render
        

    def _render_gamepad_pause_(self, instrument, x, harp_width, harp_height, grid_size):
        
        # The harp SVG container
        css_class = "gp instr silent"
        
        harp_render = f'<svg x="{x :.2f}" y="0" width="{harp_width}" height="{harp_height}" class="{css_class}" id="instr-{instrument.get_index()}">'
        
        nr = SvgNoteRenderer(platform_name=self.platform_name, gamepad=self.gamepad)
        
        harp_render += nr.get_silent_svg('0%', '0%', widths='100%', heights='100%')
        
        harp_render += '</svg>'
        
        return harp_render
        

    def _render_gamepad_harp_(self, instrument, x, harp_width, harp_height, grid_size=(1,1)):
        
        if instrument.get_is_silent(): return self._render_gamepad_pause_(instrument, x, harp_width, harp_height, grid_size)
        
        if instrument.get_is_broken(): return self._render_gamepad_broken_(instrument, x, harp_width, harp_height, grid_size)
        
        note_renderer = SvgNoteRenderer(platform_name=self.gamepad.platform.get_name(),gamepad=self.gamepad)
        
        # Required to get gamepad button name from note coord in the Skygrid
        note_parser = self.gamepad.get_note_parser(locale=self.locale, shape=instrument.get_shape()) #Cannot be sooner because we need instrument shape
        
        # The harp SVG container
        css_class = "gp instr"
        
        harp_render = f'<svg x="{x :.2f}" y="0" width="{harp_width}" height="{harp_height}" class="{css_class}" id="instr-{instrument.get_index()}">'
        
        xn0 = 0
        yn0 = 0
        
        frames = instrument.get_skygrid().get_highlighted_frames()#cols
        num_frames = max(1, len(frames))
        num_buttons = max(1, instrument.get_skygrid().get_max_num_by_frame()) #rows
        
        #TODO: use both frames and grid size
        
        quaver_gap = self.get_gamepad_gaps(absolute=False)['quaver-gapH']
        row_gap = self.get_gamepad_gaps(absolute=False)['note-gapV']
        
        (note_width, note_height) = note_renderer.get_gp_note_size(absolute=False)
        
        max_frames, max_buttons = grid_size
        
        rel_note_height = 1/((max_buttons*note_height+(max_buttons-1)*row_gap))
        
        rel_note_width = rel_note_height*note_width/note_height
        
        rel_quaver_gap = quaver_gap*rel_note_width/note_width
        rel_row_gap = row_gap*rel_note_height/note_height
        
        xn = xn0 #starts from left col
        # Render harp in vertical layout mode
        for ix, frame in enumerate(frames): # cols
            harp_render += '\n'
            coords = instrument.get_skygrid().get_highlighted_coords(frame)
            yn = yn0 #restarts from top row
            for iy, coord in enumerate(coords): #rows

                note = instrument.get_note_from_coord(coord)
                # NOTE RENDER
                if len(note.get_highlighted_frames()) > 0:  # Only paste highlighted notes  
                    harp_render += note_renderer.render(note, xs=f"{100*xn :.2f}%", ys=f"{100*yn :.2f}%", widths=f"{100*rel_note_width :.2f}%", heights=f"{100*rel_note_height :.2f}%", note_parser=note_parser)
    
                    yn += rel_note_height + rel_row_gap
                    
            if coords:
                xn += rel_note_width + rel_quaver_gap
            
        
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

        note_renderer = SvgNoteRenderer(platform_name=self.platform_name,gamepad=self.gamepad)

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
                harp_render += note_renderer.render(note, xs=f"{100*xn :.2f}%", ys=f"{100*yn :.2f}%", widths=f"{100*note_width :.2f}%", heights=f"{100*note_width :.2f}%")
                
        harp_render += '\n</svg>'

        return harp_render


