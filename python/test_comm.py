import os
from modes import InputMode, ReplyType
from communication import QueryOpen, QueryChoice, Query
    
class test_responder():
	
    def __init__(self):
    	
        self.song_dir_in = 'test_songs'
        self.song_dir_out = 'songs_out'
        self.name = 'music-cog'
        
    def create_query_mode(self, modes_list):

        query_mode = QueryChoice(sender=self.name, recipient='bot', question="Mode (1-" + str(len(modes_list)) + "): ",
                                 foreword="Please choose your note format:\n", afterword=None, reply_type=ReplyType.INPUTMODE, limits=modes_list)

        return query_mode            
            
resp = test_responder()
q = resp.create_query_mode(modes_list=[InputMode.JIANPU])
q.send()


