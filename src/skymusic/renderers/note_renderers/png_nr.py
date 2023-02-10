from skymusic.resources import Resources
from . import note_renderer

try:
    from PIL import Image

    no_PIL_module = False
except (ImportError, ModuleNotFoundError):
    no_PIL_module = True


class PngNoteRenderer(note_renderer.NoteRenderer):

    def __init__(self, gamepad=None):
        self.gamepad = gamepad
        self.png_max_quavers = Resources.PNG_SETTINGS['png_max_quavers']
        self.rows_names = Resources.PNG_SETTINGS['row_names']
        self.png_size = None


    def set_png_size(self):
        """Retrieves the original size of the .png image of a highlighted note"""
        if self.png_size is None:
            self.png_size = Image.open(Resources.PNGS[Resources.PNG_SETTINGS['typical_note']]).size

    def get_png_size(self):
        """Returns the original size of the .png image of a note"""
        if self.png_size is None:
            self.set_png_size()
        return self.png_size

    def get_dead_png(self):
        """Renders a PNG of a grey note placeholder, in case we want to display an empty harp when it is broken, instead of a central question mark"""
        if not self.gamepad:
            Image.open(Resources.PNGS['dead-note'])
        else:
            Image.open(Resources.PNGS['blank'])

    def get_unhighlighted_png(self, position):
        """Renders a PNG of a colored note placeholder, when the note at position is not part of the chord"""
        row_name = self.rows_names[position[0]]
        
        try:
            note_png = Resources.PNGS[f"{row_name}-unhighlighted"]
            return Image.open(note_png)
        except AttributeError:
            print(f"\n***ERROR: Could not open '{row_name}-unhighlighted' note image.")
            return None
        
    def get_png(self, aspect, position, highlighted_frames):
        
        if highlighted_frames[0] == 0:
            row_name = self.rows_names[position[0]]
            try:
                note_png = Resources.PNGS[f"{row_name}-{aspect}"]        
            except KeyError:
                print(f"\n***ERROR: Could not find '{row_name}-{aspect}' in PNGS.")
                return None    
        else:
            num = min(highlighted_frames[0], self.png_max_quavers)
            try:
                note_png = Resources.PNGS[f"{aspect}-highlighted-{num}"]
            except KeyError:
                print(f"\n***ERROR: Could not find '{aspect}-highlighted-{num}' in PNGS.")
                return None   
        
        return Image.open(note_png) if note_png else None
    

    def render(self, note, rescale=1.0):
        
        note_position = note.get_position()

        if not note.instrument.get_is_broken() and not note.instrument.get_is_silent():
            if not note.is_highlighted():
                # Draws a small button (will be colored thanks to CSS)
                png_render = self.get_unhighlighted_png(note_position)
            else:
                # Draws an highlighted note                
                note_aspect = self.get_aspect(note)
                highlighted_frames = note.get_highlighted_frames()
                png_render = self.get_png(note_aspect, note_position, highlighted_frames)
        else:
            png_render = self.get_dead_png()

        if rescale != 1:
            png_render = png_render.resize((int(png_render.size[0] * rescale), int(png_render.size[1] * rescale)),
                                             resample=Image.LANCZOS)

        return png_render


