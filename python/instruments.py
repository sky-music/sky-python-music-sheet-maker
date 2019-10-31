from notes import NoteRoot, NoteCircle, NoteDiamond
from modes import RenderMode
### Instrument classes
# A cleaner implementation should define a generic instrument class
# and  instrument sub-classes inheriting some methods

class Voice: # Lyrics or comments
    
    def __init__(self):
        self.instrument_type = 'voice'
        self.chord_skygrid = {}
        self.repeat = 0
        
    def render_in_html(self, lyrics, note_width, instrument_index):     
        chord_render = '<table class=\"voice\">'
        chord_render +='<tr>'
        chord_render +='<td  width=\"90em\" align=\"center\">' #TODO: width calculated automatically
        chord_render += lyrics
        chord_render += '</td>'
        chord_render +='</tr>'
        chord_render +='</table>'
        return chord_render

    def render_in_ascii(self, lyrics, render_mode):     
        chord_render = '# ' + lyrics # Lyrics marked as comments in output text files
        return chord_render
    
    def set_chord_skygrid(self, chord_skygrid):
        self.chord_skygrid = chord_skygrid
        
    def get_instrument_type(self):
        return self.instrument_type
    
    def get_chord_skygrid(self):
        return self.chord_skygrid
    
    def set_repeat(self, repeat):
        self.repeat = repeat

    def get_repeat(self):
        return self.repeat

class Harp:

    def __init__(self):

        self.column_count = 5
        self.row_count = 3
        self.chord_skygrid = {}
        self.highlighted_states_skygrid = []
        self.instrument_type = 'harp'
        self.is_empty = True
        self.is_error = False
        self.repeat = 0

        self.sky_inverse_position_map = {
                (0, 0): 'A1', (0, 1): 'A2', (0, 2): 'A3', (0, 3): 'A4', (0, 4): 'A5',
                (1, 0): 'B1', (1, 1): 'B2', (1, 2): 'B3', (1, 3): 'B4', (1, 4): 'B5',
                (2, 0): 'C1', (2, 1): 'C2', (2, 2): 'C3', (2, 3): 'C4', (2, 4): 'C5'
                }
        
        self.western_inverse_position_map = {
                (0, 0): 'C4', (0, 1): 'D4', (0, 2): 'E4', (0, 3): 'F4', (0, 4): 'G4',
                (1, 0): 'A4', (1, 1): 'B4', (1, 2): 'C5', (1, 3): 'D5', (1, 4): 'E5',
                (2, 0): 'F5', (2, 1): 'G5', (2, 2): 'A6', (2, 3): 'B6', (2, 4): 'C6'
                }
        
        self.jianpu_inverse_position_map = {
                (0, 0): '1', (0, 1): '2', (0, 2): '3', (0, 3): '4', (0, 4): '5',
                (1, 0): '6', (1, 1): '7', (1, 2): '1+', (1, 3): '2+', (1, 4): '3+',
                (2, 0): '4+', (2, 1): '5+', (2, 2): '6+', (2, 3): '7+', (2, 4): '1++'
                }               

    def get_row_count(self):
        return self.row_count

    def get_column_count(self):
        return self.column_count
    
    def get_instrument_type(self):
        return self.instrument_type
    
    def get_is_empty(self):
        return self.is_empty

    def get_is_error(self):
        return self.is_error

    def set_repeat(self, repeat):
        self.repeat = repeat

    def get_repeat(self):
        return self.repeat

    def set_is_error(self, is_error):
        '''
        Expecting a boolean, to determine whether the harp could not be translated
        '''
        self.is_error = is_error

    def set_is_empty(self, is_empty):
        '''
        Expecting a boolean, to determine whether the harp is empty in this frame
        '''
        self.is_empty = is_empty

    def set_chord_skygrid(self, chord_skygrid):
        '''
        The chord_skygrid is a dictionary. The keys are tuples representing the positions of the buttons. The values are dictionaries, where each key is the frame, and the value is a Boolean indicating whether the button is highlighted in that frame.
        '''
        # Ok, but in this case the dict should have keys for all the positions, and shut down buttons should be set to False
        #TODO: Raise TypeError if chord_skygrid is not a dict
        self.chord_skygrid = chord_skygrid

    # def update_chord_skygrid(self, index, new_state):
#    def append_highlighted_state(self, row_index, column_index, new_state):
#
#        '''
#        INCOMPLETE IMPLEMENTATION. new_state is expected to be a Boolean
#        '''
#
#        chord_skygrid = self.get_chord_skygrid()
#
#        row = chord_skygrid[row_index]
#        highlighted_states = row[column_index]
#        highlighted_states.append(new_state)
#
#        chord_skygrid[index] = highlighted_states #index is undefined
#
#        self.set_chord_skygrid(chord_skygrid)


    def get_chord_skygrid(self):
        return self.chord_skygrid

    def render_in_ascii(self, chord_skygrid, render_mode):
        
        ascii_chord = ''
        if render_mode == RenderMode.SKYASCII:
            inverse_map = self.sky_inverse_position_map
        elif render_mode == RenderMode.WESTERNASCII:
            inverse_map = self.western_inverse_position_map
        elif render_mode == RenderMode.JIANPUASCII:
            inverse_map = self.jianpu_inverse_position_map  
        else:
            inverse_map  = self.sky_inverse_position_map              
        
        #TODO: differentiate empty harps and pauses
        if len(chord_skygrid)==0:
            ascii_chord = '.' # Empty frame is assumed to be a pause
        else:
            for k in chord_skygrid: # Cycle over positions in a frame
                for f in chord_skygrid[k]: # Cycle over triplets & quavers
                    if chord_skygrid[k][f]==True: # Button is highlighted
                        ascii_chord += inverse_map[k]
        return ascii_chord        
        

    def render_in_html(self, chord_skygrid, note_width, instrument_index):

        harp_empty = self.get_is_empty()
        harp_error = self.get_is_error()

        harp_render = ''

        if harp_empty:
            harp_render += '<table class=\"harp harp-' + str(instrument_index) + ' empty\">'
        elif harp_error:
            harp_render += '<table class=\"harp harp-' + str(instrument_index) + ' error\">'
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

                note_render = note.render_in_html(note_width, chord_skygrid, note_position, self.get_instrument_type(), note_index, harp_empty, harp_error)
                harp_render += note_render
                harp_render += '</td>'

            harp_render += '</tr>'

        harp_render += '</table>'
        
        if self.get_repeat() > 0:
            harp_render += '<table class=\"repeat harp-' + str(instrument_index) + ' empty \">'
            harp_render += '<tr>'
            harp_render += '<td>'
            harp_render += 'x' + str(self.get_repeat())       
            harp_render += '</td>'
            harp_render += '</tr>'
            harp_render += '</table>'
        
        return harp_render
    