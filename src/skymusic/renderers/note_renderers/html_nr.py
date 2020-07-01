from . import note_renderer, svg_nr

class HtmlNoteRenderer(note_renderer.NoteRenderer):

    def __init__(self):
        
        pass

    def render(self, note):

        return svg_nr.SvgNoteRenderer().render(note)
