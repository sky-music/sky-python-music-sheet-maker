class NoteRoot:

    def __init__(self):
        self.icon = 'note_root'
        self.highlighted_states = []

    def get_highlighted_states(self):
        return self.highlighted_states

    def set_highlighted_states(self, highlighted_states):
        '''
        highlighted_states is a list of True/False depending on whether the note is highlighted in n-th frame, where n is the index of the item in the list
        '''
        #TODO: raise TypeError if type of highlighted_states is not a list
        self.highlighted_states = highlighted_states

    def render_from_highlighted_states(self, width):

        highlighted_states = self.get_highlighted_states()
        highlighted_classes = []

        for is_highlighted_idx, is_highlighted in enumerate(highlighted_states):
            if is_highlighted:
                highlighted_class = 'highlighted-' + str(is_highlighted_idx)
            else:
                highlighted_class = ''
            highlighted_classes.append(highlighted_class)

        note_render = '<svg class=\"note-root  \" xmlns=\"https://www.w3.org/2000/svg\" width=\"' + str(width) + '\" height=\"' + str(width) + '\" viewBox=\"0 0 91 91\">' #TODO: insert instrument type class .e.g harp-key-0, bass
        note_render += '<path class="instrument-button ' + ' '.join(highlighted_classes).rstrip() + '" d="M90.7 76.5c0 7.8-6.3 14.2-14.2 14.2H14.2C6.4 90.7 0 84.4 0 76.5V14.2C0 6.4 6.3 0 14.2 0h62.3c7.8 0 14.2 6.3 14.2 14.2V76.5z"/>'
        note_render += '<circle cx="45.5" cy="45.4" r="26" class="instrument-button-icon"/>'
        note_render += '<rect x="19.5" y="19.3" transform="matrix(-0.7071 0.7071 -0.7071 -0.7071 109.7415 45.2438)" width="52" height="52" class="instrument-button-icon"/>'
        note_render += '</svg>'
        return note_render

    def render_from_chord_image(self, width, chord_image, position, instrument_type, note_index):

        try:
            note_states = chord_image[position]
        except KeyError:
            highlighted_classes = []

            note_render = '<svg class=\"note-root ' + instrument_type + '-button-' + str(note_index) + ' \" xmlns=\"https://www.w3.org/2000/svg\" width=\"' + str(width) + '\" height=\"' + str(width) + '\" viewBox=\"0 0 91 91\">\n'
            note_render += '<circle cx="45.4" cy="45.4" r="12" class="instrument-button-icon unhighlighted ' + ' '.join(highlighted_classes).rstrip() + '"/>'
            #note_render += '<path class="instrument-button ' + ' '.join(highlighted_classes).rstrip() + '" d="M90.7 76.5c0 7.8-6.3 14.2-14.2 14.2H14.2C6.4 90.7 0 84.4 0 76.5V14.2C0 6.4 6.3 0 14.2 0h62.3c7.8 0 14.2 6.3 14.2 14.2V76.5z"/>\n'
            #note_render += '<circle cx="45.5" cy="45.4" r="26" class="instrument-button-icon ' + ' '.join(highlighted_classes).rstrip() + '"/>'
            #note_render += '<rect x="19.5" y="19.3" transform="matrix(-0.7071 0.7071 -0.7071 -0.7071 109.7415 45.2438)" width="52" height="52" class="instrument-button-icon ' + ' '.join(highlighted_classes).rstrip() + '"/>\n'
            note_render += '</svg>\n'
        else:
            highlighted_classes = ['highlighted-' + str(frame_index) for frame_index in note_states.keys()]

            note_render = '<svg class=\"note-root ' + instrument_type + '-button-' + str(note_index) + ' \" xmlns=\"https://www.w3.org/2000/svg\" width=\"' + str(width) + '\" height=\"' + str(width) + '\" viewBox=\"0 0 91 91\">\n'
            note_render += '<path class="instrument-button ' + ' '.join(highlighted_classes).rstrip() + '" d="M90.7 76.5c0 7.8-6.3 14.2-14.2 14.2H14.2C6.4 90.7 0 84.4 0 76.5V14.2C0 6.4 6.3 0 14.2 0h62.3c7.8 0 14.2 6.3 14.2 14.2V76.5z"/>\n'
            note_render += '<circle cx="45.5" cy="45.4" r="26" class="instrument-button-icon ' + ' '.join(highlighted_classes).rstrip() + '"/>'
            note_render += '<rect x="19.5" y="19.3" transform="matrix(-0.7071 0.7071 -0.7071 -0.7071 109.7415 45.2438)" width="52" height="52" class="instrument-button-icon ' + ' '.join(highlighted_classes).rstrip() + '"/>\n'
            note_render += '</svg>\n'

        return note_render


