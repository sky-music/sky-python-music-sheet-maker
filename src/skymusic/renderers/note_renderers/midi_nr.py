from skymusic.resources import Resources
from . import note_renderer

try:
    import mido
    no_mido_module = False
except (ImportError, ModuleNotFoundError):
    no_mido_module = True


class MidiNoteRenderer(note_renderer.NoteRenderer):

    def __init__(self, music_key=Resources.DEFAULT_KEY):
        self.music_key = music_key

    def render(self, note, event_type, delta_t=0):
        """
        Starts or ends a MIDI note, assuming a chromatic scale (12 semitones)
        """
        octave = int(note.get_index() / 7) #7 because of the heptatonic tone scale of Sky (no accidentals)
        semi = Resources.MIDI_SEMITONES[note.get_index() % 7]
        try:
            root_pitch = Resources.MIDI_PITCHES[self.music_key]
        except KeyError:
            root_pitch = Resources.MIDI_PITCHES[Resources.DEFAULT_KEY]
            
        note_pitch = root_pitch + octave * 12 + semi

        if len(note.get_highlighted_frames()) == 0:
            midi_render = None
        else:
            midi_render = mido.Message(event_type, channel=0, note=note_pitch, velocity=64, time=int(delta_t))

        return midi_render
