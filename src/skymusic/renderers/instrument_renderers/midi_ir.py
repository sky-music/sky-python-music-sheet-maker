from . import instrument_renderer
from skymusic.renderers.note_renderers import midi_nr
from skymusic.resources import Resources

try:
    import mido

    no_mido_module = False
except (ImportError, ModuleNotFoundError):
    no_mido_module = True



class MidiInstrumentRenderer(instrument_renderer.InstrumentRenderer):
    
    def __init__(self, locale=None, note_ticks=960, music_key=Resources.DEFAULT_KEY):
        
        super().__init__(locale)

        self.note_ticks = note_ticks
        self.music_key = music_key
        relspacing = 0.1  # Spacing between midi notes, as a ratio of note duration
        #midi_pause_relticks = 1  # Spacing between midi notes, as a ratio of note duration
        quaver_relspacing = 0.1
        quaver_relticks = 0.5
        self.delta_times = {'note_on': relspacing * note_ticks, 'note_off': note_ticks, 'quaver_on': quaver_relspacing*note_ticks, 'quaver_off': quaver_relticks*note_ticks}

    '''
    def cycle_chord(self, instrument):
        
        note_renderer = midi_nr.MidiNoteRenderer(music_key=self.music_key)
        harp_render = []
        
        for event_type in ['note_on', 'note_off']:
            t = self.delta_times[event_type]
            for row in range(instrument.get_row_count()):
                for col in range(instrument.get_column_count()):
                    note = instrument.get_note_from_position((row, col))
                    frames = note.get_highlighted_frames()
                    if frames:
                        if frames[0] == 0:
                        # A chord note has a frame index==0
                            note_render = note_renderer.render(note, event_type, t)
        
                            if isinstance(note_render, mido.Message):
                                harp_render.append(note_render)
                                t = 0 #In a chord all notes are played simultaneously
                            
        return harp_render
    '''

    def render_icon(self, instrument):
        
        note_renderer = midi_nr.MidiNoteRenderer(music_key=self.music_key)
        #harp_render = []
        
        render_args = []
        harp_render = [] 
        
        t = self.delta_times['note_on']
        
        for frame in range(instrument.get_frame_count()):
            
            skygrid = instrument.get_skygrid(frame)
            
            if skygrid:
                for coord in skygrid:  # Cycle over (row, col) positions in an icon
                    
                    if skygrid[coord][frame]:  # Button is highlighted
                        note = instrument.get_note_from_position(coord)
                        
                        render_args.append({'note':note,'event_type':'note_on','t':t})
                        
                        note_duration = self.delta_times['note_off'] if frame == 0 else self.delta_times['quaver_off']
                        render_args.append({'note':note,'event_type':'note_off','t':t+note_duration})
                        
                if frame > 0:
                    t += self.delta_times['quaver_on']
        
        if render_args:
            render_args.sort(key=lambda v:v['t']) #sort by absolute time
            
            render_args[0]['delta_t'] = render_args[0]['t']
            for i in range(1, len(render_args)):
                render_args[i]['delta_t'] = render_args[i]['t'] - render_args[i-1]['t']
                                                 
            for kwarg in render_args:
                del(kwarg['t'])
                note_render = note_renderer.render(**kwarg)
                if note_render:
                    harp_render.append(note_render)                   
                            
        return harp_render


    def render_harp(self, instrument):
        harp_silent = instrument.get_is_silent()
        #harp_broken = instrument.get_is_broken()
        harp_dead = instrument.get_is_dead()

        if harp_dead:
            harp_render = [
                mido.Message('note_on', note=120, velocity=127, time=int(self.delta_times['note_on'])),
                mido.Message('note_off', note=120, velocity=127, time=int(self.delta_times['note_off']))]
        elif harp_silent:
            harp_render = [
                mido.Message('note_on', note=115, velocity=0, time=int(self.delta_times['note_on'])),
                mido.Message('note_off', note=115, velocity=0, time=int(self.delta_times['note_off']))]
        else:
            harp_render = self.render_icon(instrument)
                                                                             
        return harp_render


    def render_voice(self, *args, **kwargs):    

        return NotImplemented
