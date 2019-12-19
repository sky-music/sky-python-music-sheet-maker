import os

try:
    from PIL import Image, ImageDraw, ImageFont
    no_PIL_module = False
except (ImportError,ModuleNotFoundError):
    no_PIL_module = True

from notes import Note, NoteRoot, NoteCircle, NoteDiamond
from modes import RenderModes
### Instrument classes

class Instrument:
    
    def __init__(self):
        self.type = 'undefined'
        self.chord_skygrid = {}
        self.repeat = 1
        self.index = 0
        self.is_silent = True
        self.is_broken = False
        self.empty_chord_png = os.path.normpath('elements/empty-chord.png') #blank harp
        self.unhighlighted_chord_png = os.path.normpath('elements/unhighlighted-chord.png') # harp with unhighlighted notes
        self.broken_png = os.path.normpath('elements/broken-symbol.png')
        self.silent_png = os.path.normpath('elements/silent-symbol.png')
        self.png_chord_size = None
        self.text_bkg = (255, 255, 255, 0) # Transparent white
        self.song_bkg = (255, 255, 255) #White paper sheet
        self.font_color = (0, 0, 0)
        self.font = 'fonts/NotoSansCJKjp-Regular.otf'  
        self.font_size = 38
        self.repeat_height = None
                   
    def set_chord_skygrid(self, chord_skygrid):
        self.chord_skygrid = chord_skygrid

    def get_chord_skygrid(self):
        '''Returns the dictionary for the chord:
            where each key is the note position (tuple of row/index),
            the value is a dictionary with key=frame, value=True/False,
            where True/False means whether the note is played or not.
            Inactive notes are actually not in the dictionary at all.
            Example: {(0,0):{0:True}, (1,1):{0:True}}
        '''
        return self.chord_skygrid

    def get_type(self):
        return self.type
        
    def set_repeat(self, repeat):
        self.repeat = repeat

    def get_repeat(self):
        '''Returns the number of times the chord must be played'''
        return self.repeat

    def set_index(self, index):
        self.index = index

    def get_index(self):
        '''Instrument index in the song'''
        return self.index
     
    def get_is_silent(self):
        '''Returns whether the Harp is empty of notes (silent)'''
        return self.is_silent

    def get_is_broken(self):
        '''Returns whether the Harp is broken (notes were not recongized by the Parser)'''
        return self.is_broken

    def set_is_broken(self, is_broken=True):
        '''Returns a boolean whether the harp could be translated'''
        self.is_broken = is_broken

    def set_is_silent(self, is_silent=True):
        '''Returns a boolean whether the harp is empty in this frame'''
        self.is_silent = is_silent        
   
    def set_png_chord_size(self):
        ''' Sets the size of the chord image from the .png file '''
        if self.png_chord_size == None:
            self.png_chord_size =  Image.open(self.unhighlighted_chord_png).size

    def get_png_chord_size(self):
        ''' Returns the size of the chord image, or sets it if None '''
        if self.png_chord_size == None:
            self.set_png_chord_size()
        return self.png_chord_size
        
    def get_repeat_png(self, max_rescaled_width, rescale=1):
        '''Returns an image of the repeat number xN'''
        repeat_im = Image.new('RGBA',(int(max_rescaled_width/rescale), int(self.get_png_chord_size()[1])), color=self.text_bkg)
        draw = ImageDraw.Draw(repeat_im)
        fnt = ImageFont.truetype(self.font, self.font_size)
        draw.text((0,repeat_im.size[1]-1.05*fnt.getsize(str(self.repeat))[1]), 'x'+str(self.repeat), font=fnt, fill=self.font_color)
        
        if rescale != 1:
            repeat_im = repeat_im.resize((int(repeat_im.size[0]*rescale),int(repeat_im.size[1]*rescale)),resample=Image.LANCZOS)
        
        return repeat_im        
        

