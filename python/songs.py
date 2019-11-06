from modes import RenderMode
#import re
import instruments
import os
from PIL import Image

class Song():

    def __init__(self):
        
        self.lines = []
        self.title = 'Untitled'
        self.headers = [['Original Artist(s):', 'Transcript:', 'Musical key:'], ['', '', '']]
        self.viewPort = (0.0, 0.0, 1334.0, 750.0)
        self.minDim = self.viewPort[2]*0.01
        self.viewPortMargins = (13.0, 7.5)
        self.maxIconsPerLine = 10
        self.maxLinesPerFile = 10
        self.maxFiles = 10
        self.harp_AspectRatio = 3.0/2
        self.pt2px = 96.0/72
        self.fontpt = 12
        self.text_height = self.fontpt * self.pt2px # In principle this should be in em
        f = 0.1 # Fraction of the harp width that will be allocated to the spacing between harps
        self.line_width = self.viewPort[2]-self.viewPortMargins[0]
        self.harp_width = max(self.minDim, (self.viewPort[2] - self.viewPortMargins[0])/(1.0*self.maxIconsPerLine*(1+f)))
        self.harp_height = max(self.minDim, self.harp_width / self.harp_AspectRatio)
        self.harp_Xspacing = (f*self.harp_width)
        self.harp_Yspacing = (self.harp_Xspacing)
