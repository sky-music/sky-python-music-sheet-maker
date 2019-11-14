from PIL import Image

class Note:

    def __init__(self, instrument):
        self.position = ()
        self.index = 0
#        self.highlighted_states = []
        self.type = 'any_note'
        self.svgclass = 'any-note'
        self.chord_skygrid = instrument.get_chord_skygrid()
        self.instrument_type = instrument.get_type()
        self.harp_is_broken = instrument.get_is_broken()
        self.harp_is_silent = instrument.get_is_silent()
        self.row_count = instrument.get_row_count()
        self.column_count = instrument.get_column_count()
        self.A_root_png = 'elements/A-root.png'
        self.A_diamond_png = 'elements/A-diamond.png'
        self.A_circle_png = 'elements/A-circle.png'
        self.B_root_png = 'elements/B-root.png'
        self.B_diamond_png = 'elements/B-diamond.png'
        self.B_circle_png = 'elements/B-circle.png'
        self.C_root_png = 'elements/C-root.png'
        self.C_diamond_png = 'elements/C-diamond.png'
        self.C_circle_png = 'elements/C-circle.png'
        self.dead_png = 'elements/dead-note.png'
        self.dead_png = 'elements/dead-note.png'
        self.A_unhighlighted_png = 'elements/A-unhighlighted.png'
        self.B_unhighlighted_png = 'elements/B-unhighlighted.png'
        self.C_unhighlighted_png = 'elements/C-unhighlighted.png'
        self.root_highlighted_pngs = ['elements/root-highlighted-' + str(i) +'.png' for i in range(1,8)]
        self.diamond_highlighted_pngs = ['elements/diamond-highlighted-' + str(i) +'.png' for i in range(1,8)]
        self.circle_highlighted_pngs = ['elements/circle-highlighted-' + str(i) +'.png' for i in range(1,8)]
        self.png_size = None

    def get_position(self):
        '''Return the note position as a tuple row/column'''
        return self.position

    def set_position(self, row_index, col_index):
        '''Sets the position tuple from row and column values'''
        self.position = (row_index, col_index)

    def get_index(self):
        '''Returns the note index in Sky grid'''
        return (self.position[0] * self.column_count) + self.position[1]

    def get_middle_index(self):
        '''Returns the index at the center of Sky grid'''
        return int(self.row_count*self.column_count/2.0)

