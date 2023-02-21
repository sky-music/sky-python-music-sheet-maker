from . import note_renderer

class HtmlNoteRenderer(note_renderer.NoteRenderer):

    def __init__(self):
        
        pass

    def get_silentsymbol_svg(self):
        return '<silence></silence>'

    def get_nonote_svg(self):
        return '<crc class="n"></crc>'

    def get_dead_svg(self):
        return '<dn></dn>'

    def get_harpbroken_svg(self):
        return '<text x="45.4" y="81" class="broken">?</text>'

    def get_unhighlighted_svg(self, row_num):
        return f"<d{row_num}></d{row_num}>"

    def render(self, note, x=0, y=0, width=None):
        
        (row, col) = note.get_position()
        try:
            highlighted_frames = note.get_highlighted_frames()
            if len(highlighted_frames) == 1 and highlighted_frames[0] == 0:
                highlighted_classes = [f'r{row+1 :d}']
            else:
                highlighted_classes = [f'q{frame :d}' for frame in highlighted_frames]
        except KeyError:  # highlighted_frames==[]: note is not highlighted
            highlighted_classes = []

        if note.instrument.get_is_broken() and ((row, col) == note.get_middle_position()):
            highlighted_classes = []
            # Draws a special symbol when harp is broken
            note_core_render = self.get_harpbroken_svg()
            
        elif note.instrument.get_is_silent() and ((row, col) == note.get_middle_position()):
            highlighted_classes = []
            # Draws a special symbol when harp is silent
            note_core_render = self.get_silentsymbol_svg()
            
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
                    note_core_render = self.get_unhighlighted_svg(f'{row+1 :d}')                    
                    
                else:
                    # Draws an highlighted note
                    aspect = self.get_aspect(note)
                    note_core_render = self.get_svg(aspect, highlighted_classes)
        
           
        svg_render = note_core_render

        return svg_render


    def get_svg(self, aspect, highlighted_classes):
        
        highlighted_classes_str = ' '.join(highlighted_classes).rstrip() 
        
        if aspect == 'circle':
            note_svg = (f'<crc class="{highlighted_classes_str}"></crc>')

        elif aspect == 'diamond': 
            note_svg = (f'<dmn class="{highlighted_classes_str}"></dmn>')
            
        elif aspect == 'root':
            note_svg = (f'<crdm class="{highlighted_classes_str}"></crdm>')
            
        else:
            note_svg = ''
              
        return note_svg