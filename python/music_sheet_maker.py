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
            queries = self.communicator.memory.recall_unsatisfied()
            queries = self.communicator.recall_unsatisfied(filters=('to_me'))
        else:
            if not isinstance(queries,(list,tuple)):
                queries = [queries]
        print('%%%%I AM MAKER AND HERE ARE MY UNSATISFIED QUERIES:%%%%')
        self.communicator.memory.print_out(filters=('to_me'))
        for q in queries:
            try:
                query_name = q.get_result()
                #print('This one is unreplied to :+query_name')
                known_query = self.communicator.known_queries[query_name]
                #print('self.'+known_query['handler']+'(sender='+q.get_sender().get_name()+')')
                result = eval('self.'+known_query['handler']+'(sender=q.get_sender())')
                q.reply_to(result)
            except KeyError:
                print('unknown query!!!')
                pass

    def create_song(self, **kwargs):
        
        try:
            recipient = kwargs['sender']
        except KeyError:
            raise MusicMakerError('No recipient specified for the Song')
            
        if self.song is not None:
            q = self.communicator.query_song_overwrite(recipient=recipient)
            #print('%%%%%DEBUG')
            #print(recipient)
            recipient.execute_queries()
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
