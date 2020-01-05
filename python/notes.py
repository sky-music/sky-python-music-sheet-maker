try:
    from PIL import Image

    no_PIL_module = False
except (ImportError, ModuleNotFoundError):
    no_PIL_module = True

try:
    import mido

    no_mido_module = False
except (ImportError, ModuleNotFoundError):
    no_mido_module = True


class Note:

    def __init__(self, instrument, pos=None):
        self.position = pos
        if pos is not None:
            self.index = (pos[0] * instrument.get_column_count()) + pos[1]
        else:
            self.index = None
        self.type = 'any_note'
        self.svgclass = 'any-note'
        self.chord_skygrid = instrument.get_chord_skygrid()
        self.instrument_type = instrument.get_type()
        self.harp_is_broken = instrument.get_is_broken()
        self.harp_is_silent = instrument.get_is_silent()
        self.row_count = instrument.get_row_count()
        self.column_count = instrument.get_column_count()
        self.A_root_png = 'elements/A-root.png'
        self.A_diamond_png = 'elements/A-diamond.png'
        self.A_circle_png = 'elements/A-circle.png'
        self.B_root_png = 'elements/B-root.png'
        self.B_diamond_png = 'elements/B-diamond.png'
        self.B_circle_png = 'elements/B-circle.png'
        self.C_root_png = 'elements/C-root.png'
        self.C_diamond_png = 'elements/C-diamond.png'
        self.C_circle_png = 'elements/C-circle.png'
        self.dead_png = 'elements/dead-note.png'
        self.dead_png = 'elements/dead-note.png'
        self.A_unhighlighted_png = 'elements/A-unhighlighted.png'
        self.B_unhighlighted_png = 'elements/B-unhighlighted.png'
        self.C_unhighlighted_png = 'elements/C-unhighlighted.png'
        self.root_highlighted_pngs = ['elements/root-highlighted-' + str(i) + '.png' for i in range(1, 8)]
        self.diamond_highlighted_pngs = ['elements/diamond-highlighted-' + str(i) + '.png' for i in range(1, 8)]
        self.circle_highlighted_pngs = ['elements/circle-highlighted-' + str(i) + '.png' for i in range(1, 8)]
        self.png_size = None

        self.midi_pitches = {'C': 60, 'C#': 61, 'Db': 61, 'D': 62, 'D#': 63, 'Eb': 63, 'E': 64, \
                             'F': 65, 'F#': 66, 'Gb': 66, 'G': 67, 'G#': 68, 'Ab': 68, 'A': 69, \
                             'A#': 70, 'Bb': 70, 'B': 71}
        self.midi_semitones = [0, 2, 4, 5, 7, 9, 11]  # May no longer be used when Western_scales is merged

    def get_position(self):
        """Return the note position as a tuple row/column"""
        return self.position

    def set_position(self, pos):
        """Sets the position tuple from row and column values"""
        self.position = pos
        self.index = (pos[0] * self.column_count) + pos[1]

    def get_index(self):
        """Returns the note index in Sky grid"""
        return self.index

    def get_middle_index(self):
        """Returns the index at the center of Sky grid"""
        return int(self.row_count * self.column_count / 2.0)

    def get_highlighted_frames(self):
        try:
            note_states = self.chord_skygrid[self.get_position()]  # Is note at 'position' highlighted or not
            highlighted_frames = [frame_index for frame_index in note_states.keys()]
        except KeyError:  # Note is not in the chord_skygrid dictionary: so it is not highlighted
            highlighted_frames = []
        return highlighted_frames

    def is_highlighted(self):
        highlighted_frames = self.get_highlighted_frames()
        if len(highlighted_frames) > 0:
            return True
        else:
            return False

    def __str__(self):
        return '<' + self.type + ' ' + str(self.index) + ', pos=' + str(self.position) + ', highlighted frames=' + str(
            self.get_highlighted_frames()) + '>'

    def get_svg(self, highlighted_classes):
        return ''

    def get_png(self, highlighted_frames):
        return

    def set_png_size(self):
        """Retrieves the original size of the .png image of a highlighted note"""
        if self.png_size is None:
            self.png_size = Image.open(self.A_root_png).size

    def get_png_size(self):
        """Returns the original size of the .png image of a note"""
        if self.png_size is None:
            self.set_png_size()
        return self.png_size

    def get_silentsymbol_svg(self, highlighted_classes):
        return '<circle cx=\"45.4\" cy=\"45.4\" r=\"26\" class=\"instrument-button-icon unhighlighted' + ' '.join(
            highlighted_classes).rstrip() + '\"/>'

    def get_dead_svg(self, highlighted_classes):
        return '<circle cx=\"45.4\" cy=\"45.4\" r=\"12\" class=\"instrument-button-icon unhighlighted' + ' '.join(
            highlighted_classes).rstrip() + '\"/>'

    def get_harpbroken_svg(self, highlighted_classes):
        return '<text x=\"45.4\" y=\"81\" class=\"broken\">?</text>'

    def get_unhighlighted_svg(self, highlighted_classes):
        return '<circle cx=\"45.4\" cy=\"45.4\" r=\"12\" class=\"instrument-button-icon unhighlighted' + ' '.join(
            highlighted_classes).rstrip() + '\"/>'

    def get_dead_png(self):
        """Renders a PNG of a grey note placeholder, in case we want to display an empty harp when it is broken"""
        return Image.open(self.dead_png)

    def get_unhighlighted_png(self):
        """Renders a PNG of a colored note placholder, when the note is note is unplayed"""
        if self.get_position()[0] == 0:
            return Image.open(self.A_unhighlighted_png)
        elif self.get_position()[0] == 1:
            return Image.open(self.B_unhighlighted_png)
        elif self.get_position()[0] == 2:
            return Image.open(self.C_unhighlighted_png)

    ####### Rendering methods
    def render_in_html(self, width='1em', x=0, y=0):
        try:
            highlighted_frames = self.get_highlighted_frames()
            highlighted_classes = ['highlighted-' + str(frame) for frame in highlighted_frames]
        except KeyError:  # Note is not in the chord_skygrid dictionary: so it is not highlighted
            highlighted_classes = []

        if self.harp_is_broken and (self.get_index() == self.get_middle_index()):
            highlighted_classes = []
            # Draws a special symbol when harp is broken
            note_render = '\n<svg x=\"' + str(x) + '\" y=\"' + str(
                y) + '\" class=\"' + self.svgclass + ' ' + self.instrument_type + '-button-' + str(
                self.get_index()) + '\" width=\"' + str(width) + '\" height=\"' + str(
                width) + '\" viewBox=\"0 0 91 91\">\n'
            note_render += self.get_harpbroken_svg(highlighted_classes)
            note_render += '</svg>'
        elif self.harp_is_silent and (self.get_index() == self.get_middle_index()):
            highlighted_classes = []
            # Draws a special symbol when harp is silent
            note_render = '\n<svg x=\"' + str(x) + '\" y=\"' + str(
                y) + '\" class=\"' + self.svgclass + ' ' + self.instrument_type + '-button-' + str(
                self.get_index()) + '\" width=\"' + str(width) + '\" height=\"' + str(
                width) + '\" viewBox=\"0 0 91 91\">\n'
            note_render += self.get_silentsymbol_svg(highlighted_classes)
            note_render += '</svg>'
        else:
            if self.harp_is_broken or self.harp_is_silent:
                # Draws a small button (will be grey thanks to CSS)
                highlighted_classes = []
                note_render = '\n<svg x=\"' + str(x) + '\" y=\"' + str(
                    y) + '\" class=\"' + self.svgclass + ' unhighlighted ' + self.instrument_type + '-button-' + str(
                    self.get_index()) + '\" width=\"' + str(width) + '\" height=\"' + str(
                    width) + '\" viewBox=\"0 0 91 91\">\n'
                note_render += self.get_dead_svg(highlighted_classes)
                note_render += '</svg>'
            else:
                if len(highlighted_classes) == 0:
                    # Draws a small button (will be colored thanks to CSS)
                    note_render = '\n<svg x=\"' + str(x) + '\" y=\"' + str(
                        y) + '\" class=\"' + self.svgclass + ' ' + self.instrument_type + '-button-' + str(
                        self.get_index()) + '\" width=\"' + str(width) + '\" height=\"' + str(
                        width) + '\" viewBox=\"0 0 91 91\">\n'
                    note_render += self.get_unhighlighted_svg(highlighted_classes)
                    note_render += '</svg>'
                else:
                    # Draws an highlighted note
                    note_render = '\n<svg x=\"' + str(x) + '\" y=\"' + str(
                        y) + '\" class=\"' + self.svgclass + ' ' + self.instrument_type + '-button-' + str(
                        self.get_index()) + '\" width=\"' + str(width) + '\" height=\"' + str(
                        width) + '\" viewBox=\"0 0 91 91\">\n'
                    note_render += self.get_svg(highlighted_classes)
                    note_render += '</svg>'

        return note_render

    def render_in_svg(self, width, x, y):
        return self.render_in_html(width, x, y)

    def render_in_png(self, rescale=1.0):

        highlighted_frames = self.get_highlighted_frames()

        if not self.harp_is_broken and not self.harp_is_silent:
            if len(highlighted_frames) == 0:
                # Draws a small button (will be colored thanks to CSS)
                note_render = self.get_unhighlighted_png()
            else:
                # Draws an highlighted note
                note_render = self.get_png(highlighted_frames)
        else:
            note_render = self.get_dead_png()

        if rescale != 1:
            note_render = note_render.resize((int(note_render.size[0] * rescale), int(note_render.size[1] * rescale)),
                                             resample=Image.LANCZOS)

        return note_render

    def render_in_midi(self, event_type, t=0, music_key='C'):
        """
            Starts or ends a MIDI note, assuming a chromatic scale (12 semitones)
        """
        octave = int(self.get_index() / 7)
        semi = self.midi_semitones[self.get_index() % 7]
        try:
            root_pitch = self.midi_pitches[music_key]
        except KeyError:
            print('Warning: Invalid music key passed to the MIDI renderer: assuming C instead.')
            root_pitch = self.midi_pitches['C']
        note_pitch = root_pitch + octave * 12 + semi

        if not self.harp_is_broken and not self.harp_is_silent:
            if len(self.get_highlighted_frames()) == 0:
                note_render = None
            else:
                note_render = mido.Message(event_type, channel=0, note=note_pitch, velocity=127, time=int(t))
        else:
            note_render = None

        return note_render


