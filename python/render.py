from modes import RenderMode

def render_instrument_line(instrument_line, instrument_index, note_width, render_mode):

    line_render = ''

    for instrument in instrument_line:
        if render_mode == RenderMode.VISUAL:
            instrument_chord_image = instrument.get_chord_image() # A dict with position tuple and values Frame:True/False
            instrument_render = instrument.render_from_chord_image(instrument_chord_image, note_width, instrument_index) 
            instrument_render += '\n\n'
        elif render_mode in [RenderMode.SKYASCII, RenderMode.WESTERNASCII, RenderMode.JIANPUASCII]:
            instrument_chord_image = instrument.get_chord_image() # A dict with position tuple and values Frame:True/False
            instrument_render = instrument.ascii_from_chord_image(instrument_chord_image, render_mode) 
            instrument_render += ' '
        instrument_index += 1
        line_render += instrument_render
            
    return line_render, instrument_index

def render_instrument_lines(instrument_lines, note_width, render_mode):

    index = 0

    song_render = ''
    for line in instrument_lines:
        line_render, index = render_instrument_line(line, index, note_width, render_mode)
        song_render += line_render
        
        if len(line_render)>0:
            if render_mode == RenderMode.VISUAL:
                song_render += '\n<br />\n<hr />\n'
            elif render_mode in [RenderMode.SKYASCII, RenderMode.WESTERNASCII, RenderMode.JIANPUASCII]:
                    song_render += '\n'   

    return song_render
