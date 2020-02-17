import os
from modes import InputMode, ReplyType
from communication import QueryOpen, QueryChoice, QueryBoolean, QueryMemory, Information

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


# song_dir_in = 'test_songs'
# song_dir_out = 'songs_out'

class Communicator:

    def __init__(self):
        self.brain = QueryMemory()
        self.create_messages()

    def create_messages(self):

        i_instructions = Information('Instructions')

        # TODO:

        # query notes
        # query song notation / input mode

        # TODO: this is meant to be set after calculated by Song
        modes_list = [InputMode.JIANPU, InputMode.SKY]

        q_mode = QueryChoice(sender='music-sheet-maker', recipient='bot', question="Mode (1-" + str(len(modes_list)) + "): ",
                             foreword="Please choose your note format:\n", afterword=None,
                             reply_type=ReplyType.INPUTMODE,
                             limits=modes_list)
        self.brain.store(q_mode)

        # query song key
        possible_keys = []
        q_song_key = QueryChoice(sender='music-sheet-maker', recipient='bot', question='What is the song key?',
                                 foreword=None, afterword=None, reply_type=ReplyType.TEXT, limits=possible_keys)
        self.brain.store(q_song_key)

        # query note shift

        # info error ratio

        # query song title
        q_song_title = QueryOpen(sender='music-sheet-maker', recipient='bot', question='What is the song title?',
                                 foreword='',
                                 afterword=None,
                                 reply_type=ReplyType.TEXT, limits=None)
        self.brain.store(q_song_title)

        # query original_artists
        q_original_artists = QueryOpen(sender='music-sheet-maker', recipient='bot', question='Original artist(s): ',
                                       foreword='Please fill song info or press ENTER to skip:', afterword=None,
                                       reply_type=ReplyType.TEXT, limits=None)
        self.brain.store(q_original_artists)
        # query transcript_writer
        q_transcript_writer = QueryOpen(sender='music-sheet-maker', recipient='bot', question='Transcribed by: ',
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