#        self.notes_colSpacing = 0.2*self.harp_width
#        self.notes_rowSpacing = 0.32*self.harp_height
        
 
    def add_line(self, line):
        if len(line)>0:
            if isinstance(line[0], instruments.Instrument):
                self.lines.append(line)
        
    def get_line(self, row):
        try:
            return self.lines[row]
        except:
            return [[]]
        
    def get_instrument(self, row, col):
        try:
            return self.lines[row][col]
        except:
            return []
     
    def set_title(self, title):
        self.title = title
        
    def set_headers(self, original_artists='', transcript_writer='', musical_key=''):
        self.headers[1] = [original_artists, transcript_writer, musical_key]

    def get_voice_SVG_height(self):
        return self.fontpt*self.pt2px
    
    def write_html(self, file_path, note_width='1em', render_mode=RenderMode.VISUAL, embed_css=True, css_path='css/main.css'):
        
        try:
            html_file = open(file_path, 'w+')
        except:
            print('Could not create text file.')
            return '' 
        
        html_file.write('<!DOCTYPE html>'
                        '\n<html xmlns:svg=\"http://www.w3.org/2000/svg\">')
        html_file.write('\n<head>\n<title>' + self.title + '</title>')  
        
        try:
            with open(css_path, 'r') as css_file:
                css_file = css_file.read()
        except:
            print('Could not open CSS file.')
            css_file = ''
    
        if embed_css == True:
            html_file.write('\n<style type=\"text/css\">')
            html_file.write(css_file)
            html_file.write('\n</style>')
        else:
            css_path = os.path.relpath('css/main.css', start= os.path.dirname(file_path))
            html_file.write('\n<link href="' + css_path + '" rel="stylesheet" />')
            
        html_file.write('\n<meta charset="utf-8"/></head>\n<body>')
        html_file.write('\n<h1> ' + self.title + ' </h1>')
      
        for i in range(len(self.headers[0])):
            html_file.write('\n<p> <b>' + self.headers[0][i] + '</b> ' + self.headers[1][i] + ' </p>')
    
        html_file.write('\n<div id="transcript">\n')
        
        song_render = ''
        instrument_index = 0
        for line in self.lines:
            if len(line) > 0:
                if line[0].get_instrument_type() == 'voice':
                    song_render += '\n<br />'
                else:
                    song_render += '\n<hr />'              
                            
                line_render = '\n'
                for instrument in line:
                    instrument.set_index(instrument_index)
                    instrument_render = instrument.render_in_html(note_width) 
                    instrument_render += ' '
                    instrument_index += 1
                    line_render += instrument_render
    
                song_render += line_render
        
        html_file.write(song_render)
        
        html_file.write('\n</div>'
                        '\n</body>'
                        '\n</html>')
    
        return file_path
    
    
    def write_ascii(self, file_path, render_mode = RenderMode.SKYASCII):    
    
        try:
            ascii_file = open(file_path, 'w+')
        except:
            print('Could not create text file.')
            return ''
        
        ascii_file.write('#' + self.title + '\n')

        for i in range(len(self.headers[0])):
            ascii_file.write('#' + self.headers[0][i] + ' ' + self.headers[1][i])

        song_render = '\n'
        instrument_index = 0
        for line in self.lines:
            line_render = ''
            for instrument in line:
                instrument.set_index(instrument_index)
                instrument_render = instrument.render_in_ascii(render_mode) 
                instrument_index += 1
                line_render += instrument_render
            song_render += '\n' + line_render
                
        ascii_file.write(song_render)
    
        return file_path
    
    def write_svg(self, file_path0, render_mode=RenderMode.VISUAL, embed_css=True, css_path='css/main.css', start_row=0, filenum=0):    
        
        if filenum>self.maxFiles:
            print('\nYour song is too long. Stopping at ' + str(self.maxFiles) + ' files.')
            return ''

        if filenum>0:
            (file_base, file_ext) = os.path.splitext(file_path0)
            file_path = file_base + str(filenum) + file_ext
        else:
            file_path = file_path0
            
        try:
            svg_file = open(file_path, 'w+')
        except:
            print('Could not create SVG file.')
            return ''
        
        # SVG/XML headers
        if embed_css == True:
            try:
                with open(css_path, 'r') as css_file:
                    css_file = css_file.read()
            except:
                print('Could not open CSS file.')
                css_file = ''

            svg_file.write('<?xml version=\"1.0\" encoding=\"utf-8\" ?>'
                      '\n<svg baseProfile=\"full\" version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:ev=\"http://www.w3.org/2001/xml-events\" xmlns:xlink=\"http://www.w3.org/1999/xlink\"'
                      ' width=\"100%\" height=\"100%\"'
                      ' viewBox=\"' + ' '.join((str(self.viewPort[0]), str(self.viewPort[1]), str(self.viewPort[2]), str(self.viewPort[3]))) + '\" preserveAspectRatio=\"xMinYMin\">'
                      '\n<defs><style type=\"text/css\"><![CDATA[\n')             
            svg_file.write(css_file)             
            svg_file.write('\n]]></style></defs>'
                           '\n<title>' + self.title + '-' + str(filenum) + '</title>')
        else:
            css_path = os.path.relpath('css/main.css', start= os.path.dirname(file_path))
            svg_file.write('<?xml version=\"1.0\" encoding=\"utf-8\" ?>'
                          '\n<?xml-stylesheet href=\"' + css_path + '\" type=\"text/css\" alternate=\"no\" media=\"all\"?>'
                          '\n<svg baseProfile=\"full\" version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:ev=\"http://www.w3.org/2001/xml-events\" xmlns:xlink=\"http://www.w3.org/1999/xlink\"'
                          ' width=\"100%\" height=\"100%\"'
                          ' viewBox=\"' + ' '.join((str(self.viewPort[0]), str(self.viewPort[1]), str(self.viewPort[2]), str(self.viewPort[3]))) + '\" preserveAspectRatio=\"xMinYMin\">'
                          '\n<defs></defs>'
                          '\n<title>' + self.title + '-' + str(filenum) + '</title>')

        # Header SVG container
        song_header = ('\n<svg x=\"' + '%.2f'%self.viewPortMargins[0] + '\" y=\"' + '%.2f'%self.viewPortMargins[1] + \
                       '\" width=\"' + '%.2f'%(self.viewPort[2]-self.viewPortMargins[0]) + '\" height=\"' + '%.2f'%(self.viewPort[3]-self.viewPortMargins[1]) + '\">')
        
        x = 0
        y = self.text_height # Because the origin of text elements of the bottom-left corner

        if filenum==0:
            song_header += '\n<text x=\"' + str(x) + '\" y=\"' + str(y) + '\" class=\"title\">' + self.title + '</text>'
            for i in range(len(self.headers[0])):
                y += 2*self.text_height
                song_header += '\n<text x=\"' + str(x)  + '\" y=\"' + str(y)  + '\" class=\"headers\">' + self.headers[0][i] + ' ' + self.headers[1][i] + '</text>'
        else:
            song_header += '\n<text x=\"' + str(x) + '\" y=\"' + str(y) + '\" class=\"title\">' + self.title + ' (page ' + str(filenum+1) + ')</text>'
            
        # Dividing line
        y += self.text_height
        song_header += ('\n<svg x=\"0" y=\"' + '%.2f'%y + '\" width=\"' + '%.2f'%(self.viewPort[2]-self.viewPortMargins[0]) + '\" height=\"' + '%.2f'%(self.harp_Yspacing/2.0) + '\">'
                        '\n<line x1=\"0\" y1=\"50%\" x2=\"100%\" y2=\"50%\" class=\"divide\"/>'
                        '\n</svg>')
        y += self.text_height
        
        song_header += '\n</svg>'

        svg_file.write(song_header)

        # Song SVG container
        ysong = y
        song_render = '\n<svg x=\"' + '%.2f'%self.viewPortMargins[0] + '\" y=\"' + '%.2f'%y + '\" width=\"' + '%.2f'%(self.viewPort[2]-self.viewPortMargins[0]) + '\" height=\"' + '%.2f'%(self.viewPort[3]-y) + '\" class=\"song\">'
        y = 0 #Because we are nested in a new SVG
        x = 0
        
        #TODO: check height instead of defining max row per line
        instrument_index = 0
        #end_row = min(start_row+self.maxLinesPerFile,len(self.lines))
        end_row = len(self.lines)
        for row in range(start_row, end_row):
            
            line = self.get_line(row)
            linetype = line[0].get_instrument_type()
            ncols = len(line)
            nsublines = int(1.0*ncols/self.maxIconsPerLine)
            
            if linetype == 'voice':
                ypredict = y + ysong + (self.text_height+self.harp_Yspacing/2.0)*(nsublines+1) + self.harp_Yspacing/2.0
            else:
                ypredict = y + ysong + (self.harp_height+self.harp_Yspacing)*(nsublines+1) + self.harp_Yspacing/2.0
                       
            if ypredict > (self.viewPort[3]-self.viewPortMargins[1]):
                end_row = row
                break
           
            line_render = ''
            sub_line = 0
            x = 0
            
            # Line SVG container            
            if linetype == 'voice':
                song_render += '\n<svg x=\"0" y=\"' + '%.2f'%y + '\" width=\"' + '%.2f'%(self.viewPort[2]-self.viewPortMargins[0]) + '\" height=\"' + '%.2f'%self.text_height + '\" class=\"instrument-line line-' + str(row) + '\">' #TODO: modify height              
                y += self.text_height + self.harp_Yspacing/2.0
            else:
                # Dividing line
                y += self.harp_Yspacing/4.0
                song_render += '\n<svg x=\"0" y=\"' + '%.2f'%y + '\" width=\"' + '%.2f'%(self.viewPort[2]-self.viewPortMargins[0]) + '\" height=\"' + '%.2f'%(self.harp_Yspacing/2.0) + '\">'              
                song_render += '\n<line x1=\"0\" y1=\"50%\" x2=\"100%\" y2=\"50%\" class=\"divide\"/>'
                song_render += '\n</svg>'
                y += self.harp_Yspacing/4.0
                
                y += self.harp_Yspacing/2.0
                song_render += '\n<svg x=\"0" y=\"' + '%.2f'%y + '\" width=\"' + '%.2f'%(self.viewPort[2]-self.viewPortMargins[0]) + '\" height=\"' + '%.2f'%self.harp_height + '\" class=\"instrument-line line-' + str(row) + '\">'            
                y += self.harp_height + self.harp_Yspacing/2.0
                
 
            for col in range(ncols):
                
                instrument = self.get_instrument(row,col)
                instrument.set_index(instrument_index)
                
                # Creating a new line if max number is exceeded
                if (int(1.0*col/self.maxIconsPerLine) - sub_line) > 0:
                    line_render += '\n</svg>'
                    sub_line += 1
                    x = 0
                    #print('max reached at row=' + str(row) + ' col=' + str(col)) 
                    # New Line SVG placeholder
                    if linetype == 'voice':
                         #TODO: check text height and position
                        line_render += '\n<svg x=\"0" y=\"' + '%.2f'%y + '\" width=\"' + '%.2f'%self.line_width + '\" height=\"' + '%.2f'%self.text_height + '\" class=\"instrument-line line-' + str(row) + '-' + str(sub_line) + '\">'
                        y += self.text_height + self.harp_Yspacing/2.0
                    else:
                        y += self.harp_Yspacing/2.0
                        line_render += '\n<svg x=\"0" y=\"' + '%.2f'%y + '\" width=\"' + '%.2f'%self.line_width + '\" height=\"' + '%.2f'%self.harp_height + '\" class=\"instrument-line line-' + str(row) + '-' + str(sub_line) + '\">'          
                        y += self.harp_height + self.harp_Yspacing/2.0
 
                # INSTRUMENT RENDER
                instrument_render = instrument.render_in_svg(x, '%.2f'%(100.0*self.harp_width/self.line_width)+'%', '100%', self.harp_AspectRatio, render_mode)
                if instrument.get_repeat()>0:
                    instrument_render += '\n<svg x=\"' + '%.2f'%(x+self.harp_width) + '\" y=\"0%\" class=\"repeat\" width=\"' + '%.2f'%(100.0*self.harp_width/self.line_width)+'%' + '\" height=\"100%\">'
                    instrument_render += '\n<text x=\"2%\" y=\"98%\" class=\"repeat\">x' + str(instrument.get_repeat()) + '</text></svg>'
                    x += self.harp_Xspacing
               
                line_render += instrument_render
                instrument_index += 1              
                x += self.harp_width + self.harp_Xspacing
                  
            song_render += line_render
            song_render += '\n</svg>' # Close line SVG        
               
        song_render += '\n</svg>' # Close song SVG
        svg_file.write(song_render) 
            
        svg_file.write('\n</svg>') # Close file SVG
        
        #Open new file
        #TODO: build array of file paths
        if end_row < len(self.lines):
            #print('reached row ' + str(end_row) + 'out of ' + str(len(self.lines)) + ':creating new file #' + str(filenum+1))
            filenum, file_path = self.write_svg(file_path0, render_mode, embed_css, css_path, end_row, filenum+1) 
        
        return filenum, file_path
