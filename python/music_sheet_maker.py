import os, io, re
from modes import InputMode, CSSMode, RenderMode
from communicator import Communicator, QueriesExecutionAbort
from parsers import SongParser
#from songs import Song


class MusicSheetMakerError(Exception):
    def __init__(self, explanation):
        self.explanation = explanation

    def __str__(self):
        return str(self.explanation)
    
    pass


class MusicSheetMaker:

    def __init__(self, songs_in='test_songs', songs_out='songs_out'):
        self.name = 'music-sheet-maker'
        self.communicator = Communicator(owner=self)
        self.song = None
        self.parser = None
        #self.directory_base = os.path.normpath(os.path.join(os.getcwd(),'../'))
        self.directory_base = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
        self.song_dir_in = os.path.join(self.directory_base,songs_in)
        self.song_dir_out = os.path.join(self.directory_base,songs_out)
        self.css_path = os.path.normpath(os.path.join(self.directory_base, "css/main.css"))#TODO: move that into Renderer
        self.rel_css_path = os.path.relpath(self.css_path, start=self.song_dir_out)
        self.css_mode = CSSMode.EMBED#TODO: move that into Renderer
        self.render_modes_enabled = [mode for mode in RenderMode]
        # self.render_modes_disabled = [RenderMode.JIANPUASCII, RenderMode.DOREMIASCII]
        self.render_modes_disabled = []
        self.render_modes_enabled = [mode for mode in self.render_modes_enabled if
                                     mode not in self.render_modes_disabled]
        self.discord_render_mode = RenderMode.PNG
        
    def __getattr__(self, attr_name):
        """
        Default function to call in case no one else is found.
        """
        if 'communicator' in self.__dict__.keys():
            return getattr(self.communicator, attr_name)
        else:
            raise AttributeError("type object " + repr(type(self).__name__) + " has no attribute 'communicator")

    def get_name(self):
        return self.name

    def is_botcog(self, recipient):       
        try:
            recipient.bot
            return True
        except AttributeError:
            return False

    def is_commandline(self, recipient): 
        try:
            return recipient.get_name() == "command-line"
        except AttributeError:
            return False

    def is_website(self, recipient):
        is_website = False
        try:
            is_website = recipient.get_name() == "sky-music-website"
        except AttributeError:
            if not self.is_botcog(recipient) and not self.is_commandline(recipient):
                is_website = True
            else:
                is_website = False

        return is_website      

    def get_song(self):
        return self.song

    def set_song(self, song):
        self.song = song

    def get_parser(self):
        return self.parser

    def set_parser(self, parser):
        self.parser = parser

    def get_directory_base(self):
        return self.directory_base
    
    def get_render_modes_enabled(self):

        return self.render_modes_enabled


    def execute_queries(self, queries=None):

        if queries is None:
            self.communicator.memory.clean()
            queries = self.communicator.memory.recall_unsatisfied(filters=('to_me'))
        else:
            if not isinstance(queries, (list, tuple, set)):
                queries = [queries]
        #FIXME: 2 lines for debugging:
        #print('\n%%%%I AM MAKER, THE UNSATISFIED QUERIES ARE:%%%%')
        #self.communicator.memory.print_out(filters=('unsatisfied'))

        """
        The query statisfaction loop:
        runs until all queries are satisfied
        """
        reply_valid = False
        while not reply_valid:
            reply_valid = True #To break the loop if no query
            for q in queries:
                #Fetching the stock Query name and arguments 
                query_name = q.get_name()
                try:   
                    stock_query = self.communicator.query_stock[query_name]
                    handler_args = ', '.join(('sender=q.get_sender()','query=q'))
                    expression = 'self.' + stock_query['handler'] + '(' + handler_args + ')'
                except KeyError as err:
                    #TODO: handle non-stock queries???
                    raise MusicSheetMakerError('Cannot create stock query ' + repr(query_name) + ', because of ' + repr(err))
                    pass
                #Actual evaluation of the stock query
                try:
                    answer = eval(expression) 
                    q.reply_to(answer)
                    reply_valid = q.get_reply_validity()
                except QueriesExecutionAbort as qExecAbort:
                    raise qExecAbort

     
    def create_song(self, **kwargs):
        """
        A very linear, sequential way of building a song from user inputs
        TODO: Systematically pass pre-requisites queries in arguments
        TODO: implement nonlinear parsing using prerequisites?
        """
        try:
            recipient = kwargs['sender']
        except KeyError:
            raise MusicSheetMakerError('No recipient specified for the Song')

        #Actually the following is not used but it may be useful to have the triggering query as an argument
        try:
            q_create_song = kwargs['query']
        except KeyError:
            raise MusicSheetMakerError('No Query passed to create_song')
        
