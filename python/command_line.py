#!/usr/bin/env python3
from music_sheet_maker import MusicSheetMaker
from communicator import Communicator


# from modes import ResponseMode
# song_responder = Responder()
# song_responder.set_response_mode(ResponseMode.COMMAND_LINE)
# song_responder.create_song_command_line()


class CommandLinePlayer:

    def __init__(self):
        self.song = None  # Song object
        self.name = 'music-cog'
        self.communicator = Communicator(owner_name=self.name)
        # self.parser = SongParser()
        # self.receive =  self.communicator.receive

    def __getattr__(self, attr_name):
        """
        Default function to call in case no one else is found.
        """
        return getattr(self.communicator, attr_name)

    def get_name(self):
        return self.name

    def receive(self, *args, **kwargs):
        self.communicator.receive(*args, **kwargs)
        
    def prompt_queries(self, queries):
    
        try:
            len(queries)
        except AttributeError:
            queries = [queries]
    		
        for q in queries:
    		
            question = self.communicator.query_to_discord()
            answer = input(question)		
            q.reply_to(answer)
        


player = CommandLinePlayer()

maker = MusicSheetMaker()

q = player.communicator.formulate_known('create_song', recipient=maker)
player.communicator.send(q, recipient=maker)

maker.execute_queries()

#player.communicator.process_queries()



#player.communicator.memory.store(q)

print('\n\n')
player.communicator.print_memory()
print('\n')
maker.communicator.print_memory()



# MusicSheetMaker().create_song(recipient=player)

# MusicSheetMaker().get_communicator().send_unsent_queries(recipient=me)

# maker.ask
