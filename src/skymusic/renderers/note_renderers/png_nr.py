import re
from skymusic.resources import Resources
from . import note_renderer

try:
    from PIL import Image

    no_PIL_module = False
except (ImportError, ModuleNotFoundError):
    no_PIL_module = True


class PngNoteRenderer(note_renderer.NoteRenderer):

    def __init__(self):
        self.max_num_quavers = len([Resources.PNGS[name] for name in Resources.PNGS if re.match(r'root\-highlighted\-[\d]+', name)])
        self.rows_names = ['A', 'B', 'C']
        self.png_size = None


    def set_png_size(self):
        """Retrieves the original size of the .png image of a highlighted note"""
        if self.png_size is None:
            self.png_size = Image.open(Resources.PNGS['A-root']).size

    def get_png_size(self):
        """Returns the original size of the .png image of a note"""
        if self.png_size is None:
            self.set_png_size()
        return self.png_size

    def get_dead_png(self):
        """Renders a PNG of a grey note placeholder, in case we want to display an empty harp when it is broken, instead of a central question mark"""
        return Image.open(Resources.PNGS['dead-note'])

    def get_unhighlighted_png(self, position):
        """Renders a PNG of a colored note placholder, when the note is note is unplayed"""
        row_name = self.rows_names[position[0]]
        
        try:
            note_png = Resources.PNGS[f"{row_name}-unhighlighted"]
            return Image.open(note_png)
        except AttributeError:
            print(f"\n***ERROR: Could not open {row_name}_unhighlighted note image.")
            return None
        
    def get_png(self, aspect, position, highlighted_frames):
                
        try:
            row_name = self.rows_names[position[0]]
            note_png = Resources.PNGS[f"{row_name}-{aspect}"]
            
            if highlighted_frames[0] == 0:
                return Image.open(note_png)
            else:
                num = min(highlighted_frames[0], self.max_num_quavers)
                return Image.open(Resources.PNGS[f"{aspect}-highlighted-{num}"])
        except (IndexError, AttributeError):
            print(f"\n***ERROR: Could not open {aspect} note image at row {row_name}.")
            return None


    def render(self, note, rescale=1.0):
        
        note_position = note.get_position()

        if not note.instrument_is_broken and not note.instrument_is_silent:
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