class NoteCircle(Note):

    def __init__(self, chord, pos):
        super().__init__(chord, pos)
        self.type = 'note_circle'
        self.svgclass = 'note-circle'

    def get_svg(self, highlighted_classes):
        note_render = '<path class="instrument-button ' + ' '.join(
            highlighted_classes).rstrip() + '" d="M90.7 76.5c0 7.8-6.3 14.2-14.2 14.2H14.2C6.3 90.7 0 84.4 0 76.5V14.2C0 6.3 6.3 0 14.2 0h62.3c7.8 0 14.2 6.3 14.2 14.2V76.5z"/>\n'
        note_render += '<circle cx="45.4" cy="45.4" r="25.5" class="instrument-button-icon ' + ' '.join(
            highlighted_classes).rstrip() + '"/>'
        return note_render

    def get_png(self, highlighted_frames):
        try:
            if highlighted_frames[0] == 0:
                if self.get_position()[0] == 0:
                    return Image.open(self.A_circle_png)
                elif self.get_position()[0] == 1:
                    return Image.open(self.B_circle_png)
                elif self.get_position()[0] == 2:
                    return Image.open(self.C_circle_png)
                else:
                    return None
            else:
                return Image.open(
                    self.root_highlighted_pngs[min(highlighted_frames[0], len(self.root_highlighted_pngs)) - 1])
        except:
            print('\nERROR: Could not open circle note image.')
            return None


