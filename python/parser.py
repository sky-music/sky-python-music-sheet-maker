from instrument import *

### Parser

def parse_icon(icon, delimiter):

    tokens = icon.split(delimiter)
    return tokens

def parse_line(line, icon_delimiter, blank_icon, chord_delimiter):

    '''
    Returns instrument_line: a list of chord images
    '''
    #TODO: HAVENT accounted for double spaces and trailing/leading spaces
    icons = line.split(icon_delimiter)
    instrument_line = []

    #TODO: Implement logic for parsing line vs single icon.
    for icon in icons:
        chords = parse_icon(icon, chord_delimiter)
        harp = Harp()
        harp.parse_chords(chords, blank_icon)
        instrument_line.append(harp)

    return instrument_line


def render_instrument_line(instrument_line, instrument_index, note_width):

    line_render = ''

    for instrument in instrument_line:

        instrument_chord_image = instrument.get_chord_image()
        instrument_render = instrument.render_from_chord_image(instrument_chord_image, note_width, instrument_index)
        instrument_index += 1
        instrument_render += '\n\n'

        line_render += instrument_render

    return line_render, instrument_index

def render_instrument_lines(instrument_lines, note_width):

    index = 0

    song_render = ''

    for line in instrument_lines:
        line_render, index = render_instrument_line(line, index, note_width)
        song_render += line_render
        song_render += '\n<br />\n'

    return song_render
