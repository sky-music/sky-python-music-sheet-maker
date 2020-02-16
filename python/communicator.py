import os
from modes import InputMode, ReplyType
from communication import QueryOpen, QueryChoice, QueryBoolean, QueryMemory

"""
Classes to ask and answer questions called Query and Reply between the bot and the music cog.
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
        self.query_memory = QueryMemory()
        self.create_queries()

    def create_queries(self):

        q_song_title = QueryOpen(sender='music-cog', recipient='bot', question='What is the song title? (also used '
                                                                               'for the file name)', foreword='',
                                 afterword=None,
                                 reply_type=ReplyType.TEXT, limits=None)
        self.query_memory.store(q_song_title)

        modes_list = [InputMode.JIANPU, InputMode.SKY]
        q_mode = QueryChoice(sender='music-cog', recipient='bot', question="Mode (1-" + str(len(modes_list)) + "): ",
                             foreword="Please choose your note format:\n", afterword=None,
                             reply_type=ReplyType.INPUTMODE,
                             limits=modes_list)
        self.query_memory.store(q_mode)

    def recall_queries(self):

        print('\nAll queries:\n')
        for q in self.query_memory.recall():
            print(q)

        print('\n\nStored TEXT queries:\n')
        qs = self.query_memory.recall(ReplyType.TEXT)
        [print(q) for q in qs]

        print('\n\nBrain inventory:\n')
        print(self.query_memory)

    def get_query_memory(self):
        return self.query_memory
