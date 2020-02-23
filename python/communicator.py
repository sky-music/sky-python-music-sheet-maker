# import os
from modes import InputMode, ReplyType
# from communication import QueryOpen, QueryChoice, QueryBoolean, QueryMemory, Information
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


class Communicator:

    def __init__(self, owner_name=None):
        self.memory = communication.QueryMemory()
        self.owner_name = owner_name

        # A dictionary of standard queries arguments
        self.standard_queries = {'song_creation': {'class': communication.QueryOpen.__name__, 'sender': owner_name,
                                                   'recipient': 'music-sheet-maker',
                                                   'question': 'Please create a Visual Sheet'}}

    def get_name(self):
        return self.owner_name

    def __str__(self):

        return '<' + self.__class__.__name__ + ' of ' + repr(self.owner_name) + ' with ' + str(
            len(self.memory)) + ' stored queries>'

    def __getattr__(self, attr_name):
        """
        Default function to call in case no one else is found.
        """
        return getattr(self.memory, attr_name)  # If it's not for me, it's for my memory

    #        def default_handler_function(*args, **kwargs):
    #            thefunc = None
    #            try:
    #                thefunc = getattr(self.memory, attr_name) #If it's not for me, it's for my memory
    #                print('RETURNING 1')
    #            except AttributeError:
    #                try:
    #                    if isinstance(args[0], communication.Query):
    #                        print('RETURNING 2')
    #                        thefunc = self.receive
    #                except:
    #                   pass
    #            if thefunc is None:
    #                raise AttributeError(type(self).__name__ + ' object has no attribute ' + str(attr_name))
    #        print('RETURNING 4')
    #        return default_handler_function

    def formulate_standard(self, standard_query_name, recipient=None):

        try:
            standard_query_name = standard_query_name.lower().replace(' ', '_')
            method_name = self.standard_queries[standard_query_name]['class']
            method_args = self.standard_queries[standard_query_name].copy()
            method_args.pop('class')
            if recipient is not None:
                method_args['recipient'] = recipient
            query_method = getattr(communication, method_name)
            q = query_method(**method_args)
            return q
        except (KeyError, AttributeError):
            raise CommunicatorError(str(standard_query_name) + ' is not a standard query')

    def send(self, communication_objects, recipient=None):

        try:
            communication_objects[0]
        except (TypeError, IndexError):
            communication_objects = [communication_objects]

        for obj in communication_objects:
            if isinstance(obj, communication.Query):
                self.send_query(obj, recipient)

    def send_query(self, query, recipient):

        if not self.memory.has_query(query):
            print('I am ' + self.get_name() + ', storing a query before sending.')
            self.memory.store(query)

        query.check_sender(allowed=self.owner_name)
        query.send(recipient=recipient)

    def receive(self, queries):

        try:
            queries[0]
        except TypeError:
            queries = [queries]

        for query in queries:
            query.check_recipient(allowed=self.owner_name)
            # print('I am ' + self.get_name() + ', storing a query upon receipt.')
            self.memory.store(query)
            # TODO: check for duplicates

    def formulate_song_messages(self, recipient=None):

        i_instructions = communication.Information(sender=self.owner_name, recipient=recipient, question='Instructions')
        self.memory.store(i_instructions)

        # TODO: outline queries

        # query notes
        # query song notation / input mode

        # TODO: this is meant to be set after calculated by Song
        modes_list = [InputMode.JIANPU, InputMode.SKY]
        q_mode = communication.QueryChoice(sender=self.owner, recipient=recipient,
                                           question="Mode (1-" + str(len(modes_list)) + "): ",
                                           foreword="Please choose your note format:\n", afterword=None,
                                           reply_type=ReplyType.INPUTMODE,
                                           limits=modes_list)
        self.memory.store(q_mode)

        # query song key
        possible_keys = ['do', 're']
        q_song_key = communication.QueryChoice(sender=self.owner, recipient=recipient, question='What is the song key?',
                                               foreword=None, afterword=None, reply_type=ReplyType.TEXT,
                                               limits=possible_keys)
        self.memory.store(q_song_key)

        # query note shift

        # info error ratio

        # query song title
        q_song_title = communication.QueryOpen(sender=self.owner, recipient=recipient,
                                               question='What is the song title?',
                                               foreword='',
                                               afterword=None,
                                               reply_type=ReplyType.TEXT, limits=None)
        self.memory.store(q_song_title)

        # query original_artists
        q_original_artists = communication.QueryOpen(sender=self.owner, recipient=recipient,
                                                     question='Original artist(s): ',
                                                     foreword='Please fill song info or press ENTER to skip:',
                                                     afterword=None,
                                                     reply_type=ReplyType.TEXT, limits=None)
        self.memory.store(q_original_artists)
        # query transcript_writer
        q_transcript_writer = communication.QueryOpen(sender=self.owner, recipient=recipient,
                                                      question='Transcribed by: ',
                                                      foreword=None,
                                                      afterword=None, reply_type=ReplyType.TEXT, limits=None)
        self.memory.store(q_transcript_writer)

    def send_unsent_queries(self, recipient=None):

        for q in self.memory.recall_unsent():
            q.send(recipient)

    def print_memory(self):

        print(self)
        for q in self.memory.recall():
            print(q)

    def get_memory(self):
        return self.memory
