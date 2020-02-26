# import os
from modes import InputMode, ReplyType
from communication import Query, QueryOpen, QueryChoice, QueryBoolean, QueryMemory, Information
import communication
import copy

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


class Communicator():

    def __init__(self, owner):
        self.owner = owner
        self.memory = QueryMemory(self.owner)
        self.name = self.owner.get_name()

        # A dictionary of standard queries arguments
        self.query_stock = {
            'create_song': {'class': QueryOpen.__name__, 'handler': 'create_song',
            'question': 'create_song'},
            
            'song_overwrite': {'class': QueryBoolean.__name__, 'handler': 'None',
            'foreword': 'A Song already exists in memory.',
            'question': 'Do you want to overwrite it?', 'reply_type': ReplyType.TEXT},
            
            'instructions': {'class': Information.__name__, 'handler': 'None',
            'foreword':'===== VISUAL MUSIC SHEETS FOR SKY:CHILDREN OF THE LIGHT =====',
            'question': ''},
            
            'song_title': {'class': QueryOpen.__name__, 'handler': 'None',
            'question': 'What is the song title?', 'reply_type': ReplyType.TEXT},
            
            'original_artist': {'class': QueryOpen.__name__, 'handler': 'None',
            'question': 'What is the Original artist(s)?', 'reply_type': ReplyType.TEXT},
            
            'transcript_writer': {'class': QueryOpen.__name__, 'handler': 'None',
            'question': 'What is the transcript writer?', 'reply_type': ReplyType.TEXT},
            
            'musical_notation': {'class': QueryChoice.__name__, 'handler': 'None',
            'question': 'Please choose your note format', 'reply_type': ReplyType.INPUTMODE, 'limits': []},
            
            'possible_keys': {'class': QueryChoice.__name__, 'handler': 'None',
            'question': 'Please choose your note format', 'reply_type': ReplyType.NOTES, 'limits': []}
            
            }
        
                                                   

    def __str__(self):

        return '<' + self.__class__.__name__ + ' of ' + repr(self.owner.get_name()) + ' with ' + str(
            len(self.memory)) + ' stored queries>'

    def __getattr__(self, attr_name):
        """
        Default function to call in case no one else is found.
        """
        if 'memory' in self.__dict__.keys():
            return getattr(self.memory, attr_name)
        else:
            raise AttributeError("type object " + repr(type(self).__name__) + " has no attribute 'memory")
            
    def get_name(self):
        return self.name
    #        def default_handler_function(*args, **kwargs):
    #            thefunc = None
    #            try:
    #                thefunc = getattr(self.memory, attr_name) #If it's not for me, it's for my memory
    #                print('RETURNING 1')
    #            except AttributeError:
    #                try:
    #                    if isinstance(args[0], Query):
    #                        print('RETURNING 2')
    #                        thefunc = self.receive
    #                except:
    #                   pass
    #            if thefunc is None:
    #                raise AttributeError(type(self).__name__ + ' object has no attribute ' + str(attr_name))
    #        print('RETURNING 4')
    #        return default_handler_function

    def send_stock_query(self, stock_query_name, recipient, **kwargs):
    '''
    Create and send a query from a catalog, overriding some parameters with kwargs 
    '''
        try:
            stock_query_name = known_query_name.lower().replace(' ', '_')
            stock_query = self.stock_queries[stock_query_name]
        except KeyError:
            raise CommunicatorError(str(stock_query_name) + ' is not a standard query')
                
        method_name = stock_query['class']
        method_args = stock_query.copy()
        method_args.pop('class')
        method_args.pop('handler')
        method_args['sender'] = self.owner
        method_args['recipient'] = recipient
        
        method_args.update(kwargs)
        	
        query_method = getattr(communication, method_name)
        
        q = query_method(**method_args)
        self.memory.store(q)
        q.check_sender(allowed=self.owner)
        q.send(recipient=recipient)
        
        return q
            
    '''
    def send(self, communication_objects, recipient=None):

        try:
            communication_objects[0]
        except (TypeError, IndexError):
            communication_objects = [communication_objects]

        for obj in communication_objects:
            if isinstance(obj, Query):
                self.send_query(obj, recipient)

    def send_query(self, query, recipient):

        if not self.memory.has_query(query):
            print('I am ' + self.owner.get_name() + ', storing a query before sending.')
            self.memory.store(query)

        query.check_sender(allowed=self.owner)#TODO: previously self.get_name()
        query.send(recipient=recipient)
    '''

    def receive(self, queries):

        if not isinstance(queries,(list,tuple)):
            queries = [queries]

        for q in queries:
            if q.check_recipient(allowed=self.owner):
                # print('I am ' + self.get_name() + ', storing a query upon receipt.')
                self.memory.store(q)
                # TODO: check for duplicates

    def query_to_discord(self, obj):
        
        question = obj.get_result()
        return question

    def discord_to_query(self, obj):
        
        return

    def tell(self, recipient, string):
        
        i = Information(sender=self, recipient=recipient, question=string)
        self.memory.store(i)
        i.send(recipient=recipient)
        return i

    def translate(self, obj):
    
        if isinstance(obj, (Query, Reply)):	
            self.query_to_discord(obj)
        else:
            self.discord_to_query(obj)
        return

            
       
    '''
    def query_song_overwrite(self, recipient):
        
        q = QueryBoolean(sender=self, recipient=recipient, foreword='A Song already exist in memory.', question='Do you want to overwrite it?', reply_type=ReplyType.TEXT)
        self.memory.store(q)
        q.send(recipient=recipient)
        return q
     '''
    '''
    def send_unsent_queries(self, recipient=None):

        for q in self.memory.recall_unsent():
            q.send(recipient)
    '''
