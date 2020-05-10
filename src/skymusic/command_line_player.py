#!/usr/bin/env python3
if __name__ == '__main__':    
    import os, sys
    project_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../'))
    if project_path not in sys.path:
        sys.path.append(project_path)


from src.skymusic.music_sheet_maker import MusicSheetMaker
from src.skymusic.communicator import Communicator, QueriesExecutionAbort
from src.skymusic import Lang

try:
    import readline
except ModuleNotFoundError:
    pass  # probably Windows


class CommandLinePlayer:

    """
    A puppet to work with the Music Sheet Maker.
    CAUTION: All puppets must have the following methods:
        - get_name(), returning a name among the authorized locutors list of communication.py
        - get_locale(), returning a language code string 'xx.YY'
        - execute_queries()
        - a Communicator to handle Queries
    It is recommended to have a receive() method or to a __getattr__ method to
    to call methods from communicator directly from the puppet.
    """

    def __init__(self, locale='en_US'):
        self.name = 'command-line'
        self.locale = self.set_locale(locale)
        self.communicator = Communicator(owner=self, locale=locale)
        
    def __getattr__(self, attr_name):
        """
        Default function to call in case no one else is found.
        """
        if 'communicator' in self.__dict__.keys():
            return getattr(self.communicator, attr_name)
        else:
            raise AttributeError(f"type object '{type(self).__name__}' has no attribute 'communicator'")

    def get_name(self):
        return self.name
        
    def get_locale(self):        
        return self.locale

    def set_locale(self, locale):
        
        self.locale = Lang.check_locale(locale)
        if self.locale is None:
            self.locale = Lang.find_substitute(locale)
            print(f"**WARNING: bad locale type passed to CommandLinePlayer: {locale}. Reverting to {self.locale}")
            
        return self.locale

    
    def receive(self, *args, **kwargs):
        self.communicator.receive(*args, **kwargs)


    def execute_queries(self, queries=None):

        if queries is None:
            self.communicator.memory.clean()
            queries = self.communicator.recall_unsatisfied(filters=('to_me'))
        else:
            if not isinstance(queries, (list, set)):
                queries = [queries]
        """
        The following part is exclusive to the command line.
        """
        for q in queries:
            reply_valid = False
            while not reply_valid:
                question = self.communicator.query_to_stdout(q)
                reply_valid = True #to be sure to break the loop
                if q.get_expect_reply(): 
                    answer = input('\n%s: '%question)   
                    q.reply_to(answer)
                    reply_valid = q.get_reply_validity()
                else:                  
                    print(question)
                    q.reply_to('ok')
                    reply_valid = q.get_reply_validity()

try:

    player = CommandLinePlayer(locale=Lang.guess_locale())

    maker = MusicSheetMaker(locale=Lang.guess_locale())

    q = player.communicator.send_stock_query('create_song', recipient=maker)

    maker.execute_queries(q)

except QueriesExecutionAbort as qExecAbort:
    print(repr(qExecAbort))
    
