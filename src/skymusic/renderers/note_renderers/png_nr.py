from skymusic.resources import Resources
from skymusic.modes import GamePlatform, GamepadLayout
from . import note_renderer


try:
    from PIL import Image

    no_PIL_module = False
except (ImportError, ModuleNotFoundError):
    no_PIL_module = True


class PngNoteRenderer(note_renderer.NoteRenderer):

    def __init__(self, platform_name=GamePlatform.get_default().get_name(), gamepad=None):
        self.platform_name = platform_name
        self.gamepad = gamepad
        self.png_max_quavers = Resources.PNG_SETTINGS['png_max_quavers']
        self.rows_names = Resources.PNG_SETTINGS['row_names']
        self.png_size = None


    def set_png_size(self):
        """Retrieves the original size of the .png image of a highlighted note"""
        if self.png_size is None:
            self.png_size = Image.open(Resources.PNGS[self.platform_name][Resources.PNG_SETTINGS['typical_notes'][self.platform_name]]).size

    def get_png_size(self):
        """Returns the original size of the .png image of a note"""
        if self.png_size is None:
            self.set_png_size()
        return self.png_size

    def get_dead_png(self):
        """Renders a PNG of a grey note placeholder, in case we want to display an empty harp when it is broken, instead of a central question mark"""
        if self.gamepad:
            Image.open(Resources.PNGS[self.platform_name]['blank'])
        else:
            Image.open(Resources.PNGS[self.platform_name]['dead-note'])
            

    def get_unhighlighted_png(self, coord):
        """Renders a PNG of a colored note placeholder, when the note at coord is not part of the chord"""
        
        if self.gamepad:
            png_key = "blank"
        else:
            row_name = self.rows_names[coord[0]]
            png_key = f"{row_name}-unhighlighted"
            
        
        try:
            note_png = Resources.PNGS[self.platform_name][png_key]
        except KeyError:
            print(f"\n***ERROR: Could not find '{png_key}' note image in PNGS['{self.platform_name}'].")
            return None
        else:
            return Image.open(note_png)
         
        
    def get_mobile_png(self, aspect, coord, highlighted_frames):
                
        if highlighted_frames[0] == 0:
            row_name = self.rows_names[coord[0]]
            try:
                note_png = Resources.PNGS[self.platform_name][f"{row_name}-{aspect}"]        
            except KeyError:
                print(f"\n***ERROR: Could not find '{row_name}-{aspect}' in PNGS['{self.platform_name}'].")
                note_png = None    
        else:
            num = min(highlighted_frames[0], self.png_max_quavers)
            try:
                note_png = Resources.PNGS[self.platform_name][f"{aspect}-highlighted-{num}"]
            except KeyError:
                print(f"\n***ERROR: Could not find '{aspect}-highlighted-{num}' in PNGS['{self.platform_name}'].")
                note_png = None
        
        return Image.open(note_png) if note_png else None


    def get_gamepad_png(self, button):
        
        try:
            note_png = Resources.PNGS[self.platform_name][button]        
        except KeyError:
            print(f"\n***ERROR: Could not find 'button' in PNGS[{self.platform_name}].")
            note_png = None            
        
        return Image.open(note_png) if note_png else None
    

    def render(self, note, rescale=1.0, note_parser=None):
        
        note_coord = note.get_coord()

        if not note.instrument.get_is_broken() and not note.instrument.get_is_silent():
            if not note.is_highlighted():
                # Draws a small button (will be colored thanks to CSS)
                png_render = self.get_unhighlighted_png(note_coord)
            else:
                # Draws an highlighted note
                if not self.gamepad:
                    note_aspect = self.get_aspect(note)
                    highlighted_frames = note.get_highlighted_frames()
                    png_render = self.get_mobile_png(note_aspect, note_coord, highlighted_frames)
                else:
                    note_button = note_parser.get_note_from_coord(note_coord)
                    png_render = self.get_gamepad_png(note_button)
                    
        else:
            png_render = self.get_dead_png()

        if rescale != 1 and rescale > 0:
            png_render = png_render.resize((round(png_render.size[0] * rescale), round(png_render.size[1] * rescale)),
                                             resample=Image.LANCZOS)

        return png_render


