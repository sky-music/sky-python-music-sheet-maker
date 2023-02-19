from . import note_renderer

class SvgNoteRenderer(note_renderer.NoteRenderer):

    def __init__(self, gamepad=None):
        super().__init__()
        self.gamepad=gamepad

    def get_silent_svg(self, xs="0%", ys="0%", widths="10%"):
        return f'<use xlink:href="#silent" x="{xs}" y="{ys}" width="{widths}" height="{widths}" />'

    def get_nonote_svg(self):
        return ''

    def get_harpbroken_svg(self, xs="0%", ys="0%", widths="10%"):
        return f'<use xlink:href="#broken" x="{xs}" y="{ys}" width="{widths}" height="{widths}" />'

    def get_unhighlighted_svg(self, row_num, xs="0%", ys="0%", widths="10%"):
        return f'<use xlink:href="#d{row_num}" x="{xs}" y="{ys}" width="{widths}" height="{widths}" />'


    def render(self, note, xs="0%", ys="0%", widths="10%"):
        
        (row, col) = note.get_coord()
        try:
            highlighted_frames = note.get_highlighted_frames()
            if len(highlighted_frames) == 1 and highlighted_frames[0] == 0:
                highlighted_classes = [f'r{row+1 :d}']
            else:
                highlighted_classes = [f'q{frame :d}' for frame in highlighted_frames]
        except KeyError:  # highlighted_frames==[]: note is not highlighted
            highlighted_classes = []

        if note.instrument.get_is_broken() and ((row, col) == note.instrument.get_middle_coord()):           
            highlighted_classes = []
            # Draws a special symbol when harp is broken
            note_core_render = self.get_harpbroken_svg(xs, ys, widths)
            
        elif note.instrument.get_is_silent() and ((row, col) == note.instrument.get_middle_coord()):            
            highlighted_classes = []
            # Draws a special symbol when harp is silent
            note_core_render = self.get_silent_svg(xs, ys, widths)
            
        else:
            
            if note.instrument.get_is_broken():
                # Draws a small button (will be grey thanks to CSS)
                highlighted_classes = []
                note_core_render = self.get_nonote_svg()              
                
            elif note.instrument.get_is_silent():                
                # Draws a small button (will be grey thanks to CSS)
                highlighted_classes = []
                note_core_render = self.get_nonote_svg()               
                
            else:
                
                if len(highlighted_classes) == 0:                    
                    # Draws a small button (will be colored thanks to CSS)
                    note_core_render = self.get_unhighlighted_svg(f'{row+1 :d}', xs, ys, widths)                    
                    
                else:
                    # Draws an highlighted note
                    aspect = self.get_aspect(note)
                    note_core_render = self.get_svg(aspect, xs, ys, widths, highlighted_classes)
        
           
        svg_render = note_core_render

        return svg_render


    def get_svg(self, aspect, xs="0%", ys="0%", widths="10%", highlighted_classes=""):
        
        highlighted_classes_str = ' '.join(highlighted_classes).rstrip() 
        
        if aspect == 'circle':
            note_svg = (f'<use xlink:href="#note" x="{xs}" y="{ys}" class="{highlighted_classes_str}" width="{widths}" height="{widths}" />'
                        f'<use xlink:href="#crc" x="{xs}" y="{ys}" width="{widths}" height="{widths}" />')


        elif aspect == 'diamond': 
            note_svg = (f'<use xlink:href="#note" x="{xs}" y="{ys}" class="{highlighted_classes_str}" width="{widths}" height="{widths}" />'
                        f'<use xlink:href="#dmn" x="{xs}" y="{ys}" width="{widths}" height="{widths}" />')
            
        elif aspect == 'root':
            note_svg = (f'<use xlink:href="#note" x="{xs}" y="{ys}" class="{highlighted_classes_str}" width="{widths}" height="{widths}" />'
                        f'<use xlink:href="#crdm" x="{xs}" y="{ys}" width="{widths}" height="{widths}" />')
            
        else:
            note_svg = ''
              
        return note_svg
