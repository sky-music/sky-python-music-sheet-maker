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

        # self.communicator.print_memory()


player = CommandLinePlayer()

maker = MusicSheetMaker()

q = player.communicator.formulate_standard('song_creation', recipient=maker)

player.communicator.memory.store(q)
print(player.communicator.memory)
print(maker.communicator.memory)
player.communicator.send(q, recipient=maker)

print('\n\n')
player.communicator.print_memory()
print('\n')
maker.communicator.print_memory()

# MusicSheetMaker().create_song(recipient=player)


# MusicSheetMaker().get_communicator().send_unsent_queries(recipient=me)

# maker.ask
