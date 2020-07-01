from . import note_renderer

class SvgNoteRenderer(note_renderer.NoteRenderer):

    def __init__(self):
        pass

    def get_silentsymbol_svg(self, highlighted_classes):
        return '<circle cx="45.4" cy="45.4" r="26" class="icon silent' + ' '.join(highlighted_classes).rstrip() + '"/>'

    def get_dead_svg(self, highlighted_classes):
        return '<circle cx="45.4" cy="45.4" r="12" class="icon broken' + ' '.join(highlighted_classes).rstrip() + '"/>'

    def get_harpbroken_svg(self, highlighted_classes):
        return '<text x="45.4" y="81" class="broken">?</text>'

    def get_unhighlighted_svg(self, highlighted_classes):
        return '<circle cx="45.4" cy="45.4" r="12" class="icon OFF' + ' '.join(highlighted_classes).rstrip() + '"/>'

    def render(self, note, x=0, y=0, width=None):
        try:
            highlighted_frames = note.get_highlighted_frames()
            highlighted_classes = [f'ON-{frame}' for frame in highlighted_frames]
        except KeyError:  # Note is not in the chord_skygrid dictionary: so it is not highlighted
            highlighted_classes = []

        if note.instrument_is_broken and (note.get_index() == note.get_middle_index()):
            
            highlighted_classes = []
            # Draws a special symbol when harp is broken
            class_unhighlighted = ''
            note_core_render = self.get_harpbroken_svg(highlighted_classes)
            
        elif note.instrument_is_silent and (note.get_index() == note.get_middle_index()):
            
            highlighted_classes = []
            # Draws a special symbol when harp is silent
            class_unhighlighted = ''
            note_core_render = self.get_silentsymbol_svg(highlighted_classes)
            
        else:
            
            if note.instrument_is_broken:
                # Draws a small button (will be grey thanks to CSS)
                highlighted_classes = []
                class_unhighlighted = ' broken'
                note_core_render = self.get_dead_svg(highlighted_classes)              
                
            elif note.instrument_is_silent:                
                # Draws a small button (will be grey thanks to CSS)
                highlighted_classes = []
                class_unhighlighted = ' silent'
                note_core_render = self.get_silentsymbol_svg(highlighted_classes)
                
                
            else:
                
                if len(highlighted_classes) == 0:                    
                    # Draws a small button (will be colored thanks to CSS)
                    class_unhighlighted = ''
                    note_core_render = self.get_unhighlighted_svg(highlighted_classes)                    
                    
                else:
                    # Draws an highlighted note
                    class_unhighlighted = ''
                    aspect = self.get_aspect(note)
                    note_core_render = self.get_svg(aspect, highlighted_classes)
        
        svgclass = self.get_aspect(note)
           
        svg_render = f'<svg x="{x}" y="{y}" class="{svgclass}{class_unhighlighted} button-{note.get_index()}"'
        
        if width:
            svg_render += f' width="{width}" height="{width}" viewBox="0 0 91 91">'
        else:
            svg_render += f' viewBox="0 0 91 91">'
        svg_render += note_core_render
        svg_render += '</svg>'

        return svg_render


    def get_svg(self, aspect, highlighted_classes):
        
        highlighted_classes_str = ' '.join(highlighted_classes).rstrip() 
        
        if aspect == 'circle':
            
            note_svg = (f'<path class="button {highlighted_classes_str}"'
                          f' d="M90.7 76.5c0 7.8-6.3 14.2-14.2 14.2H14.2C6.3 90.7 0 84.4 0 76.5V14.2C0 6.3 6.3 0 14.2 0h62.3c7.8 0 14.2 6.3 14.2 14.2V76.5z"/>'
                          f'<circle cx="45.4" cy="45.4" r="25.5" class="icon {highlighted_classes_str}"/>'
                          )

        elif aspect == 'diamond': 
                                
            note_svg = (f'<path class="button {highlighted_classes_str}"'
                           f' d="M90.7 76.5c0 7.8-6.3 14.2-14.2 14.2H14.2C6.3 90.7 0 84.4 0 76.5V14.2C0 6.3 6.3 0 14.2'
                           f' 0h62.3c7.8 0 14.2 6.3 14.2 14.2V76.5z"/>'
                           f'<rect x="22.6" y="22.7" transform="matrix(-0.7071 -0.7071 0.7071 -0.7071 45.3002 109.5842)"'
                           f' width="45.4" height="45.4" class="icon {highlighted_classes_str}"/> '
                          )     
        elif aspect == 'root':
            note_svg = (f'<path class="button {highlighted_classes_str}" d="M90.7 76.5c0 7.8-6.3 14.2-14.2 14.2H14.2C6.3 90.7 0 84.4 0'
                           f' 76.5V14.2C0 6.3 6.3 0 14.2 0h62.3c7.8 0 14.2 6.3 14.2 14.2V76.5z"/>'
                           f'<circle cx="45.5" cy="45.4" r="26" class="icon {highlighted_classes_str}"/>'
                           f'<rect x="19.5" y="19.3" transform="matrix(-0.7071 0.7071 -0.7071 -0.7071 109.7415 45.2438)"'
                           f' width="52" height="52" class="icon {highlighted_classes_str}"/>\n'
                           )
        else:
            note_svg = ''
              
        return note_svg
