import os
from communicator import Communicator
from parsers import SongParser

class MusicMakerError(Exception):
    def __init__(self, explanation):
        self.explanation = explanation

    def __str__(self):
        return str(self.explanation)
    pass

class MusicSheetMaker:

    def __init__(self):
        self.name = 'music-sheet-maker'
        self.communicator = Communicator(owner=self)
        self.song = 0  # Song object
        self.parser = None
        self.init_working_directory()
        self.directory_base = os.getcwd()
        
        # self.parser = SongParser()

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

    def init_working_directory(self):

        os.chdir('../')
        #if not os.path.isdir(self.song_dir_out):
            #os.mkdir(self.song_dir_out)

    def receive(self, *args, **kwargs):
        self.communicator.receive(*args, **kwargs)


    def execute_queries(self, queries=None):
        
        if queries == None:
            self.communicator.memory.clean()
            queries = self.communicator.memory.recall_unsatisfied(filters=('to_me'))
        else:
            if not isinstance(queries,(list,tuple)):
                queries = [queries]
        print('\n%%%%I AM MAKER, MY UNSATISFIED QUERIES ARE:%%%%')
        self.communicator.memory.print_out(filters=('to_me'))
        for q in queries:
            try:
                query_name = q.get_result()
                #print('This one is unreplied to :+query_name')
                stock_query = self.communicator.stock_queries[query_name]
                #print('self.'+stock_query['handler']+'(sender='+q.get_sender().get_name()+')')
                result = eval('self.'+stock_query['handler']+'(sender=q.get_sender())')
                q.reply_to(result)
            except KeyError:
                raise MusicMakerError('Unknown query '+repr(query_name))
                pass

    def create_song(self, **kwargs):
        
        try:
            recipient = kwargs['sender']
        except KeyError:
            raise MusicMakerError('No recipient specified for the Song')
            
        if self.song is not None:
            #q  = self.communicator.query_song_overwrite(recipient=recipient)
            q = self.communicator.send_stock_query('song_overwrite', recipient=recipient)
            #print('%%%%%DEBUG')
            #print(recipient)
            recipient.execute_queries()
            #print('%%%%%DEBUG, Reply RESULT')
            if q.get_reply().get_result()==False:
                #print('you said no')
                i = self.communicator.tell(string='Aborting.',recipient=recipient)
                recipient.execute_queries()
                return
                #TODO: return old song?
                
            i_instructions = self.communicator.send_stock_query('instructions', recipient=recipient)

            recipient.execute_queries(i_instructions)
            self.send_song_messages(recipient=recipient)
                #print('you said yes')
                #TODO: test of the song
                
                
    def send_song_messages(self, recipient=None):

        modes_list = [InputMode.JIANPU, InputMode.SKY]
        q_mode = self.communicator.send_stock_query('musical_notation', recipient=recipient, limits=modes_list)
        
        possible_keys = ['do', 're']
        q_song_key = self.communicator.send_stock_query('possible_keys', recipient=recipient, foreword="\nYour song can be transposed in Sky with the following keys: " + ','.join(possible_keys),limits=possible_keys, prerequisites=q_mode)
        
        recipient.execute_queries()

        
        q_song_title = self.communicator.send_stock_query('song_title', recipient=recipient)
        q_original_artist = self.communicator.send_stock_query('original_artist', recipient=recipient)
        q_transcript_writer = self.communicator.send_stock_query('transcript_writer', recipient=recipient)
        
        recipient.execute_queries(q_song_title, q_original_artist, q_transcript_writer)
        
            #if q.get_result() == 
        #self.set_parser(SongParser(self))
        #os.chdir(self.directory_base)

        # communicator.output_instructions()

        # communicator.ask_first_line()
        # fp = self.load_file(self.get_song_dir_in(), first_line)  # loads file or asks for next line
        # song_lines = self.read_lines(first_line, fp)

        # Parse song
        # TODO: refactor song_lines, song_keys, parse_song to be in Song class
        # communicator.ask_input_mode(song_lines)
        # song_key = self.ask_song_key(self.get_parser().get_input_mode(), song_lines)
        # note_shift = communicator.ask_note_shift()
        # self.set_song(self.parse_song(song_lines, song_key, note_shift))

        # self.calculate_error_ratio()

        # Song information
        # communicator.ask_song_title()
        # communicator.ask_song_headers(song_key)

        # Output
        # communicator.send_song(RenderMode.PNG)
