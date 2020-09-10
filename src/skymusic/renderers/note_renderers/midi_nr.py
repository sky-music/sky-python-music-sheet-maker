from skymusic.resources import Resources
from . import note_renderer

try:
    import mido
    no_mido_module = False
except (ImportError, ModuleNotFoundError):
    no_mido_module = True


class MidiNoteRenderer(note_renderer.NoteRenderer):

    def __init__(self):
        pass

    def render(self, note, event_type, t=0, music_key='C'):
        """
        Starts or ends a MIDI note, assuming a chromatic scale (12 semitones)
        """
        octave = int(note.get_index() / 7)
        semi = Resources.MIDI_SEMITONES[note.get_index() % 7]
        try:
            root_pitch = Resources.MIDI_PITCHES[music_key]
        except KeyError:
            default_key = Resources.DEFAULT_KEY
            root_pitch = Resources.MIDI_PITCHES[default_key]
            
        note_pitch = root_pitch + octave * 12 + semi

        if not note.instrument_is_broken and not note.instrument_is_silent:
            if len(note.get_highlighted_frames()) == 0:
                midi_render = None
            else:
                midi_render = mido.Message(event_type, channel=0, note=note_pitch, velocity=127, time=int(t))
        else:
            midi_render = None

        return midi_render
