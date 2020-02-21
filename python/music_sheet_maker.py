from communicator import Communicator, CommunicatorError
#from parsers import SongParser


class MusicSheetMaker:

    def __init__(self):
        self.song = None #Song object
        self.name = 'music-sheet-maker'
        self.communicator = Communicator(owner=self.name)
        #self.parser = SongParser()
        #self.receive =  self.communicator.receive
    
    def __getattr__(self, name):
        '''
        Default function to call in case no one else is found. 
        '''
        return getattr(self.communicator, name)
    
    def create_song(self, client_listening=True, recipient=None):
        
        if not self.listening:
            raise CommunicatorError(self.name+' is not listening')
               
        self.communicator.create_song_messages(recipient=recipient)

        #self.set_parser(SongParser(self))

        #os.chdir(self.get_directory_base())

        #communicator.output_instructions()

        #communicator.ask_first_line()
        #fp = self.load_file(self.get_song_dir_in(), first_line)  # loads file or asks for next line
        #song_lines = self.read_lines(first_line, fp)

        # Parse song
        # TODO: refactor song_lines, song_keys, parse_song to be in Song class
        #communicator.ask_input_mode(song_lines)
        #song_key = self.ask_song_key(self.get_parser().get_input_mode(), song_lines)
        #note_shift = communicator.ask_note_shift()
        #self.set_song(self.parse_song(song_lines, song_key, note_shift))

        #self.calculate_error_ratio()

        # Song information
        #communicator.ask_song_title()
        #communicator.ask_song_headers(song_key)

        # Output
        #communicator.send_song(RenderMode.PNG)
        

