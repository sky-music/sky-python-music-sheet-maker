class Note:
    
    def __init__(self, chord):
        self.position = ()
        self.index = 0
        self.highlighted_states = []
        self.icon = 'any_note'
        self.svgclass = 'any-note'
        self.chord_skygrid = chord.get_chord_skygrid()
        self.instrument_type = chord.get_instrument_type()
        self.harp_is_broken = chord.get_is_broken()
        self.harp_is_silent = chord.get_is_silent()
        self.column_count = chord.get_column_count()

    def get_position(self):
        return self.position
    
    def set_position(self, row_index, col_index):
        self.position = (row_index, col_index)

    def get_index(self):
        return (self.position[0] * self.column_count) + self.position[1]

    
    def get_highlighted_states(self):
        return self.highlighted_states

    def set_highlighted_states(self, highlighted_states):
        '''
        highlighted_states is a list of True/False depending on whether the note is highlighted in n-th frame, where n is the index of the item in the list
        '''
        #TODO: raise TypeError if type of highlighted_states is not a list
        self.highlighted_states = highlighted_states
        
    def get_note_svg(self):
        return ''

    def get_silentSymbol_svg(self, highlighted_classes):         
        return '<circle cx=\"45.4\" cy=\"45.4\" r=\"26\" class=\"instrument-button-icon unhighlighted' + ' '.join(highlighted_classes).rstrip() + '\"/>'       
    
    def get_deadNote_svg(self, highlighted_classes):         
        return '<circle cx=\"45.4\" cy=\"45.4\" r=\"12\" class=\"instrument-button-icon unhighlighted' + ' '.join(highlighted_classes).rstrip() + '\"/>'       
     
    def get_harpBroken_svg(self, highlighted_classes): 
        #return '<circle cx="45.4" cy="45.4" r="20" class="instrument-button-icon unhighlighted' + ' '.join(highlighted_classes).rstrip() + '"/>'
        return '<text x=\"45.4\" y=\"81\" class=\"broken\">?</text>'

    def get_unhighlightedNote_svg(self, highlighted_classes):       
        return '<circle cx=\"45.4\" cy=\"45.4\" r=\"12\" class=\"instrument-button-icon unhighlighted' + ' '.join(highlighted_classes).rstrip() + '\"/>'
    
    def render_in_html(self, width='1em', x=0, y=0):

        try:
            note_states = self.chord_skygrid[self.get_position()] #Is note at 'position' highlighted or not
            highlighted_classes = ['highlighted-' + str(frame_index) for frame_index in note_states.keys()]
        except KeyError: #Note is not in the chord_skygrid dictionary: so it is not highlighted
            highlighted_classes = []
        
        
        if self.harp_is_broken and (self.get_index() == 7):
                highlighted_classes = []
                #Draws a special symbol when harp is broken
                note_render = '\n<svg x=\"' + str(x) + '\" y=\"' + str(y) + '\" class=\"' + self.svgclass + ' ' + self.instrument_type + '-button-' + str(self.get_index()) + '\" width=\"' + str(width) + '\" height=\"' + str(width) + '\" viewBox=\"0 0 91 91\">\n'
                note_render += self.get_harpBroken_svg(highlighted_classes)
                note_render += '</svg>'
        elif self.harp_is_silent and (self.get_index() == 7):
                highlighted_classes = []
                #Draws a special symbol when harp is silent
                note_render = '\n<svg x=\"' + str(x) + '\" y=\"' + str(y) + '\" class=\"' + self.svgclass + ' ' + self.instrument_type + '-button-' + str(self.get_index()) + '\" width=\"' + str(width) + '\" height=\"' + str(width) + '\" viewBox=\"0 0 91 91\">\n'
                note_render += self.get_silentSymbol_svg(highlighted_classes)
                note_render += '</svg>'
        else:
            if self.harp_is_broken or self.harp_is_silent:
                #Draws a small button (will be grey thanks to CSS)
                highlighted_classes = []   
                note_render = '\n<svg x=\"' + str(x) + '\" y=\"' + str(y) + '\" class=\"' + self.svgclass + ' unhighlighted ' + self.instrument_type + '-button-' + str(self.get_index()) + '\" width=\"' + str(width) + '\" height=\"' + str(width) + '\" viewBox=\"0 0 91 91\">\n'
                note_render += self.get_deadNote_svg(highlighted_classes)
                note_render += '</svg>'
            else:
                if len(highlighted_classes)==0:
                    #Draws a small button (will be colored thanks to CSS)
                    note_render = '\n<svg x=\"' + str(x) + '\" y=\"' + str(y) + '\" class=\"' + self.svgclass + ' ' + self.instrument_type + '-button-' + str(self.get_index()) + '\" width=\"' + str(width) + '\" height=\"' + str(width) + '\" viewBox=\"0 0 91 91\">\n'
                    note_render +=  self.get_unhighlightedNote_svg(highlighted_classes)       
                    note_render += '</svg>'
                else:
                    #Draws an highlighted note          
                    note_render = '\n<svg x=\"' + str(x) + '\" y=\"' + str(y) + '\" class=\"' + self.svgclass + ' ' + self.instrument_type + '-button-' + str(self.get_index()) + '\" width=\"' + str(width) + '\" height=\"' + str(width) + '\" viewBox=\"0 0 91 91\">\n'
                    note_render += self.get_note_svg(highlighted_classes)
                    note_render += '</svg>'
     
        return note_render

    def render_in_svg(self, width, x, y):        
        return self.render_in_html(width, x, y)        