class NoteDiamond(Note):

    def __init__(self, chord, pos):
        super().__init__(chord, pos)
        self.type = 'note_diamond'
        self.svgclass = 'note-diamond'

    def get_svg(self, highlighted_classes):
        note_render = '<path class="instrument-button ' + ' '.join(highlighted_classes).rstrip() + '" d="M90.7 76.5c0 7.8-6.3 14.2-14.2 14.2H14.2C6.3 90.7 0 84.4 0 76.5V14.2C0 6.3 6.3 0 14.2 0h62.3c7.8 0 14.2 6.3 14.2 14.2V76.5z"/>\n'
        note_render += '<rect x="22.6" y="22.7" transform="matrix(-0.7071 -0.7071 0.7071 -0.7071 45.3002 109.5842)" width="45.4" height="45.4" class="instrument-button-icon ' + ' '.join(highlighted_classes).rstrip() + '"/>'
        return note_render

    def get_png(self, highlighted_frames):
        try:
            if highlighted_frames[0] == 0:
                if self.get_position()[0] == 0:
                    return Image.open(self.A_diamond_png)
                elif self.get_position()[0] == 1:
                    return Image.open(self.B_diamond_png)
                elif self.get_position()[0] == 2:
                    return Image.open(self.C_diamond_png)
                else:
                    return None
            else:
                return Image.open(
                    self.root_highlighted_pngs[min(highlighted_frames[0], len(self.root_highlighted_pngs)) - 1])
        except:
            print('\nERROR: Could not open diamond note image.')
            return None


class NoteRoot(Note):

    def __init__(self, chord, pos):
        super().__init__(chord, pos)
        self.type = 'note_root'
        self.svgclass = 'note-root'

    def get_svg(self, highlighted_classes):
        note_render = '<path class="instrument-button ' + ' '.join(
            highlighted_classes).rstrip() + '" d="M90.7 76.5c0 7.8-6.3 14.2-14.2 14.2H14.2C6.3 90.7 0 84.4 0 76.5V14.2C0 6.3 6.3 0 14.2 0h62.3c7.8 0 14.2 6.3 14.2 14.2V76.5z"/>\n'
        note_render += '<circle cx="45.5" cy="45.4" r="26" class="instrument-button-icon ' + ' '.join(
            highlighted_classes).rstrip() + '"/>'
        note_render += '<rect x="19.5" y="19.3" transform="matrix(-0.7071 0.7071 -0.7071 -0.7071 109.7415 45.2438)" width="52" height="52" class="instrument-button-icon ' + ' '.join(
            highlighted_classes).rstrip() + '"/>\n'
        return note_render

    def get_png(self, highlighted_frames):
        try:
            if highlighted_frames[0] == 0:
                if self.get_position()[0] == 0:
                    return Image.open(self.A_root_png)
                elif self.get_position()[0] == 1:
                    return Image.open(self.B_root_png)
                elif self.get_position()[0] == 2:
                    return Image.open(self.C_root_png)
                else:
                    return None
            else:
                return Image.open(
                    self.root_highlighted_pngs[min(highlighted_frames[0], len(self.root_highlighted_pngs)) - 1])
        except:
            print('\nERROR: Could not open root note image.')
            return None