#    def get_highlighted_states(self):
#        return self.highlighted_states
#
#    def set_highlighted_states(self, highlighted_states):
#        '''
#        highlighted_states is a list of True/False depending on whether the note is highlighted in n-th frame, where n is the index of the item in the list
#        '''
#        #TODO: raise TypeError if type of highlighted_states is not a list
#        self.highlighted_states = highlighted_states

    def get_svg(self):
        return ''

    def get_png(self):
        return

    def set_png_size(self):
        '''Retrieves the original size of the .png image of a highlighted note'''
        if self.png_size == None:
            self.png_size =  Image.open(self.A_root_png).size

    def get_png_size(self):
        '''Returns the original size of the .png image of a note'''
        if self.png_size == None:
            self.set_png_size()
        return self.png_size

    def get_silentSymbol_svg(self, highlighted_classes):
        return '<circle cx=\"45.4\" cy=\"45.4\" r=\"26\" class=\"instrument-button-icon unhighlighted' + ' '.join(highlighted_classes).rstrip() + '\"/>'

    def get_dead_svg(self, highlighted_classes):
        return '<circle cx=\"45.4\" cy=\"45.4\" r=\"12\" class=\"instrument-button-icon unhighlighted' + ' '.join(highlighted_classes).rstrip() + '\"/>'

    def get_harpBroken_svg(self, highlighted_classes):
        return '<text x=\"45.4\" y=\"81\" class=\"broken\">?</text>'

    def get_unhighlighted_svg(self, highlighted_classes):
        return '<circle cx=\"45.4\" cy=\"45.4\" r=\"12\" class=\"instrument-button-icon unhighlighted' + ' '.join(highlighted_classes).rstrip() + '\"/>'

    def get_dead_png(self):
        '''Renders a PNG of a grey note placeholder, in case we want to display an empty harp when it is broken'''
        return Image.open(self.dead_png)

    def get_unhighlighted_png(self):
        '''Renders a PNG of a colored note placholder, when the note is note is unplayed'''
        if self.get_position()[0] == 0:
            return Image.open(self.A_unhighlighted_png)
        elif self.get_position()[0] == 1:
            return Image.open(self.B_unhighlighted_png)
        elif self.get_position()[0] == 2:
            return Image.open(self.C_unhighlighted_png)

    def render_in_html(self, width='1em', x=0, y=0):
        try:
            note_states = self.chord_skygrid[self.get_position()] #Is note at 'position' highlighted or not
            #skygrid is a dictionary with keys=position tuple, value = dictionary with key=frame, value=True/false
            # {(0,0):{0:True}, (1,1):{0:True}}
            highlighted_classes = ['highlighted-' + str(frame_index) for frame_index in note_states.keys()]
        except KeyError: #Note is not in the chord_skygrid dictionary: so it is not highlighted
            highlighted_classes = []
            pass

        if self.harp_is_broken and (self.get_index() == self.get_middle_index()):
                highlighted_classes = []
                #Draws a special symbol when harp is broken
                note_render = '\n<svg x=\"' + str(x) + '\" y=\"' + str(y) + '\" class=\"' + self.svgclass + ' ' + self.instrument_type + '-button-' + str(self.get_index()) + '\" width=\"' + str(width) + '\" height=\"' + str(width) + '\" viewBox=\"0 0 91 91\">\n'
                note_render += self.get_harpBroken_svg(highlighted_classes)
                note_render += '</svg>'
        elif self.harp_is_silent and (self.get_index() == self.get_middle_index()):
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
                note_render += self.get_dead_svg(highlighted_classes)
                note_render += '</svg>'
            else:
                if len(highlighted_classes)==0:
                    #Draws a small button (will be colored thanks to CSS)
                    note_render = '\n<svg x=\"' + str(x) + '\" y=\"' + str(y) + '\" class=\"' + self.svgclass + ' ' + self.instrument_type + '-button-' + str(self.get_index()) + '\" width=\"' + str(width) + '\" height=\"' + str(width) + '\" viewBox=\"0 0 91 91\">\n'
                    note_render +=  self.get_unhighlighted_svg(highlighted_classes)
                    note_render += '</svg>'
                else:
                    #Draws an highlighted note
                    note_render = '\n<svg x=\"' + str(x) + '\" y=\"' + str(y) + '\" class=\"' + self.svgclass + ' ' + self.instrument_type + '-button-' + str(self.get_index()) + '\" width=\"' + str(width) + '\" height=\"' + str(width) + '\" viewBox=\"0 0 91 91\">\n'
                    note_render += self.get_svg(highlighted_classes)
                    note_render += '</svg>'

        return note_render

    def render_in_svg(self, width, x, y):        
        return self.render_in_html(width, x, y)

    def render_in_png(self, rescale=1.0):
        try:
            note_states = self.chord_skygrid[self.get_position()] #Is note at 'position' highlighted or not
            highlighted_frames = [frame_index for frame_index in note_states.keys()]
        except KeyError: #Note is not in the chord_skygrid dictionary: so it is not highlighted
            note_states = {}
            highlighted_frames = []
            pass

        if not(self.harp_is_broken) and not(self.harp_is_silent):
            if len(highlighted_frames)==0:
                #Draws a small button (will be colored thanks to CSS)
                note_render = self.get_unhighlighted_png()
            else:
                #Draws an highlighted note
                note_render = self.get_png(highlighted_frames)
        else:
            note_render = self.get_dead_png()

        if rescale != 1:
            note_render = note_render.resize((int(note_render.size[0]*rescale),int(note_render.size[1]*rescale)), resample=Image.LANCZOS)

        return note_render

