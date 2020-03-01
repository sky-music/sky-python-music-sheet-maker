#!/usr/bin/env python3
from music_sheet_maker import MusicSheetMaker
from communicator import Communicator


class CommandLinePlayer:

    def __init__(self):
        self.song = None  # Song object
        self.name = 'command-line'
        self.communicator = Communicator(owner=self)
        # self.parser = SongParser()
        # self.receive =  self.communicator.receive

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

    def receive(self, *args, **kwargs):
        self.communicator.receive(*args, **kwargs)
        
        
    def execute_queries(self, queries=None):
        
        if queries == None:
            self.communicator.memory.clean()
            queries = self.communicator.recall_unsatisfied(filters=('to_me'))
        else:
            if not isinstance(queries,(list,tuple)):
                queries = [queries]
        print('\n%%%%I AM PLAYER, MY UNSATISFIED QUERIES ARE:%%%%')
        self.communicator.memory.print_out(filters=('to_me'))
        
        for q in queries:
            question = self.communicator.query_to_discord(q)
            reply_valid = False
            while not reply_valid:
                if q.get_expect_reply():
                    print('%%%PLAYER, YOU ARE BEING PROMPTED%%%')
                    answer = input(question + ': ')		
                    q.reply_to(answer)
                    reply_valid = q.get_reply_validity()
                else:
                    print('%%%PLAYER, YOU ARE BEING TOLD%%%')
                    print(question)
                    q.reply_to('ok')
                    reply_valid = q.get_reply_validity()
        return True

if __name__ == "__main__":

    player = CommandLinePlayer()
    maker = MusicSheetMaker()
    
    q = player.communicator.send_stock_query('create_song', recipient=maker)
    #player.communicator.send(q, recipient=maker)
    
    maker.execute_queries()
    
    #player.execute_queries()
    
    
    print('\n%%%MAIN script has ended%%%')
    print('\n\n%%%Player memory:')
    player.communicator.memory.print_out()
    print('\n%%%Maker memory:')
    maker.communicator.memory.print_out()
    

