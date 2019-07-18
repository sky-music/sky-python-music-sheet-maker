# Import notes

from notes import *

### Instrument classes

class Harp:

    def __init__(self):

        self.column_count = 5
        self.row_count = 3
        self.keyboard_position_map = {'Q': (0, 0), 'W': (0, 1), 'E': (0, 2), 'R': (0, 3), 'T': (0, 4), 'A': (1, 0), 'S': (1, 1), 'D': (1, 2), 'F': (1, 3), 'G': (1, 4), 'Z': (2, 0), 'X': (2, 1), 'C': (2, 2), 'V': (2, 3), 'B': (2, 4)}
        self.chord_image = {}
        self.highlighted_states_image = []
        self.instrument_type = 'harp'

    def map_letter_to_position(self, letter, blank_icon):

        '''
        Returns a tuple containing the row index and the column index of the note's position.
        '''

        keyboard_position_map = self.get_keyboard_position_map()

        letter = letter.upper()
        if letter in keyboard_position_map.keys():
            return keyboard_position_map[letter] # Expecting a tuple
        #elif letter == BLANK_ICON:
        #    print(letter)
        #    raise BlankIconError
        elif letter == blank_icon:
            #TODO: Implement support for breaks/empty harps
            #Define a custom InvalidLetterException
            raise KeyError
        else:
            raise KeyError

    def get_row_count(self):
        return self.row_count

    def get_column_count(self):
        return self.column_count

    def get_keyboard_position_map(self):
        return self.keyboard_position_map

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

    def parse_chords(self, chords, blank_icon):

        keyboard_position_map = self.get_keyboard_position_map()

        chord_image = {}

        for chord_idx, chord in enumerate(chords):

            # Create an image of the harp's chords
            # For each chord, set the highlighted state of each note accordingly (whether True or False)

            for letter in chord:
                #Except InvalidLetterException
                try:
                    highlighted_note_position = self.map_letter_to_position(letter, blank_icon)
                except KeyError:
                    pass
                else:
                    chord_image[highlighted_note_position] = {}
                    chord_image[highlighted_note_position][chord_idx] = True

        self.set_chord_image(chord_image)

    def render_from_chord_image(self, chord_image, note_width, instrument_index):

        harp_render = ''
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

                note_render = note.render_from_chord_image(note_width, chord_image, note_position, self.get_instrument_type(), note_index)
                harp_render += note_render
                harp_render += '</td>'

            harp_render += '</tr>'


        harp_render += '</table>'
        return harp_render


    def get_instrument_type(self):
        return self.instrument_type
