# Import notes

from notes import *
from modes import *

### Instrument classes

class Harp:

    def __init__(self):

        self.column_count = 5
        self.row_count = 3
        self.chord_image = {}
        self.highlighted_states_image = []
        self.instrument_type = 'harp'
        self.is_highlighted = False



    def get_row_count(self):
        return self.row_count

    def get_column_count(self):
        return self.column_count

    def get_is_highlighted(self):
        return self.is_highlighted

    def set_is_highlighted(self, is_highlighted):
        '''
        Expecting a boolean, to determine whether the harp is empty in this frame
        '''
        self.is_highlighted = is_highlighted

    def set_chord_image(self, chord_image):
        '''
        The chord_image is a dictionary. The keys are tuples representing the positions of the buttons. The values are dictionaries, where each key is the frame, and the value is a Boolean indicating whether the button is highlighted in that frame.
        '''
        #TODO: Raise TypeError if chord_image is not a dict
        self.chord_image = chord_image

    # def update_chord_image(self, index, new_state):
    def append_highlighted_state(self, row_index, column_index, new_state):

        '''
        INCOMPLETE IMPLEMENTATION. new_state is expected to be a Boolean
        '''

        chord_image = self.get_chord_image()

        row = chord_image[row_index]
        highlighted_states = row[column_index]
        highlighted_states.append(new_state)

        chord_image[index] = highlighted_states

        self.set_chord_image(chord_image)


    def get_chord_image(self):
        return self.chord_image



    def render_from_chord_image(self, chord_image, note_width, instrument_index):

        harp_is_empty = not(self.get_is_highlighted())

        harp_render = ''

        if harp_is_empty:
            harp_render += '<table class=\"harp harp-' + str(instrument_index) + ' empty \">'
        else:
            harp_render += '<table class=\"harp harp-' + str(instrument_index) + '\">'

        for row_index in range(self.get_row_count()):

            harp_render += '<tr>'

            for column_index in range(self.get_column_count()):

                harp_render += '<td>'

                # Calculate the note's overall index in the harp (0 to 14)
                note_index = (row_index * self.get_column_count()) + column_index

                note_position = (row_index, column_index)

                if note_index % 7 == 0:
                    # Note is a root note
                    note = NoteRoot()
                elif (note_index % self.get_column_count() == 0 or note_index % self.get_column_count() == 2) or note_index % self.get_column_count() == 4:
                    # Note is in an odd column, so it is a circle
                    note = NoteCircle()
                else:
                    # Note is in an even column, so it is a diamond
                    note = NoteDiamond()

                note_render = note.render_from_chord_image(note_width, chord_image, note_position, self.get_instrument_type(), note_index, harp_is_empty)
                harp_render += note_render
                harp_render += '</td>'

            harp_render += '</tr>'


        harp_render += '</table>'
        return harp_render


    def get_instrument_type(self):
        return self.instrument_type
