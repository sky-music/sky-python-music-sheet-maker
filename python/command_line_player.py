#!/usr/bin/env python3
from music_sheet_maker import MusicSheetMaker
from communicator import Communicator, QueriesExecutionAbort
import Lang

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
            raise AttributeError("type object " + repr(type(self).__name__) + " has no attribute 'communicator")

    def get_name(self):
        return self.name
        
    def get_locale(self):        
        return self.locale

    def set_locale(self, locale):
        
        self.locale = Lang.check_locale(locale)
        if self.locale is None:
            self.locale = Lang.find_substitute(locale)
            print("**WARNING: bad locale type %s passed to CommandLinePlayer. Reverting to %s"%(locale, self.locale))
            
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
        #FIXME: 2 lines for debugging:
        #print('\n%%%%DEBUG. I AM PLAYER, THE UNSATISFIED QUERIES ARE:%%%%')
        #self.communicator.memory.print_out(filters=('unsatisfied'))x
        """
        The following part is exclusive to the command line.
        The executing code must be rewritten for discord, typically using:
            question = self.communicator.query_to_discord(q)
            await Questions.ask_text(self.bot, channel, ctx.author, question...)
        """
        for q in queries:
            reply_valid = False
            while not reply_valid:
                question = self.communicator.query_to_stdout(q)
                reply_valid = True #to be sure to break the loop
                if q.get_expect_reply():                  
                    #print('%%%DEBUG. PLAYER, YOU ARE BEING PROMPTED%%%') #FIXME: for debugging only                    
                    answer = input('%s: '%question)   
                    q.reply_to(answer)
                    reply_valid = q.get_reply_validity()
                else:                  
                    #print('%%%DEBUG. PLAYER, YOU ARE BEING TOLD%%%') #FIXME: for debugging only
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
    
    
'''
# for debugging only
print('\n%%%DEBUG. MAIN script has ended%%%')
print('\n\n%%%DEBUG. Player memory:')
player.communicator.memory.print_out()
print('\n%%%DEBUG. Maker memory:')
maker.communicator.memory.print_out()
'''
