#import os
from modes import InputMode, ReplyType
#from communication import QueryOpen, QueryChoice, QueryBoolean, QueryMemory, Information
import communication

"""
Classes to ask and answer questions called Query and Reply between the bot and the music sheet maker
TODO: list of mandatory questions to implement
a) asked by the cog:
- notes, OPEN
- musical notation (if several are found), CHOICE
- music key (if several are found), CHOICE
- song title, OPEN
- song headers, OPEN
- note shift, OPEN with type and range restrictions

b) asked by the bot:
- what are the PNGs?, OPEN with type restriction
- how many PNGs?, OPEN with type and range restrictions

c) asked by the command line:
- what are the files and where are they saved, OPEN

"""

class CommunicatorError(Exception):
    def __init__(self, explanation):
        self.explanation = explanation

    def __str__(self):
        return str(self.explanation)

    pass




class Communicator:

    def __init__(self, owner=None):
        self.brain = communication.QueryMemory()
        self.listening = True
        self.owner = owner

        #A dictionary of standard queries arguments
        self.standard_queries = {}
        self.standard_queries['song_creation'] = {'class': communication.QueryOpen.__name__, 'sender': 'bot', 'recipient': 'music-sheet-maker', 'question': 'Please create a Visual Sheet'}

    def __getattr__(self, name):
        '''
        Default function to call in case no one else is found. 
        '''
        def default_handler_function(*args, **kwargs):
            try:
                thefunc = getattr(self.brain, name) #If it's not for me, it's for my brain
                return thefunc
            except AttributeError:
                try:
                    if isinstance(args[0], communication.Query):
                        self.receive(*args, **kwargs)
                except:
                   return AttributeError

        return default_handler_function

    def formulate(self, standard_query_name):
        
        try:
            standard_query_name = standard_query_name.lower().replace(' ','_')
            method_name = self.standard_queries[standard_query_name]['class']
            method_args = self.standard_queries[standard_query_name].copy()
            method_args.pop('class')
            query_method = getattr(communication, method_name)
            q = query_method(**method_args)
            return q
        except (KeyError, AttributeError):
            raise CommunicatorError(str(standard_query_name) + ' is not a standard query')
    
    
    def receive(self, query):
        
        query.check_recipient(forbidden=self.owner)
        self.brain.store(query)
        

    def create_song_messages(self, recipient=None):

        i_instructions = communication.Information('Instructions')

        # TODO: outline queries

        # query notes
        # query song notation / input mode

        # TODO: this is meant to be set after calculated by Song
        modes_list = [InputMode.JIANPU, InputMode.SKY]
        q_mode = communication.QueryChoice(sender=self.owner, recipient=recipient, question="Mode (1-" + str(len(modes_list)) + "): ",
                             foreword="Please choose your note format:\n", afterword=None,
                             reply_type=ReplyType.INPUTMODE,
                             limits=modes_list)
        self.brain.store(q_mode)

        # query song key
        possible_keys = []
        q_song_key = communication.QueryChoice(sender=self.owner, recipient=recipient, question='What is the song key?',
                                 foreword=None, afterword=None, reply_type=ReplyType.TEXT, limits=possible_keys)
        self.brain.store(q_song_key)

        # query note shift

        # info error ratio

        # query song title
        q_song_title = communication.QueryOpen(sender=self.owner, recipient=recipient, question='What is the song title?',
                                 foreword='',
                                 afterword=None,
                                 reply_type=ReplyType.TEXT, limits=None)
        self.brain.store(q_song_title)

        # query original_artists
        q_original_artists = communication.QueryOpen(sender=self.owner, recipient=recipient, question='Original artist(s): ',
                                       foreword='Please fill song info or press ENTER to skip:', afterword=None,
                                       reply_type=ReplyType.TEXT, limits=None)
        self.brain.store(q_original_artists)
        # query transcript_writer
        q_transcript_writer = communication.QueryOpen(sender=self.owner, recipient=recipient, question='Transcribed by: ',
                                        foreword=None,
                                        afterword=None, reply_type=ReplyType.TEXT, limits=None)
        self.brain.store(q_transcript_writer)

    def recall_queries(self):

        print('\nAll queries:\n')
        for q in self.brain.recall():
            print(q)

        print('\n\nStored TEXT queries:\n')
        qs = self.brain.recall(ReplyType.TEXT)
        [print(q) for q in qs]

        print('\n\nBrain inventory:\n')
        print(self.brain)

    def get_query_memory(self):
        return self.brain
