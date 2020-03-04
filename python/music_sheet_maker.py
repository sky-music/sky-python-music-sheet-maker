import os,io,re
from modes import InputMode, CSSMode, RenderMode
from communicator import Communicator
from parsers import SongParser
from songs import Song


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
        self.song = 0  # TODO reset song to None after debugging tests
        self.parser = None
        self.directory_base = os.path.normpath(os.path.join(os.getcwd(),'../'))
        self.song_dir_in = os.path.join(self.directory_base,songs_in)
        self.song_dir_out = os.path.join(self.directory_base,songs_out)
        self.init_working_directory()
        #TODO: create output directory if doesnt exist => create set/get method
        self.css_path = "css/main.css"#TODO: move that into Renderer
        self.css_mode = CSSMode.EMBED#TODO: move that into Renderer
        self.render_modes_enabled = [mode for mode in RenderMode]
        # self.render_modes_disabled = [RenderMode.JIANPUASCII, RenderMode.DOREMIASCII]
        self.render_modes_disabled = []
        self.render_modes_enabled = [mode for mode in self.render_modes_enabled if
                                     mode not in self.render_modes_disabled]

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

    def is_render_mode_enabled(self, mode):

        if mode in self.render_modes_enabled:
            return True
        else:
            return False
    
    def receive(self, *args, **kwargs):
        self.communicator.receive(*args, **kwargs)

    def execute_queries(self, queries=None):

        if queries is None:
            self.communicator.memory.clean()
            queries = self.communicator.memory.recall_unsatisfied(filters=('to_me'))
        else:
            if not isinstance(queries, (list, tuple)):
                queries = [queries]
        print('\n%%%%I AM MAKER, MY UNSATISFIED QUERIES ARE:%%%%')
        self.communicator.memory.print_out(filters=('to_me'))

        reply_valid = False
        while not reply_valid:
            for q in queries:
                try:
                    query_name = q.get_result()

                    stock_query = self.communicator.query_stock[query_name]

                    result = eval('self.' + stock_query['handler'] + '(sender=q.get_sender())')
                    q.reply_to(result)
                    reply_valid = q.get_reply_validity()

                except KeyError:
                    raise MusicMakerError('Unknown query ' + repr(query_name))
                    pass

    def create_song(self, **kwargs):
        """
        A very linear, sesuential way of building a song from user inputs
        TODO: implement nonlinear parsing using prerequisites?

        """
        try:
            recipient = kwargs['sender']
        except KeyError:
            raise MusicMakerError('No recipient specified for the Song')
            
        self.init_working_directory()
        #os.chdir(self.get_directory_base())
        
        if self.song is not None:
            # q  = self.communicator.query_song_overwrite(recipient=recipient)
            q_overwrite = self.communicator.send_stock_query('song_overwrite', recipient=recipient)
            # print('%%%%%DEBUG')
            # print(recipient)
            recipient.execute_queries()
            # print('%%%%%DEBUG, Reply RESULT')
            if q_overwrite.get_reply().get_result() == False:
                i = self.communicator.tell(string='Aborting.', recipient=recipient)
                recipient.execute_queries()
                return
                # TODO: return old song?
                # TODO reply None to song_creation query so that it gets satisfied and the loop ends
                # return something, a Reply or  do Query.reply_to if it has been passed as argument

        self.set_parser(SongParser(self))

        # Display instructions
        i_instructions = self.communicator.send_stock_query('instructions', recipient=recipient)
        recipient.execute_queries(i_instructions)

        # Ask for notes
        notes = self.ask_notes(recipient=recipient)
      
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
        
        buffers = self.write_song_to_buffers(RenderMode.PNG)
        file_paths = self.build_file_paths(RenderMode.PNG, len(buffers))
        self.write_buffers_to_files(buffers, file_paths)
        
        #TODO: render song
        #TODO: answer to query 
        #self.send_song(recipient=recipient)
        # err=self.calculate_error_ratio()
        # i_errors = self.communicator.send_stock_query('information', recipient=recipient, question=str(err))

        # self.send_song(query,recipient)     

    def ask_song_metadata(self, recipient):

        # TODO: Remember metadata so that, if parsing fails the questions are not asked again

        queries = []

        queries += [self.communicator.send_stock_query('song_title', recipient=recipient)]
        queries += [self.communicator.send_stock_query('original_artist', recipient=recipient)]
        queries += [self.communicator.send_stock_query('transcript_writer', recipient=recipient)]

        recipient.execute_queries(queries)

        result = [q.get_reply().get_result() for q in queries]

        return tuple(result)

    def ask_notes(self, recipient):

        # TODO: ask for notes, check for file, etc
        # communicator.ask_first_line()
        # fp = self.load_file(self.get_song_dir_in(), first_line)  # loads file or asks for next line
        # song_lines self.read_lines(first_line, fp)
        q_notes = self.communicator.send_stock_query('song_notes', recipient=recipient)
        recipient.execute_queries(q_notes)

        return q_notes.get_reply().get_result()

    def ask_input_mode(self, recipient, notes):

        possible_modes = self.get_parser().get_possible_modes(notes)

        # Ask for musical notation
        # modes_list = [InputMode.JIANPU, InputMode.SKY]
        q_mode = self.communicator.send_stock_query('musical_notation', recipient=recipient, limits=possible_modes)
        recipient.execute_queries(q_mode)

        result = q_mode.get_reply().get_result()
        
        return result

    def ask_song_key(self, recipient, notes, input_mode):
        # asks for song key
        # possible_keys = ['do', 're']
        """
        Attempts to detect key for input written in absolute musical scales (western, Jianpu)
        """
        # TODO:
        if input_mode in [InputMode.ENGLISH, InputMode.DOREMI, InputMode.JIANPU]:
            
            possible_keys = self.get_parser().find_key(notes)
            
            if len(possible_keys) == 0:
                self.communicator.tell(string="\nYour song cannot be transposed exactly in Sky.", recipient=recipient)
                # trans = input('Enter a key or a number to transpose your song within the chromatic scale:')
                self.communicator.tell(string="\nDefault key will be set to C.", recipient=recipient)

                song_key = 'C'

            elif len(possible_keys) == 1:
                song_key = str(possible_keys[0])
                self.communicator.tell(
                    string="\nYour song can be transposed in Sky with the following key: " + song_key,
                    recipient=recipient)
                    
            else:
                q_key = self.communicator.send_stock_query('possible_keys', recipient=recipient,
                                                           foreword="\nYour song can be transposed in Sky with the following keys: " + ','.join(
                                                               possible_keys), limits=possible_keys)
                recipient.execute_queries(q_key)

                song_key = q_key.get_reply().get_result()

        else:
            song_key = 'C'
        # song_key
        # TODO: create stock query for this one
        # q_key = self.communicator.send_stock_query('text', recipient=recipient, foreword="\Recommended key to play the visual pattern: ",limits=possible_keys)

        return song_key
                
        
    def send_song(self, recipient):
        
        pass
        
        
    def calculate_error_ratio(self):
        #TODO: use queries
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
        Writes the content of an IOString or IOBytes buffer list to one or several files
        """
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
                            1] + ' and ' + os.path.split(file_paths)[-1])
            
        return i

    def write_song_to_buffers(self, render_mode):
        """
        Writes the song to files with different formats as defined in RenderMode
        """
        #TODO: Move this method to Renderer?
        if render_mode in self.get_render_modes_enabled():

            if render_mode == RenderMode.HTML:
                buffers = [self.get_song().write_html(self.get_css_mode(), self.get_css_path())]
            elif render_mode == RenderMode.SVG:
                buffers = self.get_song().write_svg(self.get_css_mode(), self.get_css_path())
            elif render_mode == RenderMode.PNG:
                buffers = self.get_song().write_png()
            elif render_mode == RenderMode.MIDI:
                buffers = [self.get_song().write_midi()]
            else:  # Ascii
                buffers = self.get_song().write_ascii(render_mode)

        else:
            buffers = []
            
        for buffer in buffers:
            buffer.seek(0)

        return buffers
    
    def build_file_paths(self, render_mode, numfiles):

        if numfiles == 0:
            return None
            
        file_base = os.path.join(self.song_dir_out, self.get_song().get_title())
        file_ext = render_mode.value[2]
        #TODO create output directory if it doesn't exist
        
        file_paths = []
        if numfiles > 1:
            for i in range(numfiles):
                file_paths += [file_base + str(i) + file_ext]
        else:
            file_paths = [file_base + file_ext]

        return file_paths
            
#            file_ext = render_mode.value[2]
#            file_path0 = os.path.join(self.get_song_dir_out(), self.get_song().get_title() + file_ext)
#
#            try:
#                file_path = self.write_buffer_to_file(buffer_list, file_path0)
#
#                if numfiles > 1:
#                    self.output('Your song in ' + render_mode.value[1] + ' is located in: ' + self.get_song_dir_out())
#                    self.output(
#                        'Your song has been split into ' + str(numfiles) + ' between ' + os.path.split(file_path0)[
#                            1] + ' and ' + os.path.split(file_path)[1])
#                else:
#                    self.output('Your song in ' + render_mode.value[1] + ' is located at:' + file_path)
#            except (OSError, IOError):
#                self.output('Could not write to ' + render_mode.value[1] + ' file.')
#            self.output('------------------------------------------')

