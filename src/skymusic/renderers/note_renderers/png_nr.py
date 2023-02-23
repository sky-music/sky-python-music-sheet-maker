from skymusic.resources import Resources
from skymusic.modes import GamePlatform
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
        self.max_quavers = Resources.PNG_SETTINGS['max_quavers']
        self.row_names = Resources.PNG_SETTINGS['row_names']
        self.note_size = None


    def set_note_size(self):
        """Retrieves the original size of the .png image of a highlighted note"""
        if self.note_size is None:
            self.note_size = Image.open(Resources.PNGS[self.platform_name][Resources.PNG_SETTINGS['typical_notes'][self.platform_name]]).size

    def get_note_size(self, rescale=1):
        """Returns the original size of the .png image of a note"""
        if self.note_size is None:
            self.set_note_size()
        return (round(self.note_size[0]*rescale), round(self.note_size[1]*rescale))

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
            row_name = self.row_names[coord[0]]
            png_key = f"{row_name}-unhighlighted"
            
        
        try:
            note_png = Resources.PNGS[self.platform_name][png_key]
        except KeyError:
            print(f"\n***ERROR: Could not find '{png_key}' note image in PNGS['{self.platform_name}'].")
            return None
        else:
            return Image.open(note_png)
         
        
    def _get_mobile_png_(self, aspect, coord, highlighted_frames):
                
        if highlighted_frames[0] == 0:
            row_name = self.row_names[coord[0]]
            try:
                note_png = Resources.PNGS[self.platform_name][f"{row_name}-{aspect}"]        
            except KeyError:
                print(f"\n***ERROR: Could not find '{row_name}-{aspect}' in PNGS['{self.platform_name}'].")
                note_png = None    
        else:
            num = min(highlighted_frames[0], self.max_quavers)
            try:
                note_png = Resources.PNGS[self.platform_name][f"{aspect}-highlighted-{num}"]
            except KeyError:
                print(f"\n***ERROR: Could not find '{aspect}-highlighted-{num}' in PNGS['{self.platform_name}'].")
                note_png = None
        
        return Image.open(note_png) if note_png else None


    def _get_gamepad_png_(self, button):
        
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
                    png_render = self._get_mobile_png_(note_aspect, note_coord, highlighted_frames)
                else:
                    note_button = note_parser.get_note_from_coord(note_coord)
                    png_render = self._get_gamepad_png_(note_button)
                    
        else:
            png_render = self.get_dead_png()

        if rescale != 1 and rescale > 0:
            png_render = png_render.resize((round(png_render.size[0] * rescale), round(png_render.size[1] * rescale)),
                                             resample=Image.LANCZOS)

        return png_render