class NoteCircle:

    def __init__(self):
        self.icon = 'note_circle'
        self.highlighted_states = []

    def get_highlighted_states(self):
        return self.highlighted_states

    def set_highlighted_states(self, highlighted_states):
        '''
        highlighted_states is a list of True/False depending on whether the note is highlighted in n-th frame, where n is the index of the item in the list
        '''
        #TODO: raise TypeError if type of highlighted_states is not a list
        self.highlighted_states = highlighted_states

    def render_from_chord_image(self, width, chord_image, position, instrument_type, note_index):

        try:
            note_states = chord_image[position]
        except KeyError:
            highlighted_classes = []

            note_render = '<svg class=\"note-circle ' + instrument_type + '-button-' + str(note_index) + ' \" xmlns=\"https://www.w3.org/2000/svg\" width=\"' + str(width) + '\" height=\"' + str(width) + '\" viewBox=\"0 0 91 91\">\n'
            note_render += '<circle cx="45.4" cy="45.4" r="12" class="instrument-button-icon unhighlighted ' + ' '.join(highlighted_classes).rstrip() + '"/>'
            #note_render += '<path class="instrument-button ' + ' '.join(highlighted_classes).rstrip() + '" d="M90.7 76.5c0 7.8-6.3 14.2-14.2 14.2H14.2C6.3 90.7 0 84.4 0 76.5V14.2C0 6.3 6.3 0 14.2 0h62.3c7.8 0 14.2 6.3 14.2 14.2V76.5z"/>\n'
            #note_render += '<circle cx="45.4" cy="45.4" r="25.5" class="instrument-button-icon ' + ' '.join(highlighted_classes).rstrip() + '"/>'
            note_render += '</svg>\n'
        else:
            highlighted_classes = ['highlighted-' + str(frame_index) for frame_index in note_states.keys()]

            note_render = '<svg class=\"note-circle ' + instrument_type + '-button-' + str(note_index) + ' \" xmlns=\"https://www.w3.org/2000/svg\" width=\"' + str(width) + '\" height=\"' + str(width) + '\" viewBox=\"0 0 91 91\">\n'
            note_render += '<path class="instrument-button ' + ' '.join(highlighted_classes).rstrip() + '" d="M90.7 76.5c0 7.8-6.3 14.2-14.2 14.2H14.2C6.3 90.7 0 84.4 0 76.5V14.2C0 6.3 6.3 0 14.2 0h62.3c7.8 0 14.2 6.3 14.2 14.2V76.5z"/>\n'
            note_render += '<circle cx="45.4" cy="45.4" r="25.5" class="instrument-button-icon ' + ' '.join(highlighted_classes).rstrip() + '"/>'
            note_render += '</svg>\n'
        return note_render

class NoteDiamond:

    def __init__(self):
        self.icon = 'note_diamond'
        self.highlighted_states = []

    def get_highlighted_states(self):
        return self.highlighted_states

    def set_highlighted_states(self, highlighted_states):
        '''
        highlighted_states is a list of True/False depending on whether the note is highlighted in n-th frame, where n is the index of the item in the list
        '''
        #TODO: raise TypeError if type of highlighted_states is not a list
        self.highlighted_states = highlighted_states

    def render_from_chord_image(self, width, chord_image, position, instrument_type, note_index):

        try:
            note_states = chord_image[position]
        except KeyError:
            highlighted_classes = []

            note_render = '<svg class=\"note-diamond ' + instrument_type + '-button-' + str(note_index) + ' \" xmlns=\"https://www.w3.org/2000/svg\" width=\"' + str(width) + '\" height=\"' + str(width) + '\" viewBox=\"0 0 91 91\">\n'
            note_render += '<circle cx="45.4" cy="45.4" r="12" class="instrument-button-icon unhighlighted ' + ' '.join(highlighted_classes).rstrip() + '"/>'
            #note_render += '<path class="instrument-button ' + ' '.join(highlighted_classes).rstrip() + '" d="M90.7 76.5c0 7.8-6.3 14.2-14.2 14.2H14.2C6.4 90.7 0 84.4 0 76.5V14.2C0 6.4 6.3 0 14.2 0h62.3c7.8 0 14.2 6.3 14.2 14.2V76.5z"/>\n'
            #note_render += '<rect x="22.6" y="22.7" transform="matrix(-0.7071 -0.7071 0.7071 -0.7071 45.3002 109.5842)" width="45.4" height="45.4" class="instrument-button-icon ' + ' '.join(highlighted_classes).rstrip() + '"/>'
            note_render += '</svg>\n'
        else:
            highlighted_classes = ['highlighted-' + str(frame_index) for frame_index in note_states.keys()]

            note_render = '<svg class=\"note-diamond ' + instrument_type + '-button-' + str(note_index) + ' \" xmlns=\"https://www.w3.org/2000/svg\" width=\"' + str(width) + '\" height=\"' + str(width) + '\" viewBox=\"0 0 91 91\">\n'
            note_render += '<path class="instrument-button ' + ' '.join(highlighted_classes).rstrip() + '" d="M90.7 76.5c0 7.8-6.3 14.2-14.2 14.2H14.2C6.4 90.7 0 84.4 0 76.5V14.2C0 6.4 6.3 0 14.2 0h62.3c7.8 0 14.2 6.3 14.2 14.2V76.5z"/>\n'
            note_render += '<rect x="22.6" y="22.7" transform="matrix(-0.7071 -0.7071 0.7071 -0.7071 45.3002 109.5842)" width="45.4" height="45.4" class="instrument-button-icon ' + ' '.join(highlighted_classes).rstrip() + '"/>'
            note_render += '</svg>\n'
        return note_render
