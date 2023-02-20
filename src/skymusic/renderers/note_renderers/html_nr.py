from . import note_renderer
#from skymusic.modes import GamePlatform

class HtmlNoteRenderer(note_renderer.NoteRenderer):

    def __init__(self, gamepad=None):
        super().__init__()
        self.gamepad = gamepad
        
    def get_silent_svg(self):
        return '<silence></silence>'
        
    def get_silent_gamepad_svg(self):
        return '<gpsilence class="gppause"></gpsilence>' #Same whatever the platform

    def get_nonote_svg(self):
        return '<crc class="n"></crc>'

    def get_nonote_gamepad_svg(self):
        return ''

    def get_dead_svg(self):
        return '<dn></dn>'

    def get_harpbroken_svg(self):
        return '<text x="45.4" y="81" class="broken">?</text>'

    def get_harpbroken_gamepad_svg(self):
        return '<text x="45.4" y="81" class="broken">?</text>'

    def get_unhighlighted_svg(self, row_num):
        return f"<d{row_num}></d{row_num}>"
        
    def get_unhighlighted_gamepad_svg(self):
        return "<gpblank></gpblank>"    

    def render(self, note, note_parser=None):
        
        gamepad = self.gamepad
        
        #if note has no coord then it's a filler for the gamepad vertical layout:
        if not note.get_coord() and gamepad:
            return self.get_unhighlighted_gamepad_svg()
        
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
            note_core_render = self.get_harpbroken_svg() if gamepad is None else self.get_harpbroken_gamepad_svg()
            
        elif note.instrument.get_is_silent() and ((row, col) == note.instrument.get_middle_coord()):
            highlighted_classes = []
            # Draws a special symbol when harp is silent
            note_core_render = self.get_silent_svg() if gamepad is None else self.get_silent_gamepad_svg() 
            
        elif note.instrument.get_is_broken():
                # Draws a small button (will be grey thanks to CSS)
                highlighted_classes = []
                note_core_render = self.get_nonote_svg() if not gamepad else self.get_nonote_gamepad_svg() 
                
        elif note.instrument.get_is_silent():                
            # Draws a small button (will be grey thanks to CSS)
            highlighted_classes = []
            note_core_render = self.get_nonote_svg() if not gamepad else self.get_nonote_gamepad_svg()
                
        else: #Instrument is OK
            # All notes have been muted
            if len(highlighted_classes) == 0:                    
                # Draws a small button (will be colored thanks to CSS)
                if not gamepad:
                    note_core_render = self.get_unhighlighted_svg(f'{row+1 :d}') 
                else:
                    note_core_render = self.get_unhighlighted_gamepad_svg()
                
            else: # Draws an highlighted note
                if not gamepad:
                    aspect = self.get_aspect(note)
                    note_core_render = self._get_mobile_svg_(aspect, highlighted_classes)
                else:
                    button = note_parser.get_note_from_coord((row,col))
                    note_core_render = self._get_gamepad_svg_(gamepad, button, highlighted_classes)
        
        return note_core_render


    def _get_mobile_svg_(self, aspect, highlighted_classes):
        
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


    def _get_gamepad_svg_(self, gamepad, button, highlighted_classes):
        
        #highlighted_classes_str = ' '.join(highlighted_classes).rstrip() 
        highlighted_classes_str = gamepad.platform.get_nickname()
        
        tag = gamepad.platform.get_nickname() + str(button)
        note_svg = (f'<{tag} class="{highlighted_classes_str}"></{tag}>')
                
        return note_svg

