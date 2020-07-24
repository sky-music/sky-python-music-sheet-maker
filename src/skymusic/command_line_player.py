#!/usr/bin/env python3
if __name__ == '__main__':    
    import os, sys
    # VERY IMPORTANT: the root project path directory must be defined and added to path
    # The '../../' has to be changed if the current file location is changed
    PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../'))
    if PROJECT_ROOT not in sys.path:
        sys.path.append(PROJECT_ROOT)

import yaml
from src.skymusic.music_sheet_maker import MusicSheetMaker
from src.skymusic.communicator import Communicator, QueriesExecutionAbort
from src.skymusic import Lang
from src.skymusic.resources import Resources
try:
    import readline
except ModuleNotFoundError:
    pass  # probably Windows

#============================
#SETTINGS FOR ADVANCED USERS
SKYJSON_URL = False # To generate a temporary song link at sky-music.herokuapp.com. By default will be enabled on the Discord Music Cog but disabled on the command line (to avoid spamming this server)
SONG_DIR_IN = os.path.normpath(PROJECT_ROOT + '/test_songs') # Overrides defaut input song folder
SONG_DIR_OUT = os.path.normpath(PROJECT_ROOT + '/songs_out') # Overrides defaut output song folder
BATCH_MODE = False # To process songs in a batch,stored as .yaml files
BATCH_DIR = os.path.normpath(PROJECT_ROOT + '/batch_songs')
PREFERENCES_PATH = os.path.normpath(PROJECT_ROOT + '/preferences.yaml')
#============================

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

    def __init__(self, locale='en_US', preferences_path='../../preferences.yaml'):
        self.name = Resources.COMMAND_LINE_NAME
        self.locale = self.set_locale(locale)
        self.communicator = Communicator(owner=self, locale=locale)
        self.preferences = self.load_preferences(preferences_path)
        self.yaml_song = None
        
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

    def fetch_yaml_songs(self, songs_dir):
        
        dirpath, _, filenames = next(os.walk(songs_dir), (None, None, []))
        
        for filename in filenames:
            if os.path.splitext(filename)[1].lower().strip() != '.yaml':
                filenames.remove(filename)
        
        self.yaml_songs = [os.path.normpath(os.path.join(dirpath, filename)) for filename in filenames]
        
        return self.yaml_songs

    def load_preferences(self, filepath):
        try:
            with open(filepath, mode='r', encoding='utf-8', errors='ignore') as file:
                print(f"(Loaded preferences file from {filepath})")
                return yaml.safe_load(file)
        except (FileNotFoundError, PermissionError):
            return None               

    def get_answer_from_preferences(self, q):
        
        try:
            answer = self.preferences[q.get_name()]
            if answer is not None:
                answer = str(answer).strip()
            else:
                answer = ''
        except (TypeError, KeyError):
            answer = None

        return answer


    def get_answer_from_yaml_song(self, q):
        
        try:
            answer = self.yaml_song[q.get_name()]
            if answer is not None:
                answer = str(answer).strip()
            else:
                answer = ''
        except (TypeError, KeyError):
            answer = None

        return answer


    def load_yaml_song(self, filepath):
        
        try:
            with open(filepath, mode='r', encoding='utf-8', errors='ignore') as file:
                self.yaml_song = yaml.safe_load(file)
                return self.yaml_song
        except (FileNotFoundError, PermissionError):
            return None
        

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
            tried_preferences = False
            tried_yaml = False
            while not reply_valid:
                question = self.communicator.query_to_stdout(q)
                reply_valid = True #to be sure to break the loop
                if q.get_expect_reply():
                    answer = None                  
                    if self.yaml_song and not tried_yaml: # First tries to process yaml song
                        tried_yaml = True
                        answer = self.get_answer_from_yaml_song(q)                        
                        if answer is not None:
                            print(f"\n{question}: {answer}") 
                            q.reply_to(answer)
                            
                    if answer is None and not tried_preferences: # If answer is still none, tries to get default answer
                        tried_preferences = True
                        answer = self.get_answer_from_preferences(q)                        
                        if answer is not None:
                            print(f"\n{question}: {answer}") 
                            q.reply_to(answer)
                            
                    if answer is None: # Else asks the user a question in the prompt
                        answer = input('%s: '%question)
                        q.reply_to(answer)
                    reply_valid = q.get_reply_validity()
                else:                  
                    print('\n'+question)
                    q.reply_to('ok')
                    reply_valid = q.get_reply_validity()

try:
    
    player = CommandLinePlayer(locale=Lang.guess_locale(), preferences_path=PREFERENCES_PATH)
    maker = MusicSheetMaker(locale=Lang.guess_locale(), song_dir_in=SONG_DIR_IN, song_dir_out=SONG_DIR_OUT, enable_skyjson_url=SKYJSON_URL)

    if BATCH_MODE:
        
        file_paths = player.fetch_yaml_songs(BATCH_DIR)
        for file_path in file_paths:
            player.load_yaml_song(file_path)
            q = player.communicator.send_stock_query('create_song', recipient=maker)
            maker.execute_queries(q)
            maker.communicator.flush()
            player.communicator.flush()
    else:
        q = player.communicator.send_stock_query('create_song', recipient=maker)
        maker.execute_queries(q)

except QueriesExecutionAbort as qExecAbort:
    print(repr(qExecAbort))
    
