#!/usr/bin/env python3
import os, sys

#Gets the directory from which the script is executed, either as a python script or as a bundle (PyInstalled dist) or an executable (PyInstaller one-file)
try:
    this_file = os.path.abspath(__file__)
except NameError:
    this_file = os.path.abspath(sys.argv[0])
if getattr(sys, 'frozen', False):
    application_root = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
else:
    application_root = os.path.dirname(this_file)

if __name__ == '__main__' and not getattr(sys, 'frozen', False): #Local Script
    # VERY IMPORTANT: the skymusic package root directory must be added to the system PATH
    # The '../' has to be changed if the directory structure is changed, in particular if the current __file__ location is changed
    PACKAGE_ROOT = os.path.normpath(os.path.join(application_root, '../'))
    USER_FILES_ROOT = os.path.normpath(os.path.join(application_root, '../../'))
    if PACKAGE_ROOT not in sys.path:
        sys.path.append(PACKAGE_ROOT)
else: #Executable, or pip installed
    USER_FILES_ROOT = os.path.join(os.path.expanduser("~"), 'skymusic')
    if not os.path.isdir(USER_FILES_ROOT):
        os.makedirs(USER_FILES_ROOT)

import yaml
from skymusic.music_sheet_maker import MusicSheetMaker
from skymusic.communicator import Communicator, QueriesExecutionAbort
from skymusic import Lang
from skymusic import Config
from skymusic.resources import Resources
try:
    import readline
except ModuleNotFoundError:
    pass  # probably Windows

args = Config.parse_args()
cfg = Config.get_configuration(args)

#=========================================
#SETTINGS FOR ADVANCED USERS
SKYJSON_URL = cfg["skyjson_url"] # To generate a temporary song link at sky-music.herokuapp.com. By default will be enabled on the Discord Music Cog but disabled on the command line (to avoid spamming this server). Always disabled if batch_mode is True
SONG_IN_DIR = cfg["song_dir_in"] or os.path.join(USER_FILES_ROOT, 'test_songs') # Overrides defaut input song folder
SONG_OUT_DIR = cfg["song_dir_out"] or os.path.join(USER_FILES_ROOT, 'songs_out') # Overrides defaut output song folder
BATCH_MODE = cfg["batch_mode"] # To process songs in a batch,stored as .yaml files
BATCH_DIR = cfg["batch_dir"] or os.path.join(USER_FILES_ROOT, 'batch_songs')
PREFERENCES_PATH = cfg["pref_file"] or os.path.join(USER_FILES_ROOT, 'skymusic_preferences.yaml')
#==========================================

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

    def __init__(self, locale='en_US', preferences_path='../skymusic_preferences.yaml'):
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
                        answer = input(f"{question}: ")
                        q.reply_to(answer)
                    reply_valid = q.get_reply_validity()
                else:
                    print('\n'+question)
                    q.reply_to("ok")
                    reply_valid = q.get_reply_validity()


try:
    player = CommandLinePlayer(locale=Lang.guess_locale(), preferences_path=PREFERENCES_PATH)
    maker = MusicSheetMaker(locale=Lang.guess_locale(), application_root=application_root, song_in_dir=SONG_IN_DIR, song_out_dir=SONG_OUT_DIR, enable_skyjson_url=(SKYJSON_URL and not BATCH_MODE))

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

