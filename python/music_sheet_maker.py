import os, io, re
from modes import InputMode, CSSMode, RenderMode
from communicator import Communicator
from parsers import SongParser
#from songs import Song


class MusicMakerError(Exception):
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
        self.directory_base = os.path.normpath(os.path.join(os.getcwd(),'../'))
        self.song_dir_in = os.path.join(self.directory_base,songs_in)
        self.song_dir_out = os.path.join(self.directory_base,songs_out)
        self.init_working_directory()
        self.css_path = os.path.normpath(os.path.join(self.directory_base, "css/main.css"))#TODO: move that into Renderer
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

    def get_song(self):
        return self.song

    def set_song(self, song):
        self.song = song

    def get_parser(self):
        return self.parser

    def set_parser(self, parser):
        self.parser = parser

    def init_working_directory(self):
        if not os.path.isdir(self.song_dir_out):
            os.mkdir(self.song_dir_out)

    def get_directory_base(self):
        return self.directory_base
    
    def get_render_modes_enabled(self):

        return self.render_modes_enabled

#    def is_render_mode_enabled(self, mode):
#    
#    def receive(self, *args, **kwargs):
#        self.communicator.receive(*args, **kwargs)

    def execute_queries(self, queries=None):

        if queries is None:
            self.communicator.memory.clean()
            queries = self.communicator.memory.recall_unsatisfied(filters=('to_me'))
        else:
            if not isinstance(queries, (list, tuple)):
                queries = [queries]
        print('\n%%%%I AM MAKER, THE UNSATISFIED QUERIES ARE:%%%%')
        self.communicator.memory.print_out(filters=('unsatisfied'))

        """
        The query statisfaction loop:
        runs until all queries are satisfied
        """
        reply_valid = False
        while not reply_valid:
            reply_valid = True #To break the loop if no query
            for q in queries:
                try:
                    query_name = q.get_name()
                    stock_query = self.communicator.query_stock[query_name]
                    handler_args = ', '.join(('sender=q.get_sender()','query=q'))
                    answer = eval('self.' + stock_query['handler'] + '(' + handler_args + ')')
                    q.reply_to(answer)
                    reply_valid = q.get_reply_validity()

                except KeyError:
                    #TODO: handle non-stock queries???
                    raise MusicMakerError('Unknown query ' + repr(query_name))
                    pass

    def create_song(self, **kwargs):
        """
        A very linear, sequential way of building a song from user inputs
        TODO: Systematically pass pre-requisites queries in arguments
        TODO: implement nonlinear parsing using prerequisites?
        """
        try:
            recipient = kwargs['sender']
        except KeyError:
            raise MusicMakerError('No recipient specified for the Song')

        #Actually the following is not used but it may be useful to have the triggering query as an argument
        try:
            creation_query = kwargs['query']
        except KeyError:
            raise MusicMakerError('No Query passed to create_song')
        
        if self.song is not None:
            q_overwrite = self.communicator.send_stock_query('song_overwrite', recipient=recipient)
            recipient.execute_queries()
            overwrite = q_overwrite.get_reply().get_result()
        else:
            overwrite = True
            
        if not overwrite:
            
            i = self.communicator.send_information(string='Aborting.', recipient=recipient)
            recipient.execute_queries(i)
            
        else:  #NEW SONG
            
            self.set_parser(SongParser(self))
    
            # Display instructions
            #TODO: add more explicit instructions, see Responder.py for an example
            #tricky part: generate the list of input modes
            i_instructions = self.communicator.send_stock_query('instructions', recipient=recipient)
            recipient.execute_queries(i_instructions)
    
            # Ask for notes
            #TODO: allow the player to enter the notes using several messages??? or maybe not
            if recipient.get_name() == 'music-cog':
                notes = self.ask_notes(recipient=recipient)
            else:
                notes = self.ask_notes_file(recipient=recipient)
          
            input_mode = self.ask_input_mode(recipient=recipient, notes=notes)
            self.get_parser().set_input_mode(input_mode)
            
            song_key = self.ask_song_key(recipient=recipient, notes=notes, input_mode=input_mode)
            
            #Asks for octave shift
            q_shift = self.communicator.send_stock_query('octave_shift', recipient=recipient)
            recipient.execute_queries(q_shift)
            octave_shift = q_shift.get_reply().get_result()
            
            # Parse song
            self.set_song(self.get_parser().parse_song(notes, song_key, octave_shift))
        
        #Asks for song metadata
        title, artist, writer = self.ask_song_metadata(recipient=recipient)
        
        #TODO:
        #Detect if on Discord or in commandn line with a safer method
        #Loop over rendering modes, several for the command line, 1 for discord
        if recipient.get_name() == 'music-cog':
            render_mode = self.discord_render_mode
            buffers = self.write_song_to_buffers(render_mode)
            
            #TODO: write this method:
            answer = self.send_buffers_to_discord(buffers=buffers, recipient=recipient)
        else:
            render_modes = self.get_render_modes_enabled()
            
            all_paths = []
            
            for render_mode in render_modes:
                buffers = self.write_song_to_buffers(render_mode)
                file_paths = self.build_file_paths(render_mode, len(buffers))
                self.write_buffers_to_files(buffers, file_paths)
                all_paths += file_paths
            
            answer = all_paths
            #TODO: decide what to reply
        
        return answer
        #TODO: display error ratio? or wait fo a query about it?
        # err=self.calculate_error_ratio()
        # i_errors = self.communicator.send_stock_query('information', recipient=recipient, question=str(err))
   

    def ask_song_metadata(self, recipient, prerequisites=None):

        # TODO: Remember metadata so that, if parsing fails the questions are not asked again?

        queries = []

        queries += [self.communicator.send_stock_query('song_title', recipient=recipient, prerequisites=prerequisites)]
        queries += [self.communicator.send_stock_query('original_artist', recipient=recipient, prerequisites=prerequisites)]
        queries += [self.communicator.send_stock_query('transcript_writer', recipient=recipient, prerequisites=prerequisites)]

        recipient.execute_queries(queries)

        result = [q.get_reply().get_result() for q in queries]

        return tuple(result)

    def ask_notes(self, recipient, prerequisites=None):
        
        q_notes = self.communicator.send_stock_query('song_notes', recipient=recipient, prerequisites=prerequisites)            
        recipient.execute_queries(q_notes)

        return q_notes.get_reply().get_result()

    def ask_notes_file(self, recipient, prerequisites=None):

        # TODO: Check for file, etc, distinguish Discord / command line to avoid loading a file on Discord
        q_notes = self.communicator.send_stock_query('song_notes_files', question='Type or copy-paste notes, or enter file name (in ' + os.path.normpath(self.song_dir_in) + '/)',recipient=recipient, prerequisites=prerequisites)
            #TODO: detect file name
            #create a new ReplyType?
            
        recipient.execute_queries(q_notes)
        
        result = q_notes.get_reply().get_result()
        
        #Detects if the result is a file path
        file_path = os.path.join(self.song_dir_in, os.path.normpath(result))
        isfile = os.path.isfile(file_path)
        
        if not isfile:
            splitted = os.path.splitext(result)
            if len(splitted[0]) > 0 and 2 < len(splitted[1]) <= 5 and re.search('\\.', splitted[0]) is None:
                # then probably a file name
                self.communicator.memory.erase(q_notes)
                
                q_file = self.communicator.send_stock_query('song_file', question='Enter file name (in ' + os.path.normpath(self.song_dir_in) + '/)',recipient=recipient, prerequisites=prerequisites, limits=os.path.normpath(self.song_dir_in))
            #TODO: detect file name
            #create a new ReplyType?
                recipient.execute_queries(q_file)
                
                result = q_file.get_reply().get_result()
                file_path = os.path.join(self.song_dir_in, os.path.normpath(result))
                isfile = os.path.isfile(file_path)
        
        if not isfile:
            return result
        else:
            #load file
            with open(file_path, mode='r', encoding='utf-8', errors='ignore') as fp:
                result = fp.readlines()
            return result
        

    def ask_input_mode(self, recipient, notes, prerequisites=None):
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
            recipient.execute_queries(q_mode)
            result = q_mode.get_reply().get_result()
            
        elif len(possible_modes) == 1:
            i_mode = self.communicator.send_information(recipient=recipient, string='\nWe detected that you use the following notation: ' + possible_modes[0].value[1] + '.', prerequisites=prerequisites)
            recipient.execute_queries(i_mode)
            result = possible_modes[0]
            
        else:
            q_mode = self.communicator.send_stock_query('musical_notation', recipient=recipient, limits=possible_modes, prerequisites=prerequisites)
            recipient.execute_queries(q_mode)
            result = q_mode.get_reply().get_result()
        
        return result

    def ask_song_key(self, recipient, notes, input_mode, prerequisites=None):
        """
        Attempts to detect key for input written in absolute musical scales (western, Jianpu)
        """
        # TODO:
        if input_mode in [InputMode.ENGLISH, InputMode.DOREMI, InputMode.JIANPU]:
            
            possible_keys = self.get_parser().find_key(notes)
            
            if len(possible_keys) == 0:
                i_C = self.communicator.send_information(string="\nYour song cannot be transposed exactly in Sky\nDefault key will be set to C.", recipient=recipient, prerequisites=prerequisites)
                # trans = input('Enter a key or a number to transpose your song within the chromatic scale:')
                recipient.execute_queries(i_C)

                song_key = 'C'

            elif len(possible_keys) == 1:
                song_key = possible_keys[0]
                i_key = self.communicator.send_information(
                    string="\nYour song can be transposed in Sky with the following key: " + str(song_key),
                    recipient=recipient, prerequisites=prerequisites)
                recipient.execute_queries(i_key)
            else:
                q_key = self.communicator.send_stock_query('possible_keys', recipient=recipient,
                                                           foreword="\nYour song can be transposed in Sky with the following keys: " + ','.join(
                                                               possible_keys), limits=possible_keys, prerequisites=prerequisites)
                recipient.execute_queries(q_key)

                song_key = q_key.get_reply().get_result()

        else:
            song_key = 'C'

        return song_key
                
        
    def send_buffers_to_discord(self, buffers, recipient):
        '''
        Discord only
        TODO: fill this method, or if very short, put it inside create_song directly
        '''
        pass
        
        
    def calculate_error_ratio(self):
        #TODO: use queries
        #TODO: use this method in create_song
        print('===========================================')
        error_ratio = self.get_song().get_num_broken() / max(1, self.get_song().get_num_instruments())
        if error_ratio == 0:
            print('Song successfully read with no errors!')
        elif error_ratio < 0.05:
            print('Song successfully read with few errors!')
        else:
            print('**WARNING**: Your song contains many errors. Please check the following:'
                        '\n- All your notes are within octaves 4 and 6. If not, try again with an octave shift.'
                        '\n- Your song is free of typos. Please check this website for full instructions: '
                        'https://sky.bloomexperiment.com/t/summary-of-input-modes/403')

    def write_buffers_to_files(self, buffers, file_paths):
        """
        Writes the content of an IOString or IOBytes buffer list to one or several files. command line only
        """
        #TODO: Move this method in Renderer???
        try:
            numfiles = len(buffers)
        except (TypeError, AttributeError):
            buffers = [buffers]
            numfiles = 1

        if len(buffers) != len(file_paths):
            raise MusicMakerError('inconsistent len gths of buffers and file_paths')

        (file_base, file_ext) = os.path.splitext(file_paths[0])

        for i, buffer in enumerate(buffers):

            if isinstance(buffer, io.StringIO):
                output_file = open(file_paths[i], 'w+', encoding='utf-8', errors='ignore')
            elif isinstance(buffer, io.BytesIO):
                output_file = open(file_paths[i], 'bw+')
            else:
                raise MusicMakerError('Unknown buffer type in ' + str(self))
            output_file.write(buffer.getvalue())
            
            print('\nYour song in ' + file_ext.upper() + ' is located in: ' + self.song_dir_out)
            
            if numfiles > 1:
                print('Your song has been split into ' + str(numfiles) + ' between ' + os.path.split(file_paths[0])[
                            1] + ' and ' + os.path.split(file_paths[-1])[1])
            
        return i

    def write_song_to_buffers(self, render_mode):
        """
        Writes the song to files with different formats as defined in RenderMode
        """
        #TODO: Move this method to Renderer?
        if render_mode in self.get_render_modes_enabled():

            if render_mode == RenderMode.HTML:
                buffers = [self.get_song().write_html(self.css_mode, self.css_path)]
            elif render_mode == RenderMode.SVG:
                buffers = self.get_song().write_svg(self.css_mode, self.css_path)
            elif render_mode == RenderMode.PNG:
                buffers = self.get_song().write_png()
            elif render_mode == RenderMode.MIDI:
                buffers = [self.get_song().write_midi()]
            else:  # Ascii
                buffers = [self.get_song().write_ascii(render_mode)]

        else:
            buffers = []
            
        for buffer in buffers:
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

