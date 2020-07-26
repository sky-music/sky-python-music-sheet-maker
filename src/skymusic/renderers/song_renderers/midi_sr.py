import re, io
from . import song_renderer
from src.skymusic.renderers.instrument_renderers.midi_ir import MidiInstrumentRenderer
from src.skymusic.resources import Resources

try:
    import mido

    no_mido_module = False
except (ImportError, ModuleNotFoundError):
    no_mido_module = True


class MidiSongRenderer(song_renderer.SongRenderer):

    def __init__(self, locale=None, song_bpm=Resources.DEFAULT_BPM):
        
        super().__init__(locale)
        
        if not no_mido_module:
            # CAUTION: instrument codes correspond to General Midi codes (see Wikipedia) minus 1
            # An instrument will sound very strange if played outside its natural pitch range
            midi_instruments = {'piano': 0, 'guitar': 24, 'flute': 73, 'pan': 75}
            self.midi_note_duration = 0.3*Resources.DEFAULT_BPM/120  # note duration is 0.3 seconds for 120 bpm
            if isinstance(song_bpm, (int, float)):
                self.midi_bpm = song_bpm  # Beats per minute
            else:
                self.midi_bpm = Resources.DEFAULT_BPM
            self.midi_instrument = midi_instruments['piano']
            self.midi_key = None


    def write_header(self, mid, track, tempo):
                
        track.append(mido.MetaMessage('set_tempo', tempo=tempo))

        try:
            track.append(mido.MetaMessage('key_signature', key=self.midi_key))
        except ValueError:
            print("\n***ERROR: invalid key passed to MIDI renderer. Using C instead.")
            track.append(mido.MetaMessage('key_signature', key='C'))
        try:
            track.append(mido.Message('program_change', program=self.midi_instrument, time=0))
        except ValueError:
            print("\n***ERROR: invalid instrument passed to MIDI renderer. Using piano instead.")
            track.append(mido.Message('program_change', program=1, time=0))      


    def write_buffers(self, song):
        global no_mido_module

        if no_mido_module:
            print("\n***WARNING: MIDI was not created because mido module was not found.")
            return None
    
        try:
            self.midi_key = re.sub(r'#', '#m', song.get_music_key())  # For mido sharped keys are minor
        except TypeError:
            self.midi_key = Resources.DEFAULT_KEY
            print(f"\n***ERROR: Invalid music key passed to the MIDI renderer: using {self.midi_key} instead.")

        try:
            tempo = mido.bpm2tempo(self.midi_bpm)
        except ValueError:
            print(f"\n***ERROR: invalid tempo passed to MIDI renderer. Using {Resources.DEFAULT_BPM} bpm instead.")
            tempo = mido.bpm2tempo(Resources.DEFAULT_BPM)

        mid = mido.MidiFile(type=0)
        track = mido.MidiTrack()
        mid.tracks.append(track)

        sec = mido.second2tick(1, ticks_per_beat=mid.ticks_per_beat, tempo=tempo)  # 1 second in ticks
        note_ticks = self.midi_note_duration * sec * Resources.DEFAULT_BPM / self.midi_bpm  # note duration in ticks
                        
        self.write_header(mid, track, tempo)

        instrument_renderer = MidiInstrumentRenderer(self.locale)
        song_lines = song.get_lines()
        for line in song_lines:
            if len(line) > 0:
                if line[0].get_type().lower().strip() != 'voice':
                    instrument_index = 0
                    for instrument in line:
                        instrument.set_index(instrument_index)
                        #instrument_render = instrument.render_in_midi(note_duration=note_ticks,
                        #                                              music_key=song.get_music_key())
                        instrument_render = instrument_renderer.render(instrument, note_duration=note_ticks,
                                                                      music_key=song.get_music_key())
                        for i in range(0, instrument.get_repeat()):
                            for note_render in instrument_render:
                                track.append(note_render)
                            instrument_index += 1
        
        midi_buffer = io.BytesIO()
        mid.save(file=midi_buffer)
        
        midi_buffer.seek(0)

        return [midi_buffer]
