import os
from modes import InputMode
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

    def __init__(self):
        self.name = 'music-sheet-maker'
        self.communicator = Communicator(owner=self)
        self.song = 0  # TODO reset song to None after debugging tests
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
        
    def get_song(self):
        return self.song

    def set_song(self, song):
        self.song = song

    def get_parser(self):
        return self.parser

    def set_parser(self, parser):
        self.parser = parser  

    def init_working_directory(self):
        os.chdir('../')
        #if not os.path.isdir(self.song_dir_out):
            #os.mkdir(self.song_dir_out)

    def get_directory_base(self):
        return self.directory_base
        
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
        
        reply_valid = False
        while not reply_valid:
            for q in queries:
                try:
                    query_name = q.get_result()
                    
                    stock_query = self.communicator.query_stock[query_name]
                
                    result = eval('self.'+stock_query['handler']+'(sender=q.get_sender())')
                    q.reply_to(result)
                    reply_valid = q.get_reply_validity()
                    
                except KeyError:
                    raise MusicMakerError('Unknown query '+repr(query_name))
                    pass

    def create_song(self, **kwargs):
        '''
        A very linear, sesuential way of building a song from user inputs
        TODO: implement nonlinear parsing using prerequisites
        
        '''
        try:
            recipient = kwargs['sender']
        except KeyError:
            raise MusicMakerError('No recipient specified for the Song')
            
        if self.song is not None:
            #q  = self.communicator.query_song_overwrite(recipient=recipient)
            q_overwrite = self.communicator.send_stock_query('song_overwrite', recipient=recipient)
            #print('%%%%%DEBUG')
            #print(recipient)
            recipient.execute_queries()
            #print('%%%%%DEBUG, Reply RESULT')
            if q_overwrite.get_reply().get_result() == False:
                i = self.communicator.tell(string='Aborting.',recipient=recipient)
                recipient.execute_queries()
                return
                #TODO: return old song?
                #TODO reply None to song_creation query so that it gets satisfied and the loop ends
                #return something, a Reply or  do Query.reply_to if it has been passed as argument
        
        self.set_parser(SongParser(self))
        os.chdir(self.get_directory_base())
        
        #Display instructions
        i_instructions = self.communicator.send_stock_query('instructions', recipient=recipient)
        recipient.execute_queries(i_instructions)
        
        #Ask for notes
        notes = self.ask_notes(recipient=recipient)
        
        input_mode = self.ask_input_mode(recipient=recipient, notes=notes)
        
        self.get_parser().set_input_mode(input_mode)
        
        print('%%%%DEBUG')
        print(input_mode)
        #TODO: Song rendering
        #self.set_parser(SongParser(self))
        #os.chdir(self.directory_base)   
       
        # Parse song
        #TODO: parse notes
        # self.parse_song(song_lines, song_key, note_shift))
        
        song_key = self.ask_song_key(recipient=recipient, notes=notes, input_mode=input_mode)
        
        #Asks for octave shift
        q_shift = self.communicator.send_stock_query('octave_shift', recipient=recipient)
        recipient.execute_queries(q_shift)
        octave_shift = q_shift.get_reply().get_result()
        
        
        #Asks for song metadata
        title, artist, writer = self.ask_song_metadata(recipient=recipient)
        
        
        #Render Song
        #TODO: render songnobjects
        #self.set_song(

        #err=self.calculate_error_ratio()
        #i_errors = self.communicator.send_stock_query('information', recipient=recipient, question=str(err))

        # TODO: Send Output
        #several options to answer the  query:
        #1/ have the query passed as the first argument of the current method and use Query.reply_to
        #2/ return the song as a reply object, and let the encapsulating method use query.reply_to
        #3/ Find the query in the memory and reply to it
        
        # self.send_song(query,recipient)     
    
    
    def ask_song_metadata(self, recipient):
    
        #TODO: Remember metadata so that, if parsing fails the questions are not asked again
        
        queries = []
        
        queries += [self.communicator.send_stock_query('song_title', recipient=recipient)]
        queries += [self.communicator.send_stock_query('original_artist', recipient=recipient)]
        queries += [self.communicator.send_stock_query('transcript_writer', recipient=recipient)]
        
        recipient.execute_queries(queries)
        
        result = [q.get_reply().get_result()  for q in queries]
        
        return tuple(result)
        
    def ask_notes(self, recipient):
        
    #TODO: ask for notes
    # communicator.ask_first_line()
    # fp = self.load_file(self.get_song_dir_in(), first_line)  # loads file or asks for next line
    # song_lines self.read_lines(first_line, fp)
        q_notes = self.communicator.send_stock_query('song_notes', recipient=recipient)
        recipient.execute_queries(q_notes)
        
        return q_notes.get_reply().get_result()
        
    def ask_input_mode(self, recipient, notes):

        possible_modes = self.get_parser().get_possible_modes(notes)
        
        #Ask for musical notation
        q_mode = self.communicator.send_stock_query('musical_notation', recipient=recipient, limits=possible_modes)
        recipient.execute_queries(q_mode)
        
        result = q_mode.get_reply().get_result()
        
        return result
        
        
    def ask_song_key(self, recipient, notes, input_mode):
        #asks for song key
        """
        Attempts to detect key for input written in absolute musical scales (western, Jianpu)
        """
        #TODO:
        if input_mode in [InputMode.ENGLISH, InputMode.DOREMI, InputMode.JIANPU]:
            possible_keys = self.get_parser().find_key(notes)
            if len(possible_keys) == 0:
                self.communicator.tell(string="\nYour song cannot be transposed exactly in Sky.",recipient=recipient)
                # trans = input('Enter a key or a number to transpose your song within the chromatic scale:')
                self.communicator.tell(string="\nDefault key will be set to C.",recipient=recipient)
                
                song_key = 'C'
                
            elif len(possible_keys) == 1:
                song_key = str(possible_keys[0])
                self.communicator.tell(string="\nYour song can be transposed in Sky with the following key: " + song_key,recipient=recipient)
            else:
                
                q_key = self.communicator.send_stock_query('possible_keys', recipient=recipient, foreword="\nYour song can be transposed in Sky with the following keys: " + ','.join(possible_keys),limits=possible_keys)
                recipient.execute_queries(q_key)
                
                song_key = q_key.get_reply().get_answer()
                
        else:
            q_key = self.communicator.send_stock_query('recommended_key', recipient=recipient)
            
            recipient.execute_queries(q_key)
                
            song_key = q_key.get_reply().get_result()
                
        return song_key
