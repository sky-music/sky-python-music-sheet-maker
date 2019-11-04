from modes import RenderMode
from notes import NoteRoot, NoteCircle, NoteDiamond
### Instrument classes

class Instrument:
    
    def __init__(self):
        self.instrument_type = 'undefined'
        self.chord_skygrid = {}
        self.repeat = 0
        self.index = 0
        self.is_silent = True
        self.is_broken = False
    
    def set_chord_skygrid(self, chord_skygrid):
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

    def get_instrument_type(self):
        return self.instrument_type
        
    def set_repeat(self, repeat):
        self.repeat = repeat

    def get_repeat(self):
        return self.repeat

    def set_index(self, index):
        self.index = index

    def get_index(self):
        return self.index
     
    def get_is_silent(self):
        return self.is_silent

    def get_is_broken(self):
        return self.is_broken

    def set_is_broken(self, is_broken):
        '''
        Expecting a boolean, to determine whether the harp could not be translated
        '''
        self.is_broken = is_broken

    def set_is_silent(self, is_silent):
        '''
        Expecting a boolean, to determine whether the harp is empty in this frame
        '''
        self.is_silent = is_silent


class Voice(Instrument): # Lyrics or comments
    
    def __init__(self):
        super().__init__()
        self.instrument_type = 'voice'
        self.lyric = ''
        
    def render_in_html(self, note_width):     
        chord_render = '<table class=\"voice\">'
        chord_render +='<tr>'
        chord_render +='<td  width=\"90em\" align=\"center\">' #TODO: width calculated automatically
        chord_render += self.lyric
        chord_render += '</td>'
        chord_render +='</tr>'
        chord_render +='</table>'
        return chord_render
    
    def get_chord_skygrid(self):
        return NotImplemented
    
    def set_chord_skygrid(self):
        return NotImplemented

    def get_lyric(self):
        return self.lyric
    
    def set_lyric(self, lyric):
        self.lyric = lyric

    def render_in_ascii(self, render_mode):     
        chord_render = '# ' + self.lyric # Lyrics marked as comments in output text files
        return chord_render
    
    def render_in_svg(self, x, width, height, aspect_ratio, render_mode):
        voice_render = '\n<svg x=\"' + '%.2f'%x + '\" y=\"0\" width=\"100%\" height=\"' + height + '\" class=\"voice voice-' + str(self.get_index()) + '\">'
        voice_render += '\n<text x=\"0%\" y=\"50%\" class=\"voice voice-' + str(self.get_index()) + '\">' + self.lyric + '</text>'
        voice_render += '\n</svg>'
        return voice_render
        #TODO: implement SVG render of lyrics

class Harp(Instrument):

    def __init__(self):
        super().__init__()
        self.instrument_type = 'harp'
        self.column_count = 5
        self.row_count = 3
        self.highlighted_states_skygrid = []      


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
     
    def get_note_from_position(self, row_index, column_index):
         
        # Calculate the note's overall index in the harp (0 to 14)              
        note_index = (row_index * self.get_column_count()) + column_index
    
        if note_index % 7 == 0:
            # Note is a root note
            return NoteRoot(self)
        elif (note_index % self.get_column_count() == 0 or note_index % self.get_column_count() == 2) or note_index % self.get_column_count() == 4:
            # Note is in an odd column, so it is a circle
            return NoteCircle(self)
        else:
            # Note is in an even column, so it is a diamond
            return NoteDiamond(self)
         

    def render_in_ascii(self, render_mode):
        
        ascii_chord = ''
        if render_mode == RenderMode.SKYASCII:
            inverse_map = self.sky_inverse_position_map
        elif render_mode == RenderMode.WESTERNASCII:
            inverse_map = self.western_inverse_position_map
        elif render_mode == RenderMode.JIANPUASCII:
            inverse_map = self.jianpu_inverse_position_map  
        else:
            inverse_map  = self.sky_inverse_position_map              
        
        if self.get_is_broken():
            ascii_chord = 'X'
        elif self.get_is_silent():
            ascii_chord = '.'
        else:
            chord_skygrid = self.get_chord_skygrid()
            for k in chord_skygrid: # Cycle over positions in a frame
                for f in chord_skygrid[k]: # Cycle over triplets & quavers
                    if chord_skygrid[k][f]==True: # Button is highlighted
                        ascii_chord += inverse_map[k]
        return ascii_chord        
        

    def render_in_html(self, note_width):

        harp_silent = self.get_is_silent()
        harp_broken = self.get_is_broken()

        if harp_broken:
            class_suffix = 'broken'
        elif harp_silent:
            class_suffix = 'silent'
        else:
            class_suffix = ''

        harp_render = '<table class=\"harp harp-' + str(self.get_index()) + ' ' + class_suffix + '">'

        for row in range(self.get_row_count()):

            harp_render += '<tr>'

            for col in range(self.get_column_count()):

                harp_render += '<td>'

                note = self.get_note_from_position(row, col)
                note.set_position(row, col)

                note_render = note.render_in_html(note_width)
                harp_render += note_render
                harp_render += '</td>'

            harp_render += '</tr>'

        harp_render += '</table>'
        
        if self.get_repeat() > 0:
            harp_render += '\n<table class=\"harp-' + str(self.get_index()) + ' repeat\">'
            harp_render += '<tr>'
            harp_render += '<td>'
            harp_render += 'x' + str(self.get_repeat())       
            harp_render += '</td>'
            harp_render += '</tr>'
            harp_render += '</table>'
        
        return harp_render


    def render_in_svg(self, x, harp_width, harp_height, aspect_ratio, render_mode):
              
        harp_silent = self.get_is_silent()
        harp_broken = self.get_is_broken()

        if harp_broken:
            class_suffix = 'broken'
        elif harp_silent:
            class_suffix = 'silent'
        else:
            class_suffix = ''
         
        # The chord SVG container
        harp_render = '\n<svg x=\"' + '%.2f'%x + '\" y=\"0\" width=\"' + harp_width + '\" height=\"' + harp_height + '\" class=\"instrument-harp harp-' + str(self.get_index()) + ' ' + class_suffix + '\">'     
         
        # The chord rectangle with rounded edges
        harp_render += '\n<rect x=\"0.7%\" y=\"0.7%\" width=\"98.6%\" height=\"98.6%\" rx=\"7.5%\" ry=\"' + '%.2f'%(7.5*aspect_ratio) + '%\" class=\"harp harp-' + str(self.get_index()) + '\"/>'

        for row in range(self.get_row_count()):
             for col in range(self.get_column_count()):
                
                note = self.get_note_from_position(row, col)                
                note.set_position(row, col)
                 
                note_width = 0.21
                xn = 0.12 + col*(1-2*0.12)/(self.get_column_count()-1)-note_width/2.0
                yn = 0.15 + row*(1-2*0.16)/(self.get_row_count()-1)-note_width/2.0
                
                #NOTE RENDER
                note_render = note.render_in_svg('%.2f'%(100*note_width)+'%', '%.2f'%(100*xn)+'%', '%.2f'%(100*yn)+'%')                                
                
                harp_render += note_render
            
        harp_render += '</svg>'
        
        return harp_render