class Voice(Instrument): # Lyrics or comments
    
    def __init__(self):
        super().__init__()
        self.type = 'voice'
        self.lyric = ''
        #self.text_bkg = (255, 255, 255, 0)#Uncomment to make it different from the inherited class
        #self.font_color = (255,255,255)#Uncomment to make it different from the inherited class
        self.font = 'fonts/NotoSansCJKjp-Regular.otf'  
        self.font_size = 32
        self.lyric_height = None
        self.lyric_width = None
        
    def render_in_html(self, note_width):
        '''Renders the lyrics text in HTML inside an invisible table'''
        chord_render = '<table class=\"voice\">'
        chord_render +='<tr>'
        chord_render +='<td>'
        chord_render += self.lyric
        chord_render += '</td>'
        chord_render +='</tr>'
        chord_render +='</table>'
        return chord_render
    
    def get_lyric(self):
        return self.lyric
    
    def set_lyric(self, lyric):
        self.lyric = lyric

    def __len__(self):
        return len(self.lyric)
    
    def __str__(self):
        return '<' + self.type + '-' + str(self.index) + ', ' + str(len(self)) + ' chars, repeat=' + str(self.repeat) + '>'


    def render_in_ascii(self, render_mode):     
        chord_render = '#' + self.lyric + ' ' # Lyrics marked as comments in output text files
        return chord_render
            
    def get_lyric_height(self):
        '''Calculates the height of the lyrics based on a standard text and the font size'''
        if self.lyric_height == None:
           fnt = ImageFont.truetype(self.font, self.font_size)
        return fnt.getsize('HQfgjyp')[1]
    
    def render_in_svg(self, x, width, height, aspect_ratio):
        '''Renders the lyrics text in SVG'''
        voice_render = '\n<svg x=\"' + '%.2f'%x + '\" y=\"0\" width=\"100%\" height=\"' + height + '\" class=\"voice voice-' + str(self.get_index()) + '\">'
        voice_render += '\n<text x=\"0%\" y=\"50%\" class=\"voice voice-' + str(self.get_index()) + '\">' + self.lyric + '</text>'
        voice_render += '\n</svg>'
        return voice_render

    def render_in_png(self, rescale=1.0):    
        '''Renders the lyrics text in PNG'''
        chord_size = self.get_png_chord_size()
        lyric_im = Image.new('RGBA',(int(chord_size[0]),int(self.get_lyric_height())), color=self.text_bkg)
        draw = ImageDraw.Draw(lyric_im)     
        fnt = ImageFont.truetype(self.font, int(self.font_size))
        lyric_width = fnt.getsize(self.lyric)[0]
        draw.text((int((chord_size[0]-lyric_width)/2.0),0), self.lyric, font=fnt, fill=self.font_color)

        if rescale != 1:
            lyric_im = lyric_im.resize((int(lyric_im.size[0]*rescale),int(lyric_im.size[1]*rescale)), resample=Image.LANCZOS)
        
        return lyric_im