class NoteCircle(Note):   
     
    def __init__(self, chord):
        super().__init__(chord)
        self.icon = 'note_circle'
        self.svgclass = 'note-circle'
        
    def get_note_svg(self, highlighted_classes):
         note_render = '<path class="instrument-button ' + ' '.join(highlighted_classes).rstrip() + '" d="M90.7 76.5c0 7.8-6.3 14.2-14.2 14.2H14.2C6.3 90.7 0 84.4 0 76.5V14.2C0 6.3 6.3 0 14.2 0h62.3c7.8 0 14.2 6.3 14.2 14.2V76.5z"/>\n'       
         note_render += '<circle cx="45.4" cy="45.4" r="25.5" class="instrument-button-icon ' + ' '.join(highlighted_classes).rstrip() + '"/>'
         return note_render
     
class NoteDiamond(Note):   
     
    def __init__(self, chord):
        super().__init__(chord)
        self.icon = 'note_diamond'
        self.svgclass = 'note-diamond'
        
    def get_note_svg(self, highlighted_classes):
         note_render = '<path class="instrument-button ' + ' '.join(highlighted_classes).rstrip() + '" d="M90.7 76.5c0 7.8-6.3 14.2-14.2 14.2H14.2C6.3 90.7 0 84.4 0 76.5V14.2C0 6.3 6.3 0 14.2 0h62.3c7.8 0 14.2 6.3 14.2 14.2V76.5z"/>\n'       
         note_render +=  '<rect x="22.6" y="22.7" transform="matrix(-0.7071 -0.7071 0.7071 -0.7071 45.3002 109.5842)" width="45.4" height="45.4" class="instrument-button-icon ' + ' '.join(highlighted_classes).rstrip() + '"/>'
         return note_render

class NoteRoot(Note):   
     
    def __init__(self, chord):
        super().__init__(chord)
        self.icon = 'note_root'
        self.svgclass = 'note-root'
        
    def get_note_svg(self, highlighted_classes):
        note_render = '<path class="instrument-button ' + ' '.join(highlighted_classes).rstrip() + '" d="M90.7 76.5c0 7.8-6.3 14.2-14.2 14.2H14.2C6.3 90.7 0 84.4 0 76.5V14.2C0 6.3 6.3 0 14.2 0h62.3c7.8 0 14.2 6.3 14.2 14.2V76.5z"/>\n'       
        note_render += '<circle cx="45.5" cy="45.4" r="26" class="instrument-button-icon ' + ' '.join(highlighted_classes).rstrip() + '"/>'
        note_render += '<rect x="19.5" y="19.3" transform="matrix(-0.7071 0.7071 -0.7071 -0.7071 109.7415 45.2438)" width="52" height="52" class="instrument-button-icon ' + ' '.join(highlighted_classes).rstrip() + '"/>\n'
        return note_render
        