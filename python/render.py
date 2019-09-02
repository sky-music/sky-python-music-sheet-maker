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
        song_render += '\n<br />\n<hr />\n<br />\n'

    return song_render