class Harp(Instrument):

    def __init__(self):
        super().__init__()
        self.type = 'harp'
        self.column_count = 5
        self.row_count = 3
        #self.highlighted_states_skygrid = []      

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
    
    def get_num_highlighted(self):
        num = 0
        for k in self.chord_skygrid.keys():
            for kk in self.chord_skygrid[k].keys():
                if self.chord_skygrid[k][kk] == True:
                    num +=1
        return num

    def __len__(self):
        return self.column_count*self.row_count
    
    def __str__(self):
        return '<' + self.type + '-' + str(self.index) + ', ' + str(len(self)) + ' notes, ' + \
               str(self.get_num_highlighted()) + ' highlighted, repeat=' + str(self.repeat) + '>'
    
    
    def get_note_from_position(self, pos):
        '''Returns the note type Root, Diamond, Circle from the position in Sky grid'''
        # Calculate the note's overall index in the harp (0 to 14)              
        note_index = (pos[0] * self.get_column_count()) + pos[1]
        
        if note_index % 7 == 0: #the 7 comes from the heptatonic scale of Sky's music (no semitones)
            # Note is a root note
            return NoteRoot(self, pos) #very important: the chord creating the note is passed as a parameter
        elif (note_index % self.get_column_count() == 0 or note_index % self.get_column_count() == 2) or note_index % self.get_column_count() == 4:
            # Note is in an odd column, so it is a circle
            return NoteCircle(self, pos)
        else:
            # Note is in an even column, so it is a diamond
            return NoteDiamond(self, pos)
         

    def render_in_ascii(self, render_mode=RenderModes.SKYASCII):
        
        ascii_chord = ''
        if render_mode == RenderModes.SKYASCII:
            inverse_map = self.sky_inverse_position_map
        elif render_mode == RenderModes.WESTERNASCII:
            inverse_map = self.western_inverse_position_map
        elif render_mode == RenderModes.JIANPUASCII:
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

                note = self.get_note_from_position((row, col))

                note_render = note.render_in_html(note_width)
                harp_render += note_render
                harp_render += '</td>'

            harp_render += '</tr>'

        harp_render += '</table>'
        
        if self.get_repeat() > 1:
            harp_render += '<table class=\"harp-' + str(self.get_index()) + ' repeat\">'
            harp_render += '<tr>'
            harp_render += '<td>'
            harp_render += 'x' + str(self.get_repeat())       
            harp_render += '</td>'
            harp_render += '</tr>'
            harp_render += '</table>'
        
        return harp_render


    def render_in_svg(self, x, harp_width, harp_height, aspect_ratio):
              
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
                
                note = self.get_note_from_position((row, col))                
                #note.set_position(row, col)
                 
                note_width = 0.21
                xn = 0.12 + col*(1-2*0.12)/(self.get_column_count()-1)-note_width/2.0
                yn = 0.15 + row*(1-2*0.16)/(self.get_row_count()-1)-note_width/2.0
                
                #NOTE RENDER
                note_render = note.render_in_svg('%.2f'%(100*note_width)+'%', '%.2f'%(100*xn)+'%', '%.2f'%(100*yn)+'%')                                
                
                harp_render += note_render
            
        harp_render += '</svg>'
        
        return harp_render
    
      
    def render_in_png(self, rescale=1.0):    
        def trans_paste(bg, fg, box=(0,0)):
            if fg.mode == 'RGBA':
                if bg.mode != 'RGBA':
                    bg = bg.convert('RGBA')
                fg_trans = Image.new('RGBA', bg.size)
                fg_trans.paste(fg,box,mask=fg)#transparent foreground
                return Image.alpha_composite(bg,fg_trans)
            else:
                 if bg.mode == 'RGBA':
                    bg = bg.convert('RGB')
                 bg.paste(fg, box)
                 return bg    
        
        harp_silent = self.get_is_silent()
        harp_broken = self.get_is_broken()
               
        harp_file =  Image.open(self.unhighlighted_chord_png) #loads default harp image into memory
        harp_size = harp_file.size
        
        harp_render = Image.new('RGB', harp_file.size, self.song_bkg) #Empty image
        
        # Get a typical note to check that the size of the note png is consistent with the harp png                  
        note_size = Note(self).get_png_size()
        note_rel_width = note_size[0]/harp_size[0] #percentage of harp 
        if note_rel_width > 1.0/self.get_column_count() or note_rel_width < 0.05:
            note_rescale = 0.153/(note_rel_width)
        else:
            note_rescale = 1
        
        if harp_broken: #'?' in the middle of the image (no harp around)
             symbol = Image.open(self.broken_png)
             harp_render = trans_paste(harp_render, symbol,(int((harp_size[0]-symbol.size[0])/2.0),int((harp_size[1]-symbol.size[1])/2.0)))
        elif harp_silent: #'.' in the middle of the image (no harp around)
             symbol = Image.open(self.silent_png)      
             harp_render = trans_paste(harp_render, symbol,(int((harp_size[0]-symbol.size[0])/2.0),int((harp_size[1]-symbol.size[1])/2.0)))
        else:
            harp_render = trans_paste(harp_render, harp_file) #default harp image
            for row in range(self.get_row_count()):
                 for col in range(self.get_column_count()):
                    
                    note = self.get_note_from_position((row, col))                
                    #note.set_position(row, col)
                                         
                    #NOTE RENDER
                    if len(note.get_highlighted_frames()) > 0: #Only paste highlighted notes
                        xn = (0.13 + col*(1-2*0.13)/(self.get_column_count()-1))*harp_size[0] - note_size[0]/2.0
                        yn = (0.17 + row*(1-2*0.17)/(self.get_row_count()-1))*harp_size[1] - note_size[1]/2.0
                        note_render = note.render_in_png(note_rescale)
                        harp_render = trans_paste(harp_render, note_render, (int(round(xn)),int(round(yn))))
        
        if rescale != 1:
            harp_render = harp_render.resize((int(harp_render.size[0]*rescale),int(harp_render.size[1]*rescale)), resample=Image.LANCZOS)
            
        return harp_render
