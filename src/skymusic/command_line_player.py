#!/usr/bin/env python3
import os, sys

#Gets the directory from which the script is executed, either as a python script or as a bundle (PyInstalled dist) or an executable (PyInstaller one-file)
try:
    this_file = os.path.abspath(__file__)
except NameError:
    this_file = os.path.abspath(sys.argv[0])
if getattr(sys, 'frozen', False): #PyInstaller
    application_root = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
else: #normal python script
    application_root = os.path.dirname(this_file)

if __name__ == '__main__' and not getattr(sys, 'frozen', False): #Local Script
    # The '../' has to be changed if the directory structure is changed, in particular if the current file location (__file__) is changed
    PACKAGE_ROOT = os.path.normpath(os.path.join(application_root, '../'))
    USER_FILES_ROOT = os.path.normpath(os.path.join(application_root, '../../'))
    # the skymusic package root directory must be added to the system PATH:
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
SKYJSON_URL = cfg["skyjson_url"] # True / None / <alphanumeric> value. To generate a temporary song link at sky-music.herokuapp.com. By default this feature will be enabled on the Discord Music Cog but disabled on the command line (to avoid spamming this server). Always disabled if batch_mode is True
# Settings from command-line arguments, or from default values:
SONG_IN_DIR = cfg["song_dir_in"] or os.path.join(USER_FILES_ROOT, 'test_songs') # Overrides defaut input song folder
SONG_OUT_DIR = cfg["song_dir_out"] or os.path.join(USER_FILES_ROOT, 'songs_out') # Overrides defaut output song folder
BATCH_MODE = cfg["batch_mode"] # To process songs in a batch,stored as .yaml files
BATCH_DIR = cfg["batch_dir"] or os.path.join(USER_FILES_ROOT, 'batch_songs')
PREFERENCES_PATH = cfg["pref_file"] or os.path.join(USER_FILES_ROOT, 'skymusic_preferences.yaml')
#==========================================

class CommandLinePlayer:
    """
    A command-line puppet to speak with the Music Sheet Maker.
    CAUTION: All puppets must have the following methods:
        - get_name(), returning a name among the authorized locutors list of communication.py
        - get_locale(), returning a language code string 'xx.YY'
        - execute_queries()
        - a Communicator to handle Queries (ask and answer questions)
    It is recommended to add a receive() method or a __getattr__ method
    to call communication methods directly from the  puppet instead of the communicator.
    """

    def __init__(self, locale=None, preferences_path='../skymusic_preferences.yaml'):
        self.name = Resources.COMMAND_LINE_NAME
        self.preferences = self.load_preferences(preferences_path)
        if locale is None: locale = self.get_locale_from_prefs()
        self.set_locale(locale)
        self.communicator = Communicator(owner=self, locale=self.locale)
        self.yaml_song = None

    def __getattr__(self, attr_name):
        """
        Default function to call in case no one else is found.
        Useful in case of confusion between the puppet and its communicator
        """
        if 'communicator' in self.__dict__.keys():
            return getattr(self.communicator, attr_name)
        else:
            raise AttributeError(f"type object '{type(self).__name__}' has no attribute 'communicator'")

    def get_name(self):
        """Mandatory: any string for a name"""
        return self.name

    def get_locale(self):
        """Mandatory: spoken language, taken from yaml prefs, or executing OS"""
        return self.locale

    def set_locale(self, locale):
        """Try to guess locale and find it in the database, or use the closest match found, or revert to en-US"""
        if locale is None: locale = Lang.guess_locale()
        self.locale = Lang.check_locale(locale)
        if self.locale is None:
            self.locale = Lang.find_substitute(locale)
            print(f"**WARNING: bad locale type passed to CommandLinePlayer: {locale}. Reverting to {self.locale}")

        return self.locale

    def get_locale_from_prefs(self):
        """Get locale from yaml preferences file
        """
        try:
            locale = self.preferences['locale']
        except (TypeError,KeyError):
            locale = None

        return locale        

    def fetch_yaml_songs(self, songs_dir):
        """Load all the yaml files of the batch_song directory (batch mode only)"""
        dirpath, _, filenames = next(os.walk(songs_dir), (None, None, []))

        for filename in filenames:
            if os.path.splitext(filename)[1].lower().strip() != '.yaml':
                filenames.remove(filename)

        self.yaml_songs = [os.path.normpath(os.path.join(dirpath, filename)) for filename in filenames]

        return self.yaml_songs

    def load_preferences(self, filepath):
        """Loads the preferences.yaml file with default answers to questions, if it exists"""
        try:
            with open(filepath, mode='r', encoding='utf-8', errors='ignore') as file:
                print(f"(Loaded preferences file from {filepath})")
                return yaml.safe_load(file)
        except (FileNotFoundError, PermissionError):
            return None

    def get_answer_from_preferences(self, q):
        """Try to get the answer to a question by probing the preferences dictionary, which was populated from the preferences.yaml"""
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
        """Batch only: Try to get the answer to a question by probing the song dictionary, which was populated from the yaml file"""
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
        """Batch mode only: loads the .yaml file in the batch_songs directory, containing answers to questions for a particular song"""
        try:
            with open(filepath, mode='r', encoding='utf-8', errors='ignore') as file:
                self.yaml_song = yaml.safe_load(file)
                return self.yaml_song
        except (FileNotFoundError, PermissionError):
            return None


    def receive(self, *args, **kwargs):
        """Shortcut to receive an answer from the other party's communicator'"""
        self.communicator.receive(*args, **kwargs)


    def execute_queries(self, queries=None):
        """Ask a question and waits for the answer"""
        if queries is None:
            self.communicator.memory.clean()
            queries = self.communicator.recall_unsatisfied(filters=('to_me'))
        else:
            if not isinstance(queries, (list, set)):
                queries = [queries]
        """
        The following part is specific to the command line, because it uses command-lîe prompts and a yaml preference file
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

# MAIN SCRIPT
try:
    player = CommandLinePlayer(preferences_path=PREFERENCES_PATH) # Me
    maker = MusicSheetMaker(locale=player.get_locale(), application_root=application_root, song_in_dir=SONG_IN_DIR, song_out_dir=SONG_OUT_DIR, skyjson_url_api=(SKYJSON_URL if not BATCH_MODE else None)) # The other party

    if BATCH_MODE:
        # process a song using a yaml file instead of asking questions in the command prompt
        file_paths = player.fetch_yaml_songs(BATCH_DIR)
        for file_path in file_paths:
            player.load_yaml_song(file_path)
            q = player.communicator.send_stock_query('create_song', recipient=maker)
            maker.execute_queries(q)
            maker.communicator.flush()
            player.communicator.flush()
    else:
        # We start the program by asking the music sheet maker to start a new song
        q = player.communicator.send_stock_query('create_song', recipient=maker)
        maker.execute_queries(q)

except QueriesExecutionAbort as qExecAbort:
    # In case of an abort command, we break the loop
    print(qExecAbort)

