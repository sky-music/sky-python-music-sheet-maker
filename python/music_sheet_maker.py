import os, io, re
from modes import InputMode, CSSMode, RenderMode, ReplyType
from communicator import Communicator, QueriesExecutionAbort
from songparser import SongParser
import Lang
#from song import Song


class MusicSheetMakerError(Exception):
    def __init__(self, explanation):
        self.explanation = explanation

    def __str__(self):
        return str(self.explanation)
    
    pass


class MusicSheetMaker:

    def __init__(self, locale='en_US', songs_in='test_songs', songs_out='songs_out'):
        self.name = 'music-sheet-maker'
        self.locale=self.set_locale(locale)
        self.communicator = Communicator(owner=self, locale=self.locale)
        self.song = None
        self.song_parser = None
        self.directory_base = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
        self.song_dir_in = os.path.join(self.directory_base,songs_in)
        self.song_dir_out = os.path.join(self.directory_base,songs_out)
        self.css_path = os.path.normpath(os.path.join(self.directory_base, "css/main.css"))#TODO: move that into Renderer
        self.rel_css_path = os.path.relpath(self.css_path, start=self.song_dir_out)
        self.css_mode = CSSMode.EMBED#TODO: move that into Renderer
        self.render_modes_enabled = [mode for mode in RenderMode]
        # self.render_modes_disabled = [RenderMode.JIANPUASCII, RenderMode.DOREMIASCII]
        self.render_modes_disabled = []
        self.render_modes_enabled = [mode for mode in self.render_modes_enabled if
                                     mode not in self.render_modes_disabled]
        self.botcog_render_modes = [RenderMode.PNG]
        self.website_render_modes = [RenderMode.HTML]
        
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
            self.locale = Lang.guess_locale()
            print("**WARNING: bad locale type %s passed to MusicSheetMaker. Reverting to %s"%(locale, self.locale))
            
        return self.locale

    
    def is_botcog(self, recipient):
        try:
            is_bot = recipient.get_name() == "music-cog"
        except AttributeError:
            try: # Guesses harder
                recipient.bot
                is_bot = True
            except AttributeError:
                is_bot = False
        return is_bot


    def is_website(self, recipient):
        try:
            is_website = recipient.get_name() == "sky-music-website"
        except AttributeError:
            try: # Guesses harder
                recipient.session_ID
                is_website = True
            except:
                is_website = False

        return is_website

    def is_commandline(self, recipient): 
        try:
            return recipient.get_name() == "command-line"
        except AttributeError: # Guesses harder
            return not (self.is_botcog(recipient) or self.is_website(recipient))

    def get_song(self):
        return self.song

    def set_song(self, song):
        self.song = song

    def get_song_parser(self):
        return self.song_parser

    def set_song_parser(self, song_parser=None):
        if song_parser is None:
            song_parser = SongParser(self)
        self.song_parser = song_parser

    def get_directory_base(self):
        return self.directory_base
    
    def get_render_modes_enabled(self):

        return self.render_modes_enabled

    def execute_queries(self, queries=None):

        if queries is None:
            self.communicator.memory.clean()
            queries = self.communicator.memory.recall_unsatisfied(filters=('to_me'))
        else:
            if not isinstance(queries, (list, set)):
                queries = [queries]
        #2 lines for debugging:
        #print('\n%%%%I AM MAKER, THE UNSATISFIED QUERIES ARE:%%%%')
        #self.communicator.memory.print_out(filters=('unsatisfied'))

        """
        The query statisfaction loop:
        runs until all queries are satisfied
        """
        reply_valid = False
        while not reply_valid:
            reply_valid = True #To break the loop if no query
            for q in queries:
                #Fetching the stock Query name and arguments 
                query_name = q.get_name()
                try:   
                    stock_query = self.communicator.query_stock[query_name]
                    handler_args = ', '.join(('sender=q.get_sender()','query=q'))
                    expression = 'self.' + str(stock_query['handler']) + '(' + handler_args + ')'
                except KeyError as err:
                    #TODO: handle non-stock queries???
                    raise MusicSheetMakerError('Cannot create stock query ' + repr(query_name) + ', because of ' + repr(err))
                    pass
                #Actual evaluation of the stock query
                try:
                    answer = eval(expression)
                    q.reply_to(answer)
                    reply_valid = q.get_reply_validity()
                    
                except QueriesExecutionAbort as qExecAbort:
                    raise qExecAbort

    '''
    def next_step(self, recipient, step_number=0):
        """
        Starts the next step of song creation for the given recipient
        Requires a current_step dictionary
        """
        steps = [self.ask_instructions, self.ask_render_modes, self.ask_notes_or_file, self.ask_input_mode,
                 self.set_parser_input_mode, self.ask_song_key, self.ask_octave_shift, self.parse_song,
                 self.display_error_ratio, self.ask_song_metadata, self.set_song_metadata]
              
        if step_number == 0:
            res = self.set_song_parser()
        elif step_number > 1 and step_number < len(steps) + 1:
            res = steps[step_number](recipient)
        else:
            res = self.render_song(recipient)

        if isinstance(res, tuple):
            (q, r) = res
            try:
                q.expect_reply()
                return q
            except AttributeError:
                pass
            try:
                q[0].expect_reply()
                return q
            except (IndexError, AttributeError):
                pass
                
        return None
    '''
        
    def create_song(self, **kwargs):
        """
        A very linear, sequential way of building a song from user inputs
        Returns a list of tuples (buffers, types) where buffers is a list of IOString/IOBytes buffers, and types the list of their types
        """
        try:
            recipient = kwargs['sender']
        except KeyError:
            raise MusicSheetMakerError('No recipient specified for the Song')

        #Actually the following is not used but it may be useful to have the triggering query as an argument
        try:
            q_create_song = kwargs['query']
        except KeyError:
            raise MusicSheetMakerError('No Query passed to create_song')               
        
        #======= NEW SONG =======
        
        # 1. Set Song Parser
        self.set_song_parser()

        # 2. Display instructions
        (i_instr, res) = self.ask_instructions(recipient=recipient)
    
        # 2.b Ask for render modes (query created for website only)
        (q_render, render_modes) = self.ask_render_modes(recipient=recipient)
    
        # 3. Ask for notes
        #TODO: allow the player to enter the notes using several messages??? or maybe not
        (q_notes, notes) = self.ask_notes_or_file(recipient=recipient, prerequisites=[i_instr])
        
        # 4. Ask for input mode (or display the one found)
        (q_mode, input_mode) = self.ask_input_mode(recipient=recipient, notes=notes, prerequisites=[q_notes])
        #(q_mode, input_mode) = self.ask_input_mode(recipient=recipient, prerequisites=[q_notes]) #TODO EXPERIMENTAL
        
        # 5. Set input_mode
        self.get_song_parser().set_input_mode(input_mode)
        #self.set_parser_input_mode(recipient) #TODO EXPERIMENTAL
        
        # 6. Ask for song key (or display the only one possible)
        (q_key, song_key) = self.ask_song_key(recipient=recipient, notes=notes, input_mode=input_mode, prerequisites=[q_notes, q_mode])
        #(q_key, song_key) = self.ask_song_key(recipient=recipient, prerequisites=[q_notes, q_mode]) #TODO EXPERIMENTAL
       
        # 7. Asks for octave shift
        (q_shift, octave_shift) = self.ask_octave_shift(recipient=recipient)
        
        # 8. Parse song
        self.parse_song(recipient, notes=notes, song_key=song_key, octave_shift=octave_shift)
        #self.parse_song(recipient) #TODO EXPERIMENTAL
        
        # 9. Displays error ratio
        (i_error, res) = self.display_error_ratio(recipient=recipient, prerequisites=[q_notes, q_mode, q_shift])
        
        # 10. Asks for song metadata
        (qs_meta, (title, artist, transcript)) = self.ask_song_metadata(recipient=recipient)
        
        self.set_song_metadata(recipient=recipient, meta=(title, artist, transcript), song_key=song_key)
        #self.set_song_metadata(recipient=recipient) #TODO EXPERIMENTAL
        
        # 11. Renders Song
        song_bundle = self.render_song(recipient, render_modes)
        
        # 12. Sends result back (required for website)
        return song_bundle
    
   
    def ask_instructions(self, recipient, prerequisites=None, execute=True):
        
        question_rep = ('\n'.join(['\n* ' + input_mode.get_long_desc(self.locale) for input_mode in InputMode]),
                        self.get_song_parser().get_icon_delimiter(), self.get_song_parser().get_pause(),
                        self.get_song_parser().get_quaver_delimiter(), self.get_song_parser().get_quaver_delimiter().join(['A1','B1','C1']),
                        self.get_song_parser().get_repeat_indicator()+'2'
                        )
                
        if self.is_commandline(recipient):      
            i_instr = self.communicator.send_stock_query('instructions_stdout', recipient=recipient, question_rep=question_rep, prerequisites=prerequisites)
        elif self.is_website(recipient):
            i_instr = self.communicator.send_stock_query('instructions_website', recipient=recipient, question_rep=question_rep, prerequisites=prerequisites)
        else:
            i_instr = self.communicator.send_stock_query('instructions_botcog', recipient=recipient, question_rep=question_rep, prerequisites=prerequisites)            
        
        if execute:
            recipient.execute_queries(i_instr)
            instructions = i_instr.get_reply().get_result()
            return (i_instr, instructions)
        else:
            return (i_instr, None)
                                  
   
    def ask_song_metadata(self, recipient, prerequisites=None, execute=True):

        queries = []

        queries += [self.communicator.send_stock_query('song_title', recipient=recipient, prerequisites=prerequisites)]
        queries += [self.communicator.send_stock_query('original_artist', recipient=recipient, prerequisites=prerequisites)]
        queries += [self.communicator.send_stock_query('transcript_writer', recipient=recipient, prerequisites=prerequisites)]

        if execute:
            recipient.execute_queries(queries)
            meta_data = [q.get_reply().get_result() for q in queries]
            return (queries, tuple(meta_data))
        else:
            return (queries, None)


    def retrieve_song_metadata(self, recipient):
        '''
        Experimental
        '''
        (title, artist, transcript) = (None, None, None)
        
        q_title = self.communicator.recall_by_recipient(recipient, criterion="song_title", filters=["valid_reply"], sort_by="date")
        q_artist = self.communicator.recall_by_recipient(recipient, criterion="original_artist", filters=["valid_reply"], sort_by="date")
        q_transcript = self.communicator.recall_by_recipient(recipient, criterion="transcript_writer", filters=["valid_reply"], sort_by="date")

        if len(q_title) != 0:
            title = q_title[-1].get_reply().get_result()
        if len(q_artist) != 0:
            artist = q_artist[-1].get_reply().get_result()
        if len(q_transcript) != 0:
            transcript = q_transcript[-1].get_reply().get_result()
         
        return (title, artist, transcript)


    def ask_notes(self, recipient, prerequisites=None, execute=True):
        
        q_notes = self.communicator.send_stock_query('notes', recipient=recipient, prerequisites=prerequisites)            
             
        if execute:
            recipient.execute_queries(q_notes)
            notes = q_notes.get_reply().get_result()
            return (q_notes, notes)
        else:
            return (q_notes, None)

    
    def ask_file(self, recipient, prerequisites=None, execute=True):
                   
        q_file = self.communicator.send_stock_query('file', recipient=recipient, question_rep=(os.path.relpath(os.path.normpath(self.song_dir_in)),),
                                                    prerequisites=prerequisites, limits=(os.path.normpath(self.song_dir_in)))
        
        if execute:
            recipient.execute_queries(q_file)
            file_name = q_file.get_reply().get_result()
            file_path = os.path.join(self.song_dir_in, os.path.normpath(file_name))
            return (q_file, file_path) #should return file name
        else:
            return (q_file, None)
        
    
    def read_file(self, file_path):
        
        isfile = os.path.isfile(file_path)
        
        if not isfile:
            MusicSheetMakerError('File does not exist: ' + os.path.abspath(file_path))
        else:
            #load file
            try:
                with open(file_path, mode='r', encoding='utf-8', errors='ignore') as fp:
                    lines = fp.readlines() #Returns a list of strings
            except (OSError, IOError) as err:
                raise err
                
            return lines


    def ask_notes_or_file(self, recipient, prerequisites=None, execute=True):
        """
        Asks for notes (all recipients) or a file name (command-line only)
        If a file name is detected but the file does not exist, sends a query to ask for a valid file path
        If notes are detected, return the notes as a list of strings splitted by the OS line separator
        """
        
        if not self.is_commandline(recipient):
            
            return self.ask_notes(recipient=recipient, prerequisites=prerequisites, execute=execute)
        
        else:
                            
            q_notes = self.communicator.send_stock_query('notes_file', question_rep=(os.path.relpath(os.path.normpath(self.song_dir_in)),),
                                                         recipient=recipient, prerequisites=prerequisites)
            
            if not execute:            
                return (q_notes, None)      
            else:            
                recipient.execute_queries(q_notes)
                
                result = q_notes.get_reply().get_result()
                
                if self.is_commandline(recipient):
                    #Detects if the result is a file path
                    file_path = os.path.join(self.song_dir_in, os.path.normpath(result))
                    isfile = os.path.isfile(file_path)
                    
                    if not isfile:
                        splitted = os.path.splitext(result)
                        if len(splitted[0]) > 0 and 2 < len(splitted[1]) <= 5 and re.search('\\.', splitted[0]) is None:
                            # then certainly a file name
                            self.communicator.memory.erase(q_notes)
                                            
                            q_notes, file_path = self.ask_file(recipient=recipient, prerequisites=prerequisites, execute=execute)
                            isfile = True #ask_file only returns when a valid file path is found
                else:
                    isfile = False #Don't allow reading files on the website or music-cog
                    
                if isfile and self.is_commandline(recipient):
                    notes = self.read_file(file_path)
                    print('(Song imported from %s)'%os.path.abspath(file_path))
                else:             
                    notes = result.split(os.linesep) # Returns a list of strings in any case
                    
                    if self.is_commandline(recipient): #Loop to ask for several lines in the standard input interface           
                        while result:                            
                            q_notes = self.communicator.send_stock_query('notes', recipient=recipient, prerequisites=prerequisites)
                            recipient.execute_queries(q_notes)
                            result = q_notes.get_reply().get_result()
                            
                            result = result.split(os.linesep)
                            for result in result:
                                notes.append(result)
                      
                return (q_notes, notes)

     
    def retrieve_notes(self, recipient):
        '''
        Experimental
        '''        
        q_notes_file = self.communicator.recall_by_recipient(recipient, criterion="file|notes_file", filters=["valid_reply"], sort_by="date")
        if len(q_notes_file) != 0:
            result = q_notes_file[-1].get_reply().get_result()
            file_path = os.path.join(self.song_dir_in, os.path.normpath(result))
            isfile = os.path.isfile(file_path)
            
            if isfile and self.is_commandline(recipient):
                notes = self.read_file(file_path)
            else:
                notes = result.split(os.linesep) 
            return notes
            
        
        q_notes = self.communicator.recall_by_recipient(recipient, criterion="notes", filters=["valid_reply"], sort_by="date")
        if len(q_notes) != 0:
            notes = q_notes_file[-1].get_reply().get_result().split(os.linesep)
            return notes
        
        

    def ask_render_modes(self, recipient, prerequisites=None, execute=True):
        """
        Asks for the desired render modes for the Song
        """
        
        render_modes = self.render_modes_enabled

        if len(render_modes) == 1:
            return (None, render_modes)

        if self.is_commandline(recipient):
            
            return (None, render_modes)
            
        elif self.is_botcog(recipient):
            
            return (None, self.botcog_render_modes)
            
        else:

            q_render = self.communicator.send_stock_query('render_modes', recipient=recipient, limits=render_modes, prerequisites=prerequisites)
            
            if execute:
                recipient.execute_queries(q_render)
                render_modes = q_render.get_reply().get_result()
                return (q_render, render_modes)
            else:
                return (q_render, None)


    def ask_input_mode(self, recipient, notes=None, prerequisites=None, execute=True):
        """
        Try to guess the musical notation and asks the player to confirm
        """
        
        if notes is None:
            notes = self.retrieve_notes(recipient)
        
        possible_modes = self.get_song_parser().get_possible_modes(notes)
                
        if len(possible_modes) == 0:
            #To avoid loopholes. I am not sure this case is ever reached, because get_possible_modes should return all modes if None is found.
            all_input_modes = [mode for mode in InputMode]
            
            q_mode = self.communicator.send_stock_query('musical_notation', recipient=recipient,
            limits=all_input_modes, prerequisites=prerequisites)
            
        elif len(possible_modes) == 1:
            q_mode = self.communicator.send_stock_query('one_input_mode', recipient=recipient, 
                                                        question_rep=(possible_modes[0].get_short_desc(self.locale),), prerequisites=prerequisites)
            
        else:
            q_mode = self.communicator.send_stock_query('musical_notation', recipient=recipient, limits=possible_modes, prerequisites=prerequisites)
        
        if len(possible_modes) == 1:
            mode = possible_modes[0]
        else:
            mode = None
        
        if execute:
            recipient.execute_queries(q_mode)
            if len(possible_modes) != 1:
                mode = q_mode.get_reply().get_result()
            return (q_mode, mode)
        else:
            return (q_mode, mode)


    def retrieve_input_mode(self, recipient, notes=None):
        '''
        Experimental
        '''        
        if notes is None:
            notes = self.retrieve_notes(recipient)
        
        try:
            input_mode = self.get_song_parser.get_input_mode()
        except:
            input_mode = None
                
        if input_mode is None:
            q_mode = self.communicator.recall_by_recipient(recipient, criterion=ReplyType.INPUTMODE, filters=["valid_reply"], sort_by="date")
            if len(q_mode) == 0:
                input_mode = self.get_song_parser().get_possible_modes(notes)[0]
            else:
                input_mode = q_mode[-1].get_reply().get_result()

        return input_mode


    def ask_song_key(self, recipient, notes=None, input_mode=None, prerequisites=None, execute=True):
        """
        Attempts to detect key for input written in absolute musical scales (western, Jianpu)
        """
        #EXPERIMENTAL
        if notes is None:
            notes = self.retrieve_notes(recipient)
       
        if input_mode is None:
            input_mode = self.retrieve_input_mode(recipient, notes)
                        
        song_key = None       
        possible_keys = self.get_song_parser().find_key(notes)
        
        if possible_keys is None:
            #Asks for any text string
            q_key = self.communicator.send_stock_query('recommended_key', recipient=recipient, prerequisites=prerequisites)
        
        elif len(possible_keys) == 0:
            #Sends information that there is no possible key
            q_key = self.communicator.send_stock_query('no_possible_key', recipient=recipient, prerequisites=prerequisites)
            possible_keys = ['C']

        elif len(possible_keys) == 1:
            #Sends information that there is only 1 possible key
            q_key = self.communicator.send_stock_query('one_possible_key', recipient=recipient,
                                                       question_rep=(str(possible_keys[0]),), prerequisites=prerequisites)
        else:
            #Asks to choose a key within a list
            q_key = self.communicator.send_stock_query('possible_keys', recipient=recipient,
                                                       foreword_rep=(', '.join(possible_keys),), limits=possible_keys, prerequisites=prerequisites)

        if execute:
            
            recipient.execute_queries(q_key)
            if possible_keys is None:
                song_key = q_key.get_reply().get_result()
                if len(song_key.strip()) == 0:
                    song_key = 'C'
            elif len(possible_keys) == 1:
                song_key =  possible_keys[0]
            elif len(possible_keys) > 1:
                song_key = q_key.get_reply().get_result() 
            else:
                raise MusicSheetMakerError('Possible keys is an empty list.')
                
            return (q_key, song_key)
        
        else:#Not execute
            
            if possible_keys is None:
                song_key =  None
            elif len(possible_keys) == 1:
                song_key =  possible_keys[0]
            else:
                song_key = None
                
            return (q_key, song_key)
    

    def retrieve_song_key(self, recipient, notes=None, input_mode=None):
        '''
        Experimental
        '''
        if notes is None:
            notes = self.retrieve_notes(recipient)
        
        if input_mode is None:
            input_mode = self.retrieve_input_mode(recipient, notes=notes)

        song_key = None
        
        q_key = self.communicator.recall_by_recipient(recipient, criterion="possible_keys", filters=["valid_reply"], sort_by="date")
        if len(q_key) != 0:
            return q_key[-1].get_reply().get_result()
        
        q_key = self.communicator.recall_by_recipient(recipient, criterion="recommended_key", filters=["valid_reply"], sort_by="date")
        if len(q_key) != 0:
            song_key = q_key[-1].get_reply().get_result()
            if len(song_key.strip()) == 0:
                song_key = 'C'
            return song_key

        q_key = self.communicator.recall_by_recipient(recipient, criterion="one_possible_key", filters=["valid_reply"], sort_by="date")
        if len(q_key) != 0:
            try:
                return self.get_song_parser().find_key(notes)[0]
            except TypeError:
                return 'C'

        q_key = self.communicator.recall_by_recipeint(recipient, criterion="no_possible_key", filters=["valid_reply"], sort_by="date")
        if len(q_key) != 0:
            return 'C'
        
        return 'C'                
        

    def ask_octave_shift(self, recipient, prerequisites=None, execute=True):
    
        q_shift = self.communicator.send_stock_query('octave_shift', recipient=recipient, prerequisites=prerequisites)
        
        if execute:
            recipient.execute_queries(q_shift)
            octave_shift = q_shift.get_reply().get_result()
            return (q_shift, octave_shift)
        else:
            return (q_shift, None)

    def retrieve_octave_shift(self, recipient):    
        '''
        Experimental
        '''
        q_shift = self.communicator.recall_by_recipient(recipient, criterion="octave_shift", filters=["valid_reply"], sort_by="date")
        if len(q_shift) == 0:
            octave_shift = 0
        else: 
            octave_shift = q_shift[-1].get_reply().get_result()
        return octave_shift   
    
        
    def send_buffers_to_botcog(self, buffers, recipient, prerequisites=None, execute=True):
        '''
        Discord only
        TODO: fill this method, or if very short, put it inside create_song directly, or delete it if unused
        '''
        return buffers
        
        
    def display_error_ratio(self, recipient, prerequisites=None, execute=True):

        error_ratio = self.get_song().get_num_broken() / max(1, self.get_song().get_num_instruments())
       
        if error_ratio == 0:
            i_error = None
        elif error_ratio < 0.05:
            i_error = self.communicator.send_stock_query('few_errors', recipient=recipient, prerequisites=prerequisites)
        else:
            i_error = self.communicator.send_stock_query('many_errors', recipient=recipient, prerequisites=prerequisites)
        
        if execute and i_error is not None:
            recipient.execute_queries(i_error)
            error_message = i_error.get_reply().get_result()
            return (i_error, error_message)
        else:
            return (i_error, None)


    def set_parser_input_mode(self, recipient, notes=None, input_mode=None):
        
        if input_mode is None:
            if notes is None:
                notes = self.retrieve_notes(recipient)
                input_mode = self.retrieve_input_mode(recipient, notes)
            else:
                raise MusicSheetMakerError('Could not retrieve input_modes because no notes were given.')

        self.get_song_parser().set_input_mode(input_mode)


    def set_song_metadata(self, recipient, meta=None, song_key=None, notes=None):
        
        if meta is None:
            (title, artist, transcript) = self.retrieve_song_metadata(recipient)
        else:
            (title, artist, transcript) = meta
         
        if song_key is None:
            song_key = self.retrieve_song_key(recipient)
                
        self.get_song().set_meta(title=title, artist=artist, transcript=transcript, song_key=song_key)


    def parse_song(self, recipient, notes=None, song_key=None, octave_shift=None):

        if notes is None:
            notes = self.retrieve_notes(recipient)
        
        if octave_shift is None:
            octave_shift = self.retrieve_octave_shift(recipient)

        if song_key is None:
            song_key = self.retrieve_song_key(recipient, notes=notes)
                
        self.set_song(self.get_song_parser().parse_song(song_lines=notes, song_key=song_key, octave_shift=octave_shift))

        return

    '''
    def retrieve_render_modes(self, recipient):
        
        q_render = self.communicator.recall_by_recipient(recipient, criterion="render_modes", filters=["valid_reply"], sort_by="date")
        if len(q_render) != 0:  
            render_modes = q_render.get_reply().get_result()
            return render_modes
    '''           

    def render_song(self, recipient, render_modes=None):
        
        if render_modes is None:
            if self.is_botcog(recipient):
                render_modes = self.botcog_render_modes
            elif self.is_website(recipient):
                render_modes = self.website_render_modes
            else:
                render_modes = self.render_modes_enabled
                
        if self.is_commandline(recipient):
                        
            print("="*40)            
            song_bundle = []
            for render_mode in render_modes:
                buffers = self.write_song_to_buffers(render_mode) # A list of IOString or IOBytes buffers
                file_paths = self.build_file_paths(render_mode, len(buffers))              
                self.send_buffers_to_files(render_mode, buffers, file_paths, recipient=recipient)
                song_bundle.append((buffers, [render_mode]*len(buffers)))
                
        else: #website or botcog or...
            
            self.css_mode = CSSMode.EMBED #Prevent the HTML/SVG from depending on an auxiliary .css file            
            song_bundle = [] # A list of tuples
            for render_mode in render_modes:                
                buffers = self.write_song_to_buffers(render_mode) # A list of IOString or IOBytes buffers
                song_bundle.append((buffers, [render_mode]*len(buffers)))          
        
        return song_bundle
        

    def send_buffers_to_files(self, render_mode, buffers, file_paths, recipient, prerequisites=None, execute=True):
        """
        Writes the content of an IOString or IOBytes buffer list to one or several files.
        Command line only
        """
        #TODO: Move this method in Renderer???
        try:
            numfiles = len(buffers)
        except (TypeError, AttributeError):
            buffers = [buffers]
            numfiles = 1
        
        #Creates output directory if did not exist
        if not os.path.isdir(self.song_dir_out):
            os.mkdir(self.song_dir_out)

        if len(buffers) != len(file_paths):
            raise MusicSheetMakerError('inconsistent lengths of buffers and file_paths')

        (file_base, file_ext) = os.path.splitext(file_paths[0])

        for i, buffer in enumerate(buffers):

            if isinstance(buffer, io.StringIO):
                output_file = open(file_paths[i], 'w+', encoding='utf-8', errors='ignore')
            elif isinstance(buffer, io.BytesIO):
                output_file = open(file_paths[i], 'bw+')
            elif buffer is None:
                pass
            else:
                raise MusicSheetMakerError('Unknown buffer type in ' + str(self))
            
            
            if buffer is not None:
                output_file.write(buffer.getvalue())
            
                if numfiles == 1:
                    
                    question_rep = (render_mode.get_short_desc(self.locale), str(os.path.relpath(file_paths[0])))
                    
                    i_song_files = self.communicator.send_stock_query('one_song_file', recipient=recipient, question_rep=question_rep, prerequisites=prerequisites)
                    
                elif numfiles > 1 and i == 0:
                    
                    question_rep = (render_mode.get_short_desc(self.locale), str(os.path.relpath(self.song_dir_out)))
                    afterword_rep = (str(numfiles), str(os.path.split(file_paths[0])[1]), str(os.path.split(file_paths[-1])[1]))
                    i_song_files = self.communicator.send_stock_query('several_song_files', recipient=recipient, question_rep=question_rep, afterword_rep=afterword_rep, prerequisites=prerequisites)
            else:
                question_rep = (render_mode.get_short_desc(self.locale),)
                i_song_files = self.communicator.send_stock_query('no_song_file', recipient=recipient, question_rep=question_rep, prerequisites=prerequisites)
        
        if execute:
            recipient.execute_queries(i_song_files)
            result = i_song_files.get_reply().get_result()
            return (i_song_files, result)
        else:
            return (i_song_files, None)

            
    def write_song_to_buffers(self, render_mode):
        """
        Writes the song to files with different formats as defined in RenderMode
        Returns a list [], even if it has only 1 element
        """
        #TODO: Move this method to Renderer?
        if render_mode in self.get_render_modes_enabled():

            if render_mode == RenderMode.HTML:
                buffers = [self.get_song().write_html(self.css_mode, self.css_path, self.rel_css_path)]
            elif render_mode == RenderMode.SVG:
                buffers = self.get_song().write_svg(self.css_mode, self.css_path, self.rel_css_path)
            elif render_mode == RenderMode.PNG:
                buffers = self.get_song().write_png()
            elif render_mode == RenderMode.MIDI:
                buffers = [self.get_song().write_midi()]
            else:  # Ascii
                buffers = [self.get_song().write_ascii(render_mode)]

        else:
            buffers = []
            
        for buffer in buffers:
            if buffer is not None:
                buffer.seek(0)

        return buffers
    
    def build_file_paths(self, render_mode, numfiles):
        '''
        Command line only : generates a list of file paths for a given input mode.
        '''
        #TODO: move this method in Renderer???
        if numfiles == 0:
            return None

        file_base = os.path.join(self.song_dir_out, self.get_song().get_title())
        file_ext = render_mode.extension
        
        file_paths = []
        if numfiles > 1:
            for i in range(numfiles):
                file_paths += [file_base + str(i) + file_ext]
        else:
            file_paths = [file_base + file_ext]

        return file_paths

