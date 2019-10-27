from modes import RenderMode

def render_line_html(instrument_line, instrument_index, note_width, render_mode):
    '''
    Renders a line with visual images of the chords, in HTML format
    '''
    line_render = ''
    for instrument in instrument_line:
        instrument_chord_skygrid = instrument.get_chord_skygrid() # A dict with position tuple and values Frame:True/False
        instrument_render = instrument.render_in_html(instrument_chord_skygrid, note_width, instrument_index) 
        instrument_render += ' '
        instrument_index += 1
        line_render += instrument_render
            
    return line_render, instrument_index

def render_line_ascii(instrument_line, instrument_index, render_mode):
    '''
    Renders a line with visual images of the chords, in ASCII format
    '''
    line_render = ''
    for instrument in instrument_line:
        instrument_chord_skygrid = instrument.get_chord_skygrid() # A dict with position tuple and values Frame:True/False
        instrument_render = instrument.render_in_ascii(instrument_chord_skygrid, render_mode) 
        instrument_render += ' '
        instrument_index += 1
        line_render += instrument_render
            
    return line_render, instrument_index


def write_html(html_file, titlehead = ['title: ', 'untitled'], headers = [], instrument_lines = [], note_width = '1em', render_mode = RenderMode.VISUALHTML):
    html_file.write('<!DOCTYPE html>\n')
    html_file.write('<html>\n')
    html_file.write('<head>')
    
    try:
        html_file.write('<title>' + titlehead[1][0] + '</title>')
    except:
        html_file.write('<title>Untitled</title> ')
    html_file.write('<link href="../css/main.css" rel="stylesheet" /> <meta charset="utf-8"/>')
    html_file.write('</head>\n')               
    html_file.write('<body>\n')
    
    try:
        html_file.write('<h1> ' + titlehead[0][0] + titlehead[1][0] + ' </h1>\n')
    except:
        html_file.write('<h1>Untitled</h1>\n')    

    try:
        for i in range(len(headers[0])):
            html_file.write('<p> <b>' + headers[0][i] + '</b> ' + headers[1][i] + ' </p>\n')
    except:
        pass

    html_file.write('<div id="transcript">\n\n')
    
    song_render = ''
    index = 0
    for line in instrument_lines:
        if len(line) > 0:
            if line[0].get_instrument_type() == 'voice':
                song_render += '\n<br />\n'
            else:
                song_render += '\n<hr />\n'              
            
            line_render, index = render_line_html(line, index, note_width, render_mode)
            song_render += line_render
    
    html_file.write(song_render)
    
    html_file.write('</div>\n')
    html_file.write('</body>\n')
    html_file.write('</html>\n')

    return True


def write_ascii(ascii_file, titlehead = ['title: ', 'untitled'], headers = [], instrument_lines = [], render_mode = RenderMode.SKYASCII):    
    try:
        ascii_file.write('#' + titlehead[1][0] + '\n')
    except:
        ascii_file.write('#Title: Untitled\n')
    
    try:
        for i in range(len(headers[0])):
            ascii_file.write('#' + headers[0][i] + ' ' + headers[1][i] + '\n')
    except:
        pass
    
    song_render = ''
    index = 0
    for line in instrument_lines:
        if len(line) > 0:
            #if line[0].get_instrument_type() == 'voice':
                #song_render += '#'           
            
            line_render, index = render_line_ascii(line, index, render_mode)
            song_render += line_render
            song_render += '\n' 
            
    ascii_file.write(song_render)

    return True