class NoteCircle(Note):

    def __init__(self, chord):
        super().__init__(chord)
        self.type = 'note_circle'
        self.svgclass = 'note-circle'

    def get_svg(self, highlighted_classes):
         note_render = '<path class="instrument-button ' + ' '.join(highlighted_classes).rstrip() + '" d="M90.7 76.5c0 7.8-6.3 14.2-14.2 14.2H14.2C6.3 90.7 0 84.4 0 76.5V14.2C0 6.3 6.3 0 14.2 0h62.3c7.8 0 14.2 6.3 14.2 14.2V76.5z"/>\n'
         note_render += '<circle cx="45.4" cy="45.4" r="25.5" class="instrument-button-icon ' + ' '.join(highlighted_classes).rstrip() + '"/>'
         return note_render

    def get_png(self, highlighted_frames):
        try:
            if highlighted_frames[0] == 0:
                if self.get_position()[0] == 0:
                    return Image.open(self.A_circle_png)
                elif self.get_position()[0] == 1:
                    return Image.open(self.B_circle_png)
                elif self.get_position()[0] == 2:
                    return Image.open(self.C_circle_png)
                else:
                    return None
            else:
                return Image.open(self.circle_highlighted_pngs[min(highlighted_frames[0]-1,len(self.circle_highlighted_pngs))])
        except:
            return None

class NoteDiamond(Note):

    def __init__(self, chord):
        super().__init__(chord)
        self.type = 'note_diamond'
        self.svgclass = 'note-diamond'

    def get_svg(self, highlighted_classes):
         note_render = '<path class="instrument-button ' + ' '.join(highlighted_classes).rstrip() + '" d="M90.7 76.5c0 7.8-6.3 14.2-14.2 14.2H14.2C6.3 90.7 0 84.4 0 76.5V14.2C0 6.3 6.3 0 14.2 0h62.3c7.8 0 14.2 6.3 14.2 14.2V76.5z"/>\n'
         note_render +=  '<rect x="22.6" y="22.7" transform="matrix(-0.7071 -0.7071 0.7071 -0.7071 45.3002 109.5842)" width="45.4" height="45.4" class="instrument-button-icon ' + ' '.join(highlighted_classes).rstrip() + '"/>'
         return note_render

    def get_png(self, highlighted_frames):
        try:
            if highlighted_frames[0] == 0:
                if self.get_position()[0] == 0:
                    return Image.open(self.A_diamond_png)
                elif self.get_position()[0] == 1:
                    return Image.open(self.B_diamond_png)
                elif self.get_position()[0] == 2:
                    return Image.open(self.C_diamond_png)
                else:
                    return None
            else:
                return Image.open(self.diamond_highlighted_pngs[min(highlighted_frames[0]-1,len(self.diamond_highlighted_pngs))])
        except:
            print('Could not open diamond note image.')
            return None

class NoteRoot(Note):

    def __init__(self, chord):
        super().__init__(chord)
        self.type = 'note_root'
        self.svgclass = 'note-root'

    def get_svg(self, highlighted_classes):
        note_render = '<path class="instrument-button ' + ' '.join(highlighted_classes).rstrip() + '" d="M90.7 76.5c0 7.8-6.3 14.2-14.2 14.2H14.2C6.3 90.7 0 84.4 0 76.5V14.2C0 6.3 6.3 0 14.2 0h62.3c7.8 0 14.2 6.3 14.2 14.2V76.5z"/>\n'
        note_render += '<circle cx="45.5" cy="45.4" r="26" class="instrument-button-icon ' + ' '.join(highlighted_classes).rstrip() + '"/>'
        note_render += '<rect x="19.5" y="19.3" transform="matrix(-0.7071 0.7071 -0.7071 -0.7071 109.7415 45.2438)" width="52" height="52" class="instrument-button-icon ' + ' '.join(highlighted_classes).rstrip() + '"/>\n'
        return note_render

    def get_png(self, highlighted_frames):
        try:
            if highlighted_frames[0] == 0:
                if self.get_position()[0] == 0:
                    return Image.open(self.A_root_png)
                elif self.get_position()[0] == 1:
                    return Image.open(self.B_root_png)
                elif self.get_position()[0] == 2:
                    return Image.open(self.C_root_png)
                else:
                    return None
            else:
                return Image.open(self.root_highlighted_pngs[min(highlighted_frames[0]-1,len(self.root_highlighted_pngs))])
        except:
            print('Could not open root note image.')
            return None
