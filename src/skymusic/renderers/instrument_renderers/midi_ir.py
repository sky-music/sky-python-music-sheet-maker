from . import instrument_renderer

try:
    import mido

    no_mido_module = False
except (ImportError, ModuleNotFoundError):
    no_mido_module = True



class MidiInstrumentRenderer(instrument_renderer.InstrumentRenderer):
    
    def __init__(self, locale=None):
        super().__init__(locale)

        self.midi_relspacing = 0.1  # Spacing between midi notes, as a ratio of note duration
        self.midi_pause_relduration = 1  # Spacing between midi notes, as a ratio of note duration
        self.midi_quaver_relspacing = 0.5

    def render_harp(self, instrument, note_duration=960, music_key='C'):
        harp_silent = instrument.get_is_silent()
        harp_broken = instrument.get_is_broken()

        if harp_broken:
            harp_render = [
                mido.Message('note_on', note=115, velocity=127, time=int(self.midi_relspacing * note_duration)),
                mido.Message('note_off', note=115, velocity=127, time=int(self.midi_relspacing * note_duration))]
        elif harp_silent:
            harp_render = [
                mido.Message('note_on', note=115, velocity=0, time=int(self.midi_relspacing * note_duration)),
                mido.Message('note_off', note=115, velocity=0, time=int(self.midi_pause_relduration * note_duration))]
        else:
            harp_render = []
            durations = [self.midi_relspacing * note_duration, note_duration]
            for i, event_type in enumerate(['note_on', 'note_off']):
                t = durations[i]
                for row in range(instrument.get_row_count()):
                    for col in range(instrument.get_column_count()):
                        note = instrument.get_note_from_position((row, col))
                        frames = note.get_highlighted_frames()

                        note_render = note.render_in_midi(event_type, t, music_key)

                        if isinstance(note_render, mido.Message):
                            harp_render.append(note_render)
                            # Below a complicated way to handle quavers
                            if frames[0] == 0 or event_type == 'note_off':
                                t = 0
                            elif frames[0] > 0 and event_type == 'note_on':
                                t = durations[0] + durations[1]
                            else:
                                t = durations[i]

        return harp_render


    def render_voice(self, *args, **kwargs):    

        return NotImplemented