#        if self.song is not None:
#            q_overwrite = self.communicator.send_stock_query('song_overwrite', recipient=recipient)
#            recipient.execute_queries(q_overwrite)
#            overwrite = q_overwrite.get_reply().get_result()
#        else:
#            q_overwrite = self.communicator.send_information(recipient=recipient, string='Creating new song.')
#            recipient.execute_queries(q_overwrite)
#            overwrite = True
#            
#        if not overwrite:
#            
#            i = self.communicator.send_information(string='Aborting.', recipient=recipient)
#            recipient.execute_queries(i)
            
        #self.communicator.memory.erase(filters=('from_me'))
        
        
        #======= NEW SONG =======
        self.set_parser(SongParser(self))

        # Display instructions
        i_instr, res = self.ask_instructions(recipient=recipient)
    
        # Ask for notes
        #TODO: allow the player to enter the notes using several messages??? or maybe not
        if self.is_botcog(recipient):
            (q_notes, notes) = self.ask_notes(recipient=recipient, prerequisites=[i_instr])
        elif recipient.get_name() == 'command-line':
            (q_notes, notes) = self.ask_notes_file(recipient=recipient, prerequisites=[i_instr])
        else:
            (q_notes, notes) = self.ask_notes(recipient=recipient, prerequisites=[i_instr])
      
        (q_mode, input_mode) = self.ask_input_mode(recipient=recipient, notes=notes, prerequisites=[q_notes])
        self.get_parser().set_input_mode(input_mode)
        
        (q_key, song_key) = self.ask_song_key(recipient=recipient, notes=notes, input_mode=input_mode, prerequisites=[q_notes, q_mode])
        
        # Asks for octave shift
        q_shift = self.communicator.send_stock_query('octave_shift', recipient=recipient)
        recipient.execute_queries(q_shift)
        octave_shift = q_shift.get_reply().get_result()
        
        # Parse song
        self.set_song(self.get_parser().parse_song(notes, song_key, octave_shift))
        (i_error, res) = self.display_error_ratio(recipient=recipient, prerequisites=[q_notes, q_mode, q_shift])
        
        # Asks for song metadata
        (q_meta, (title, artist, transcript)) = self.ask_song_metadata(recipient=recipient)
        self.get_song().set_meta(title=title, artist=artist, transcript=transcript, song_key=song_key)

        if self.is_botcog(recipient) or self.is_website(recipient):
            
            self.css_mode = CSSMode.EMBED #Prevent the HTML/SVG from depending on an auxiliary .css file
            buffers = self.write_song_to_buffers(self.discord_render_mode)
            q_create_song.reply_to((self.discord_render_mode, buffers))
            answer = q_create_song
        
        else: #command line
            
            print("="*40)
            all_paths = []
            
            for render_mode in self.get_render_modes_enabled():
                buffers = self.write_song_to_buffers(render_mode)
                file_paths = self.build_file_paths(render_mode, len(buffers))              
                self.send_buffers_to_files(render_mode, buffers, file_paths, recipient=recipient, prerequisites=[i_error])
                all_paths += file_paths
            
            q_create_song.reply_to((self.get_render_modes_enabled(), all_paths))
            answer = q_create_song
            #TODO: decide what to reply instead
                
        return answer
    
   
    def ask_instructions(self, recipient, prerequisites=None, execute=True):
        
        question = '\nAccepted music notes formats:'
        for mode in InputMode:
            question += '\n* ' + mode.value[2]
        question += '\nNotes composing a chord must be glued together (e.g. A1B1C1).'
        question += '\nSeparate chords with \"' + self.get_parser().get_icon_delimiter() + '\".'
        question += '\nUse \"' + self.get_parser().get_pause() + '\" for a silence (rest).'
        question += '\nUse \"' + self.get_parser().get_quaver_delimiter() + '\" to link notes within an icon, for triplets, quavers... (e.g. ' + self.get_parser().get_quaver_delimiter().join(('A1','B1','C1'))
        question +=( '\nAdd \""' + self.get_parser().get_repeat_indicator() + '2\"" after a chord to indicate repetition.')
        question += '\nSharps # and flats b (semitones) are supported for Western and Jianpu notations.'
        
        if recipient.get_name() == 'command-line':        
            i_instructions = self.communicator.send_stock_query('instructions_stdout', recipient=recipient, question=question, prerequisites=prerequisites)
        else:
            i_instructions = self.communicator.send_stock_query('instructions', recipient=recipient, question=question, prerequisites=prerequisites)
        
        if execute:
            recipient.execute_queries(i_instructions)
            result = i_instructions.get_reply().get_result()
            return (i_instructions, result)
        else:
            return (i_instructions, None)
                                  
   
    def ask_song_metadata(self, recipient, prerequisites=None, execute=True):

        queries = []

        queries += [self.communicator.send_stock_query('song_title', recipient=recipient, prerequisites=prerequisites)]
        queries += [self.communicator.send_stock_query('original_artist', recipient=recipient, prerequisites=prerequisites)]
        queries += [self.communicator.send_stock_query('transcript_writer', recipient=recipient, prerequisites=prerequisites)]

        if execute:
            recipient.execute_queries(queries)
            result = [q.get_reply().get_result() for q in queries]
            return (queries, tuple(result))
        else:
            return (queries, None)

    def ask_notes(self, recipient, prerequisites=None, execute=True):
        
        q_notes = self.communicator.send_stock_query('song_notes', recipient=recipient, prerequisites=prerequisites)            
             
        if execute:
            recipient.execute_queries(q_notes)
            result = q_notes.get_reply().get_result()
            return (q_notes, result)
        else:
            return (q_notes, None)

    
    def ask_file(self, recipient, prerequisites=None, execute=True):
                   
        q_file = self.communicator.send_stock_query('song_file', question='Enter file name (in ' + os.path.relpath(os.path.normpath(self.song_dir_in)) + '/)',\
                                                    recipient=recipient, prerequisites=prerequisites, limits=(os.path.normpath(self.song_dir_in)))
        
        if execute:
            recipient.execute_queries(q_file)
            file_name = q_file.get_reply().get_result()
            file_path = os.path.join(self.song_dir_in, os.path.normpath(file_name))
            return (q_file, file_path) #should return file name
        else:
            return (q_file, None)
        
    
    def read_file(self, file_path):
        
        isfile = os.path.isfile(file_path)
        
        if not isfile:
            MusicSheetMakerError('File does not exist: ' + os.path.abspath(file_path))
        else:
            #load file
            try:
                with open(file_path, mode='r', encoding='utf-8', errors='ignore') as fp:
                    lines = fp.readlines()
            except (OSError, IOError) as err:
                #print('Error opening file: ' + os.path.abspath(file_path))
                raise err
                
            print('(Song imported from ' + os.path.abspath(file_path) + ')')
            return lines


    def ask_notes_file(self, recipient, prerequisites=None, execute=True):

        # TODO: Check for file, etc, distinguish Discord / command line to avoid loading a file on Discord
        q_notes = self.communicator.send_stock_query('song_notes_files', \
                                                     question='Type or copy-paste notes, or enter file name (in ' + os.path.relpath(os.path.normpath(self.song_dir_in)) + '/)',\
                                                     recipient=recipient, prerequisites=prerequisites)
        
        if not execute:            
            return (q_notes, None)      
        else:            
            recipient.execute_queries(q_notes)
            
            result = q_notes.get_reply().get_result()
            
            #Detects if the result is a file path
            file_path = os.path.join(self.song_dir_in, os.path.normpath(result))
            isfile = os.path.isfile(file_path)
            
            if not isfile:
                splitted = os.path.splitext(result)
                if len(splitted[0]) > 0 and 2 < len(splitted[1]) <= 5 and re.search('\\.', splitted[0]) is None:
                    # then certainly a file name
                    self.communicator.memory.erase(q_notes)
                                    
                    q_notes, file_path = self.ask_file(recipient=recipient, prerequisites=prerequisites, execute=execute)
                     
            if isfile:
                notes = self.read_file(file_path)
            else:
                notes = result
                    
            return (q_notes, notes)
                

    def ask_input_mode(self, recipient, notes, prerequisites=None, execute=True):
        """
        Try to guess the musical notation and ask the player to confirm
        """
        
        possible_modes = self.get_parser().get_possible_modes(notes)

        if len(possible_modes) == 0:
            #To avoid loopholes. I am not sure this case is ever reached, because get_possible_modes should return all modes if None is found.
            all_input_modes = [mode for mode in InputMode]
            
            q_mode = self.communicator.send_stock_query('musical_notation', recipient=recipient,
            foreword = '\nCould not detect your note format. Maybe your song contains typo errors?',
            limits=all_input_modes, prerequisites=prerequisites)
            
        elif len(possible_modes) == 1:
            q_mode = self.communicator.send_information(recipient=recipient, \
                                                        string='\nWe detected that you use the following notation: ' + possible_modes[0].value[1] + '.', \
                                                        prerequisites=prerequisites)
            
        else:
            q_mode = self.communicator.send_stock_query('musical_notation', recipient=recipient, limits=possible_modes, prerequisites=prerequisites)
        
        if execute:
            recipient.execute_queries(q_mode) 
            if len(possible_modes) == 1:
                result = possible_modes[0]
            else:
                result = q_mode.get_reply().get_result()
            return (q_mode, result)
        else:
            return (q_mode, None)


    def ask_song_key(self, recipient, notes, input_mode, prerequisites=None, execute=True):
        """
        Attempts to detect key for input written in absolute musical scales (western, Jianpu)
        """
        if input_mode in [InputMode.ENGLISH, InputMode.DOREMI, InputMode.JIANPU]:
            
            possible_keys = self.get_parser().find_key(notes)
            
            if len(possible_keys) == 0:
                q_key = self.communicator.send_information(string="\nYour song cannot be transposed exactly in Sky\nDefault key will be set to C.", \
                                                           recipient=recipient, prerequisites=prerequisites)
                possible_keys = ['C']
                # trans = input('Enter a key or a number to transpose your song within the chromatic scale:')                
            elif len(possible_keys) == 1:
                q_key = self.communicator.send_information(
                    string="\nYour song can be transposed in Sky with the following key: " + str(possible_keys[0]),
                    recipient=recipient, prerequisites=prerequisites)
            else:
                q_key = self.communicator.send_stock_query('possible_keys', recipient=recipient, \
                                                           foreword="\nYour song can be transposed in Sky with the following keys: " + ','.join(possible_keys), \
                                                           limits=possible_keys, prerequisites=prerequisites)
        else:
            q_key = self.communicator.send_stock_query('recommended_key', recipient=recipient, prerequisites=prerequisites)
            possible_keys = self.get_parser().find_key('') #should return None

        if execute:
            recipient.execute_queries(q_key)
            if possible_keys is None:
                song_key = q_key.get_reply().get_result()
                if len(song_key) == 0:
                    song_key = 'C'
            elif len(possible_keys) > 1:
                song_key = q_key.get_reply().get_result()
            elif len(possible_keys) == 1:
               song_key =  possible_keys[0]  
            else:
                raise MusicSheetMakerError('Possible keys is an empty list.')
                
            return (q_key, song_key)
        else:
            return (q_key, None)

        
    def send_buffers_to_discord(self, buffers, recipient, prerequisites=None, execute=True):
        '''
        Discord only
        TODO: fill this method, or if very short, put it inside create_song directly
        '''
        return buffers
        
        
    def display_error_ratio(self, recipient, prerequisites=None, execute=True):

        error_ratio = self.get_song().get_num_broken() / max(1, self.get_song().get_num_instruments())
        if error_ratio == 0:
            message = 'Song successfully read with no errors!'
        elif error_ratio < 0.05:
            message = 'Song successfully read with few errors!'
        else:
            message = '**WARNING**: Your song contains many errors. Please check the following:' + \
            '\n- All your notes are within octaves 4 and 6. If not, try again with an octave shift.' + \
            '\n- Your song is free of typos. Please check this website for full instructions: ' + \
            'https://sky.bloomexperiment.com/t/summary-of-input-modes/403'
            
        i_error = self.communicator.send_information(recipient=recipient, string=message, prerequisites=prerequisites)
       
        if execute:
            recipient.execute_queries(i_error)
            result = i_error.get_reply().get_result()
            return (i_error, result)
        else:
            return (i_error, None)
        

    def send_buffers_to_files(self, render_mode, buffers, file_paths, recipient, prerequisites=None, execute=True):
        """
        Writes the content of an IOString or IOBytes buffer list to one or several files.
        Command line only
        """
        #TODO: Move this method in Renderer???
        try:
            numfiles = len(buffers)
        except (TypeError, AttributeError):
            buffers = [buffers]
            numfiles = 1
        
        #Creates output directory if did not exist
        if not os.path.isdir(self.song_dir_out):
            os.mkdir(self.song_dir_out)

        if len(buffers) != len(file_paths):
            raise MusicSheetMakerError('inconsistent len gths of buffers and file_paths')

        (file_base, file_ext) = os.path.splitext(file_paths[0])

        for i, buffer in enumerate(buffers):

            if isinstance(buffer, io.StringIO):
                output_file = open(file_paths[i], 'w+', encoding='utf-8', errors='ignore')
            elif isinstance(buffer, io.BytesIO):
                output_file = open(file_paths[i], 'bw+')
            elif buffer is None:
                pass
            else:
                raise MusicSheetMakerError('Unknown buffer type in ' + str(self))
            
            
            if buffer is not None:
                output_file.write(buffer.getvalue())
            
                if numfiles == 1:
                    
                    message = '\nYour song in ' + render_mode.value[1] + ' is located at: ' + os.path.relpath(file_paths[0])
                    
                elif numfiles > 1 and i == 0:
                    
                    message = '\nYour song in ' + render_mode.value[1] + ' is located in: ' + os.path.relpath(self.song_dir_out)
                    
                    message += 'Your song has been split into ' + str(numfiles) + ' files between ' + os.path.split(file_paths[0])[
                                1] + ' and ' + os.path.split(file_paths[-1])[1]
            else:
                message = '\nYour song in ' + render_mode.value[1] + ' was not saved to file.'   

        i_song_files = self.communicator.send_stock_query('information', foreword="-"*40, \
                                                     question=message, recipient=recipient, prerequisites=prerequisites)    
        if execute:
            recipient.execute_queries(i_song_files)
            result = i_song_files.get_reply().get_result()
            return (i_song_files, result)
        else:
            return (i_song_files, None)

            
    def write_song_to_buffers(self, render_mode):
        """
        Writes the song to files with different formats as defined in RenderMode
        """
        #TODO: Move this method to Renderer?
        if render_mode in self.get_render_modes_enabled():

            if render_mode == RenderMode.HTML:
                buffers = [self.get_song().write_html(self.css_mode, self.css_path, self.rel_css_path)]
            elif render_mode == RenderMode.SVG:
                buffers = self.get_song().write_svg(self.css_mode, self.css_path, self.rel_css_path)
            elif render_mode == RenderMode.PNG:
                buffers = self.get_song().write_png()
            elif render_mode == RenderMode.MIDI:
                buffers = [self.get_song().write_midi()]
            else:  # Ascii
                buffers = [self.get_song().write_ascii(render_mode)]

        else:
            buffers = []
            
        for buffer in buffers:
            if buffer is not None:
                buffer.seek(0)

        return buffers
    
    def build_file_paths(self, render_mode, numfiles):
        '''
        Command line only : generates a list of file paths for a given input mode.
        '''
        #TODO: move this method in Renderer???
        if numfiles == 0:
            return None
            
        file_base = os.path.join(self.song_dir_out, self.get_song().get_title())
        file_ext = render_mode.value[2]
        
        file_paths = []
        if numfiles > 1:
            for i in range(numfiles):
                file_paths += [file_base + str(i) + file_ext]
        else:
            file_paths = [file_base + file_ext]

        return file_paths

