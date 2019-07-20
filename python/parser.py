from instrument import *
from modes import *
from instrument import *

### Parser

class Parser:

    def __init__(self):

        self.keyboard_position_map = {'Q': (0, 0), 'W': (0, 1), 'E': (0, 2), 'R': (0, 3), 'T': (0, 4), 'A': (1, 0), 'S': (1, 1), 'D': (1, 2), 'F': (1, 3), 'G': (1, 4), 'Z': (2, 0), 'X': (2, 1), 'C': (2, 2), 'V': (2, 3), 'B': (2, 4)}
        self.alphanumeric_position_map = {'A1': (0, 0), 'A2': (0, 1), 'A3': (0, 2), 'A4': (0, 3), 'A5': (0, 4), 'B1': (1, 0), 'B2': (1, 1), 'B3': (1, 2), 'B4': (1, 3), 'B5': (1, 4), 'C1': (2, 0), 'C2': (2, 1), 'C3': (2, 2), 'C4': (2, 3), 'C5': (2, 4)}

    def get_keyboard_position_map(self):
        return self.keyboard_position_map

    def get_alphanumeric_position_map(self):
        return self.alphanumeric_position_map

    def parse_icon(self, icon, delimiter, input_mode):

        if input_mode == InputMode.KEYBOARD:
            tokens = icon.split(delimiter)
            return tokens
        elif input_mode == InputMode.ALPHANUMERIC:
            tokens = icon.split(delimiter)

    def parse_line(self, line, icon_delimiter, blank_icon, chord_delimiter, input_mode):

        '''
        Returns instrument_line: a list of chord images
        '''
        #TODO: HAVENT accounted for double spaces and trailing/leading spaces
        icons = line.split(icon_delimiter)
        instrument_line = []

        #TODO: Implement logic for parsing line vs single icon.
        for icon in icons:
            chords = self.parse_icon(icon, chord_delimiter, input_mode)
            chord_image = self.parse_chords(chords, blank_icon, input_mode)
            harp = Harp()
            harp.set_chord_image(chord_image)
            instrument_line.append(harp)

        return instrument_line

    def map_note_to_position(self, note, blank_icon, input_mode):

        '''
        Returns a tuple containing the row index and the column index of the note's position.
        '''

        if input_mode == InputMode.KEYBOARD:
            position_map = self.get_keyboard_position_map()
        if input_mode == InputMode.ALPHANUMERIC:
            position_map = self.get_alphanumeric_position_map()

        note = note.upper()
        if note in position_map.keys():
            return position_map[note] # Expecting a tuple
        #elif letter == BLANK_ICON:
        #    print(letter)
        #    raise BlankIconError
        elif note == blank_icon:
            #TODO: Implement support for breaks/empty harps
            #Define a custom InvalidLetterException
            raise KeyError
        else:
            raise KeyError

    def parse_chords(self, chords, blank_icon, input_mode):

        chord_image = {}

        for chord_idx, chord in enumerate(chords):

            # Create an image of the harp's chords
            # For each chord, set the highlighted state of each note accordingly (whether True or False)

            if input_mode == InputMode.KEYBOARD:

                for note in chord:
                    #Except InvalidLetterException
                    try:
                        highlighted_note_position = self.map_note_to_position(note, blank_icon, input_mode)
                    except KeyError:
                        pass
                    else:
                        chord_image[highlighted_note_position] = {}
                        chord_image[highlighted_note_position][chord_idx] = True
                        
            elif input_mode == InputMode.ALPHANUMERIC:
                try:
                    highlighted_note_position = self.map_note_to_position(chord, blank_icon, input_mode)
                except KeyError:
                    pass
                else:
                    chord_image[highlighted_note_position][chord_idx] = True

        return chord_image
