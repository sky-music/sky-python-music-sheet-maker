class NoteRenderer:

    def __init__(self):
        pass

    def render(self, *args, **kwargs):
        return
    
    def get_aspect(self, note):
        
        note_index = note.get_index()

        if not note.is_highlighted():
            return 'OFF'

        if note_index % 7 == 0:  # the 7 comes from the heptatonic scale of Sky's music (no semitones)
            # Note is a root note
            return 'root'
        elif note_index % note.instrument.get_column_count() % 2 == 0:
            # Note is in an odd column, so it is a circle
            return 'circle'
        else:
            # Note is in an even column, so it is a diamond
            return 'diamond'
