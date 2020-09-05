import os, io, re
from skymusic.modes import InputMode, CSSMode, RenderMode, ReplyType, AspectRatio
from skymusic.communicator import Communicator, QueriesExecutionAbort
from skymusic.parsers.song_parser import SongParser
from skymusic.renderers.song_renderers.song_renderer import SongRenderer
from skymusic.renderers.song_renderers import skyjson_sr
from skymusic import Lang
from skymusic.resources import Resources


class MusicSheetMakerError(Exception):
    def __init__(self, explanation):
        self.explanation = explanation

    def __str__(self):
        return str(self.explanation)

    pass


class SongBundle:
    """
    An object containing a song rendered in several formats
    """
    def __init__(self):
        
        self.meta = {}
        self.renders = {} #{render_mode: [buffers]}

    def __len__(self):
        
        return len(self.renders.keys())
     
    def get_size(self):
        
       return ( len(self.renders.keys()), sum([len(buffers) for buffers in self.renders.values()]) )     
        
    def __repr__(self):
        
        size = self.get_size()
        return f'<SongBundle, {size[0]} render modes, {size[1]} buffers total>'
        
    def set_meta(self, song_meta: dict):
        
        meta = {}
        for k in song_meta:
            meta.update({k: song_meta[k][1]})
        
        self.meta.update(meta)

    def get_sanitized_song_title(self):
        
        try:
            title = self.meta['title']
            sanitized_title = re.sub(r'[\\/:"*?<>|]', '', re.escape(title)).strip()
            sanitized_title = re.sub('(\s)+', '_', sanitized_title)  # replaces spaces by underscore
            sanitized_title = sanitized_title[:31]
            return sanitized_title
        except KeyError:
            return ''
        
    def get_meta(self):
        
        return self.meta
    
    def add_render(self, render_mode, buffers):
        
        if render_mode not in RenderMode:
            raise MusicSheetMakerError(f'{render_mode} passed to SongBundle is not a valid RenderMode')

        if not isinstance(buffers, (list, tuple, set)):
            buffers = [buffers]

        if any([not isinstance(buffer, (io.StringIO, io.BytesIO)) for buffer in buffers]):
            raise MusicSheetMakerError('An invalid buffer type was passed to SongBundle')

        self.renders.update({render_mode: buffers})


    def get_renders(self, render_modes=[]):
        """
        Returns a fraction or the whole renders dictionary        
        """
        if not render_modes:
            return self.renders
        else:        
            if not isinstance(render_modes, (list, tuple, set)):
                render_modes = [render_modes]
            return { key:value for key, value in self.renders.items() if key in render_modes }

    def get_buffers(self, render_mode):
        """
        Returns the buffer list for a given RenderMode
        """
        try:
            return self.renders[render_mode]
        except KeyError:
            return []


class MusicSheetMaker:

    def __init__(self, locale='en_US', application_root=None, song_dir_in=None, song_dir_out=None, enable_skyjson_url=False):
        self.name = Resources.MUSIC_MAKER_NAME
        self.locale = self.set_locale(locale)
        self.communicator = Communicator(owner=self, locale=self.locale)
        self.song = None
        self.song_parser = None
        self.application_root = application_root if application_root is not None else os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
        self.song_dir_in = song_dir_in if song_dir_in is not None else os.path.join(self.application_root, 'test_songs')
        self.song_dir_out = song_dir_out if song_dir_out is not None else os.path.join(self.application_root, 'songs_out')
        self.css_mode = CSSMode.EMBED
        self.render_modes_enabled = [mode for mode in RenderMode]
        # self.render_modes_disabled = [RenderMode.JIANPUASCII, RenderMode.DOREMIASCII]
        self.render_modes_disabled = []
        self.render_modes_enabled = [mode for mode in self.render_modes_enabled if
                                     mode not in self.render_modes_disabled]
        self.music_cog_render_modes = [RenderMode.PNG, RenderMode.SKYJSON]
        self.enable_skyjson_url = enable_skyjson_url

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

    def shortest_path(self, path):
        
        relpath = os.path.relpath(path,start=self.application_root)
        abs_path = os.path.abspath(path)
        home_relpath = os.path.relpath(path,start=os.path.expanduser("~"))
        
        return sorted([relpath,abs_path,home_relpath],key=len)[0]

    def get_locale(self):
        return self.locale

    def set_locale(self, locale):

        self.locale = Lang.check_locale(locale)
        if self.locale is None:
            self.locale = Lang.guess_locale()
            print(f"**WARNING: bad locale type {locale} passed to MusicSheetMaker. Reverting to {self.locale}")

        return self.locale

    def is_music_cog(self, recipient):
        try:
            is_cog = recipient.get_name() == Resources.MUSIC_COG_NAME
        except AttributeError:
            try:  # Guesses harder
                recipient.bot
                is_cog = True
            except AttributeError:
                is_cog = False
        return is_cog

    def is_sky_music_website(self, recipient):
        try:
            is_website = recipient.get_name() == Resources.SKY_MUSIC_WEBSITE_NAME
        except AttributeError:
            try:  # Guesses harder
                recipient.session_ID
                is_website = True
            except:
                is_website = False

        return is_website

    def is_command_line(self, recipient):
        try:
            return recipient.get_name() == Resources.COMMAND_LINE_NAME
        except AttributeError:  # Guesses harder
            return not (self.is_music_cog(recipient) or self.is_sky_music_website(recipient))

    def get_song(self):
        return self.song

    def set_song(self, song):
        self.song = song

    def get_song_parser(self):
        return self.song_parser

    def set_song_parser(self, song_parser=None, recipient=None):
        if self.is_command_line(recipient):
            silent_warnings = False
        else:
            silent_warnings = True
        if song_parser is None:
            song_parser = SongParser(maker=self, silent_warnings=silent_warnings)
        self.song_parser = song_parser

    def get_render_modes_enabled(self):

        return self.render_modes_enabled

    def execute_queries(self, queries=None):

        if queries is None:
            self.communicator.memory.clean()
            queries = self.communicator.memory.recall_unsatisfied(filters='to_me')
        else:
            if not isinstance(queries, (list, set)):
                queries = [queries]
        """
        The query statisfaction loop:
        runs until all queries are satisfied
        """
        reply_valid = False
        while not reply_valid:
            reply_valid = True  # To break the loop if no query
            for q in queries:
                # Fetching the stock Query name and arguments
                query_name = q.get_name()
                try:
                    stock_query = self.communicator.get_stock_query(query_name)
                    handler_args = ', '.join(('sender=q.get_sender()', 'query=q'))
                    expression = f"self.{stock_query['handler']}({handler_args})"
                except KeyError as err:
                    # TODO: handle non-stock queries???
                    raise MusicSheetMakerError(f"Cannot create stock query '{query_name}', because of {repr(err)}")
                    pass
                # Actual evaluation of the stock query
                try:
                    answer = eval(expression)
                    q.reply_to(answer)
                    reply_valid = q.get_reply_validity()

                except QueriesExecutionAbort as qExecAbort:
                    raise qExecAbort


    def create_song(self, **kwargs):
        """
        A very linear, sequential way of building a song from user inputs
        Returns a list of tuples (buffers, types) where buffers is a list of IOString/IOBytes buffers, and types the list of their types
        """
        try:
            recipient = kwargs['sender']
        except KeyError:
            raise MusicSheetMakerError('No recipient specified for the Song')

        # Actually the following is not used but it may be useful to have the triggering query as an argument
        try:
            kwargs['query']
        except KeyError:
            raise MusicSheetMakerError('No Query passed to create_song')

        # ======= NEW SONG =======

        # 0. Set Song Parser # Must be done first!
        self.set_song_parser(recipient=recipient)

        # 1. Display instructions
        (i_instr, res) = self.ask_instructions(recipient=recipient)

        # 2. Asks instrument type
        (q_instr_type, instrument_type) = self.ask_instrument(recipient=recipient)

        # 2b. Sets instrument type
        self.get_song_parser().set_instrument_type(instrument_type)

        # 3. Ask for notes
        (q_notes, notes) = self.ask_notes_or_file(recipient=recipient, prerequisites=[i_instr])

        # 4. Ask for input mode (or display the one found)
        (q_mode, input_mode) = self.ask_input_mode(recipient=recipient, notes=notes, prerequisites=[q_notes])
        #(q_mode, input_mode) = self.ask_input_mode(recipient=recipient, prerequisites=[q_notes]) # EXPERIMENTAL
        
        # 4.b Set input mode
        self.set_parser_input_mode(recipient, input_mode=input_mode)
        #self.set_parser_input_mode(recipient) # EXPERIMENTAL

        # 5. Ask for song key (or display the only one possible)
        (q_key, song_key) = self.ask_song_key(recipient=recipient, notes=notes, input_mode=input_mode, prerequisites=[q_notes, q_mode])
        #(q_key, song_key) = self.ask_song_key(recipient=recipient, prerequisites=[q_notes, q_mode]) # EXPERIMENTAL

        # 6. Asks for octave shift
        (q_shift, octave_shift) = self.ask_octave_shift(recipient=recipient, input_mode=input_mode)

        # 7. Parses song
        self.parse_song(recipient, notes=notes, song_key=song_key, octave_shift=octave_shift)
        #self.parse_song(recipient) # EXPERIMENTAL
        
        # 8. Displays error ratio
        (i_error, res) = self.display_error_ratio(recipient=recipient, prerequisites=[q_notes, q_mode, q_shift])
        
        # 9. Asks for render modes
        (q_render, render_modes) = self.ask_render_modes(recipient=recipient)

        # 10. Asks for aspect ratio
        (q_aspect, aspect_ratio) = self.ask_aspect_ratio(recipient=recipient, render_modes=render_modes, prerequisites=[q_render])
        #(q_aspect, aspect_ratio) = self.ask_aspect_ratio(recipient=recipient, prerequisites=[q_render])  # EXPERIMENTAL

        # 11. Ask beats per minutes
        (q_song_bpm, song_bpm) = self.ask_song_bpm(recipient=recipient, render_modes=render_modes, prerequisites=[q_render])
        #(q_song_bpm, song_bpm) = self.ask_song_bpm(recipient=recipient, prerequisites=[q_render])  # EXPERIMENTAL       

        # 12. Asks for song metadata
        if self.get_song().get_meta_changed():
            (q_keep_meta, keep_meta) = self.ask_song_keep_metadata(recipient=recipient, prerequisites=[q_notes])
        else:
            keep_meta = False
                
        if not keep_meta:
            (qs_meta, (title, artist, transcript)) = self.ask_song_metadata(recipient=recipient)
            self.set_song_metadata(recipient=recipient, meta=(title, artist, transcript), song_key=song_key)
            #self.set_song_metadata(recipient=recipient) # EXPERIMENTAL

        # 13. Renders Song
        song_bundle = self.render_song(recipient=recipient, render_modes=render_modes, aspect_ratio=aspect_ratio, song_bpm=song_bpm)
        
        # 14. Sends an url from sky-music.herokuapp.com
        if self.enable_skyjson_url:
            self.send_json_url(recipient=recipient, song_bundle=song_bundle)

        # 15. Advertises for the Discord version
        if self.is_command_line(recipient):
            q_discord = self.communicator.send_stock_query('discord_ad', recipient=recipient)
            recipient.execute_queries(q_discord)

        
        # 16. Sends result back (required for website)
        return song_bundle



    def ask_instrument(self, recipient, prerequisites=None, execute=True):

        q_instrument = self.communicator.send_stock_query('instrument_type', recipient=recipient, prerequisites=prerequisites)

        if execute:
            recipient.execute_queries(q_instrument)
            instrument_name = q_instrument.get_reply().get_result()
            return q_instrument, instrument_name
        else:
            return q_instrument, None
        

    def ask_instructions(self, recipient, prerequisites=None, execute=True):

        replacements = {'input_modes':'\n'.join(['\n* ' + input_mode.get_long_desc(self.locale) for input_mode in InputMode]),
                        'icon_delimiter': self.get_song_parser().get_icon_delimiter().replace('\s','<space>'),
                        'pause': self.get_song_parser().get_pause().replace('\s','<space>'),
                        'quaver_delimiter': self.get_song_parser().get_quaver_delimiter().replace('\s','<space>'),
                        'quaver_example': self.get_song_parser().get_quaver_delimiter().replace('\s','<space>').join(['A1', 'B1', 'C1']),
                        'jianpu_quaver_delimiter': Resources.JIANPU_QUAVER_DELIMITER,
                        'repeat_indicator': self.get_song_parser().get_repeat_indicator() + '2'
                        }
        if self.is_command_line(recipient):
            i_instr = self.communicator.send_stock_query('instructions_command_line', recipient=recipient,
                                                         replacements=replacements, prerequisites=prerequisites)
        elif self.is_sky_music_website(recipient):
            i_instr = self.communicator.send_stock_query('instructions_sky_music_website', recipient=recipient,
                                                         replacements=replacements, prerequisites=prerequisites)
        else:
            i_instr = self.communicator.send_stock_query('instructions_music_cog', recipient=recipient,
                                                         replacements=replacements, prerequisites=prerequisites)
        if execute:
            recipient.execute_queries(i_instr)
            ok = i_instr.get_reply().get_result()
            return i_instr, ok
        else:
            return i_instr, None


    def ask_notes(self, recipient, prerequisites=None, execute=True):

        replacements = {'input_modes':'\n'.join(['\n* ' + input_mode.get_long_desc(self.locale) for input_mode in InputMode]),
                        'icon_delimiter': self.get_song_parser().get_icon_delimiter().replace('\s','<space>'),
                        'pause': self.get_song_parser().get_pause().replace('\s','<space>'),
                        'quaver_delimiter': self.get_song_parser().get_quaver_delimiter().replace('\s','<space>'),
                        'quaver_example': self.get_song_parser().get_quaver_delimiter().replace('\s','<space>').join(['A1', 'B1', 'C1']),
                        'jianpu_quaver_delimiter': Resources.JIANPU_QUAVER_DELIMITER,
                        'repeat_indicator': self.get_song_parser().get_repeat_indicator() + '2'
                        }
        replacements.update({'skip': Lang.get_string(f"recipient_specifics/skip/{recipient.get_name()}", self.locale)})
        
        q_notes = self.communicator.send_stock_query('notes', recipient=recipient, replacements=replacements, prerequisites=prerequisites)

        if execute:
            recipient.execute_queries(q_notes)
            notes = q_notes.get_reply().get_result()
            return q_notes, notes
        else:
            return q_notes, None

    def ask_file(self, recipient, prerequisites=None, execute=True):

        q_file = self.communicator.send_stock_query('file', recipient=recipient,
                                                    replacements={'songs_in': self.shortest_path(self.song_dir_in)},
                                                    prerequisites=prerequisites,
                                                    limits=(os.path.normpath(self.song_dir_in)))

        if execute:
            recipient.execute_queries(q_file)
            file_name = q_file.get_reply().get_result()
            file_path = os.path.join(self.song_dir_in, os.path.normpath(file_name))
            return q_file, file_path  # should return file name
        else:
            return q_file, None

    def read_file(self, file_path):

        isfile = os.path.isfile(file_path)

        if not isfile:
            MusicSheetMakerError("File does not exist: %s" % os.path.abspath(file_path))
        else:
            # load file
            try:
                with open(file_path, mode='r', encoding='utf-8', errors='ignore') as fp:
                    lines = fp.readlines()  # Returns a list of strings
            except (OSError, IOError) as err:
                raise err

            return lines

    def ask_notes_or_file(self, recipient, prerequisites=None, execute=True):
        """
        Asks for notes (all recipients) or a file name (command-line only)
        If a file name is detected but the file does not exist, sends a query to ask for a valid file path
        If notes are detected, return the notes as a list of strings splitted by the OS line separator
        """

        replacements = {'input_modes':'\n'.join(['\n* ' + input_mode.get_long_desc(self.locale) for input_mode in InputMode]),
                        'icon_delimiter': self.get_song_parser().get_icon_delimiter().replace('\s','<space>'),
                        'pause': self.get_song_parser().get_pause().replace('\s','<space>'),
                        'quaver_delimiter': self.get_song_parser().get_quaver_delimiter().replace('\s','<space>'),
                        'quaver_example': self.get_song_parser().get_quaver_delimiter().replace('\s','<space>').join(['A1', 'B1', 'C1']),
                        'jianpu_quaver_delimiter': Resources.JIANPU_QUAVER_DELIMITER,
                        'repeat_indicator': self.get_song_parser().get_repeat_indicator() + '2'
                        }

        if not self.is_command_line(recipient):

            return self.ask_notes(recipient=recipient, prerequisites=prerequisites, execute=execute)

        else:

            replacements.update({'songs_in': self.shortest_path(self.song_dir_in)})
            q_notes = self.communicator.send_stock_query('notes_file', recipient=recipient, replacements=replacements, prerequisites=prerequisites)

            if not execute:
                return q_notes, None
            else:
                recipient.execute_queries(q_notes)

                result = q_notes.get_reply().get_result()

                if self.is_command_line(recipient):
                    # Detects if the result is a file path
                    file_path = os.path.join(self.song_dir_in, os.path.normpath(result))
                    isfile = os.path.isfile(file_path)

                    if not isfile:
                        splitted = os.path.splitext(result)
                        if len(splitted[0]) > 0 and 2 < len(splitted[1]) <= 5 and re.search('\\.', splitted[0]) is None:
                            # then certainly a file name
                            self.communicator.memory.erase(q_notes)

                            q_notes, file_path = self.ask_file(recipient=recipient, prerequisites=prerequisites,
                                                               execute=execute)
                            isfile = True  # ask_file only returns when a valid file path is found
                else:
                    isfile = False  # Don't allow reading files on the website or music-cog

                if isfile and self.is_command_line(recipient):
                    notes = self.read_file(file_path)
                    print(Lang.get_string("open_file", self.locale).format(file_path=os.path.abspath(file_path)))
                else:
                    notes = result.split(os.linesep)  # Returns a list of strings in any case

                    if self.is_command_line(recipient):  # Loop to ask for several lines in the standard input interface
                        while result:
                            
                            (q_notes, result) = self.ask_notes(recipient=recipient, prerequisites=prerequisites, execute=execute)
                            
                            result = result.split(os.linesep)
                            for result in result:
                                notes.append(result)

                return q_notes, notes


    def ask_song_keep_metadata(self, recipient, prerequisites=None, execute=True):
        
        q_keep_meta = self.communicator.send_stock_query('keep_meta', recipient=recipient, 
                                                       prerequisites=prerequisites)
        
        if execute:
            recipient.execute_queries(q_keep_meta)
            keep_meta = q_keep_meta.get_reply().get_result()
            return q_keep_meta, keep_meta
        else:
            return q_keep_meta, None


    def ask_song_metadata(self, recipient, prerequisites=None, execute=True):
                
        queries = []
        replacements = {'skip': Lang.get_string(f"recipient_specifics/skip/{recipient.get_name()}", self.locale)}
        queries += [self.communicator.send_stock_query('song_title', recipient=recipient, 
                                                       replacements=replacements,
                                                       prerequisites=prerequisites)]
        queries += [
            self.communicator.send_stock_query('original_artist', recipient=recipient, prerequisites=prerequisites)]
        queries += [
            self.communicator.send_stock_query('transcript_writer', replacements=replacements, recipient=recipient, prerequisites=prerequisites)]

        if execute:
            recipient.execute_queries(queries)
            meta_data = [q.get_reply().get_result() for q in queries]
            return queries, tuple(meta_data)
        else:
            return queries, None


    def ask_input_mode(self, recipient, notes=None, prerequisites=None, execute=True):
        """
        Try to guess the musical notation and asks the player to confirm
        """

        if notes is None:
            notes = self.retrieve_notes(recipient)

        possible_modes = self.get_song_parser().get_possible_modes(notes)

        if len(possible_modes) == 0:
            # To avoid loopholes. I am not sure this case is ever reached, because get_possible_modes should return all modes if None is found.
            all_input_modes = [mode for mode in InputMode]

            q_mode = self.communicator.send_stock_query('musical_notation', recipient=recipient,
                                                        limits=all_input_modes, prerequisites=prerequisites)

        elif len(possible_modes) == 1:
            q_mode = self.communicator.send_stock_query('one_input_mode', recipient=recipient,
                                                        replacements={'input_mode': possible_modes[0].get_short_desc(self.locale)},
                                                        prerequisites=prerequisites)

        else:
            q_mode = self.communicator.send_stock_query('musical_notation', recipient=recipient, limits=possible_modes,
                                                        prerequisites=prerequisites)

        if len(possible_modes) == 1:
            mode = possible_modes[0]
        else:
            mode = None

        if execute:
            recipient.execute_queries(q_mode)
            if len(possible_modes) != 1:
                mode = q_mode.get_reply().get_result()
            return q_mode, mode
        else:
            return q_mode, mode


    def ask_song_key(self, recipient, notes=None, input_mode=None, prerequisites=None, execute=True):
        """
        Attempts to detect key for input written in absolute musical scales (western, Jianpu)
        """
        # EXPERIMENTAL
        if notes is None:
            notes = self.retrieve_notes(recipient)

        if input_mode is None:
            input_mode = self.retrieve_input_mode(recipient, notes)

        song_key = None
        possible_keys = self.get_song_parser().find_key(notes)
        
        try:
            default_key = self.get_song_parser().get_default_key()
        except AttributeError:
            default_key = 'C'

        if possible_keys is None:
            # Asks for any text string
            replacements={'skip': Lang.get_string(f"recipient_specifics/skip/{recipient.get_name()}", self.locale), 'song_key': default_key}
            q_key = self.communicator.send_stock_query('recommended_key', recipient=recipient,
            replacements=replacements, prerequisites=prerequisites)

        elif len(possible_keys) == 0:
            # Sends information that there is no possible key
            q_key = self.communicator.send_stock_query('no_possible_key', recipient=recipient,
            replacements={'song_key': default_key}, prerequisites=prerequisites)
            possible_keys = [default_key]

        elif len(possible_keys) == 1:
            # Sends information that there is only 1 possible key
            q_key = self.communicator.send_stock_query('one_possible_key', recipient=recipient,
                                                       replacements={'song_key': str(possible_keys[0])},
                                                       prerequisites=prerequisites)
        else:
            # Asks to choose a key within a list
            q_key = self.communicator.send_stock_query('possible_keys', recipient=recipient,
                                                       replacements={'song_key': ', '.join(possible_keys)}, limits=possible_keys,
                                                       prerequisites=prerequisites)

        if execute:

            recipient.execute_queries(q_key)
            if possible_keys is None:
                song_key = q_key.get_reply().get_result()
                if len(song_key.strip()) == 0:
                    song_key = default_key
            elif len(possible_keys) == 1:
                song_key = possible_keys[0]
            elif len(possible_keys) > 1:
                song_key = q_key.get_reply().get_result()
            else:
                raise MusicSheetMakerError("Possible keys is an empty list.")

            return q_key, song_key

        else:  # Not execute

            if possible_keys is None:
                song_key = None
            elif len(possible_keys) == 1:
                song_key = possible_keys[0]
            else:
                song_key = None

            return q_key, song_key


    def ask_octave_shift(self, recipient, input_mode=None, prerequisites=None, execute=True):
                
        if input_mode is None:
            input_mode = self.retrieve_input_mode(recipient)        
        
        if not input_mode.get_is_chromatic():
            return None, 0
        else:
        
            replacements = {'skip_number': Lang.get_string(f"recipient_specifics/skip_number/{recipient.get_name()}", self.locale)}
            q_shift = self.communicator.send_stock_query('octave_shift', recipient=recipient,
                                                         replacements=replacements,
                                                         prerequisites=prerequisites)
    
            if execute:
                recipient.execute_queries(q_shift)
                octave_shift = q_shift.get_reply().get_result()
                return q_shift, octave_shift
            else:
                return q_shift, None


    def display_error_ratio(self, recipient, prerequisites=None, execute=True):

        error_ratio = self.get_song().get_num_broken() / max(1, self.get_song().get_num_instruments())

        if error_ratio == 0:
            i_error = None
        elif error_ratio < 0.05:
            i_error = self.communicator.send_stock_query('few_errors', recipient=recipient, prerequisites=prerequisites)
        else:
            i_error = self.communicator.send_stock_query('many_errors', recipient=recipient,
                                                         prerequisites=prerequisites)

        if len(self.get_song()) == 0:
            i_error = self.communicator.send_stock_query('empty_song', recipient=recipient,
                                                         prerequisites=prerequisites)

        if execute and i_error is not None:
            recipient.execute_queries(i_error)
            ok = i_error.get_reply().get_result()
            return i_error, ok
        else:
            return i_error, None

     
    def ask_aspect_ratio(self, recipient, render_modes=None, prerequisites=None, execute=True):

        if render_modes is None:
            render_modes = self.retrieve_render_modes(recipient)

        if not any([mode.get_is_image() for mode in render_modes]):
            return None, AspectRatio.WIDESCREEN
        else:
            replacements = {'skip': Lang.get_string(f"recipient_specifics/skip/{recipient.get_name()}", self.locale)}
            q_aspect = self.communicator.send_stock_query('aspect_ratio', recipient=recipient, 
                                                          replacements=replacements, prerequisites=prerequisites)
    
            if execute:
                recipient.execute_queries(q_aspect)
                aspect_ratio = q_aspect.get_reply().get_result()
                return q_aspect, aspect_ratio
            else:
                return q_aspect, None
            

    def ask_song_bpm(self, recipient, render_modes=None, prerequisites=None, execute=True):

        if render_modes is None:
            render_modes = self.retrieve_render_modes(recipient)

        #time_modes = RenderMode.get_time_modes()
        #if not any([mode in render_modes for mode in time_modes]):
        if not any([mode.get_is_time() for mode in render_modes]):   
            return None, Resources.DEFAULT_BPM
        else:
            replacements = {'skip_number': Lang.get_string(f"recipient_specifics/skip_number/{recipient.get_name()}", self.locale)}
            q_song_bpm = self.communicator.send_stock_query('song_bpm', recipient=recipient,
                                                            replacements=replacements, prerequisites=prerequisites)
    
            if execute:
                recipient.execute_queries(q_song_bpm)
                song_bpm = q_song_bpm.get_reply().get_result()
                return q_song_bpm, song_bpm
            else:
                return q_song_bpm, None

    def ask_render_modes(self, recipient, prerequisites=None, execute=True):
        """
        Asks for the desired render modes for the Song
        """
        render_modes = self.render_modes_enabled

        if len(render_modes) == 1:
            return None, render_modes

        if self.is_music_cog(recipient):

            return None, self.music_cog_render_modes

        else:

            replacements = {'all_modes': Lang.get_string(f"recipient_specifics/all_modes/{recipient.get_name()}", self.locale)}

            q_render = self.communicator.send_stock_query('render_modes', recipient=recipient, limits=render_modes,
                                                          replacements=replacements, prerequisites=prerequisites)

            if execute:
                recipient.execute_queries(q_render)
                render_modes = q_render.get_reply().get_result()
                return q_render, render_modes
            else:
                return q_render, None
    

    def set_parser_input_mode(self, recipient, notes=None, input_mode=None):

        if input_mode is None:
            if notes is None:
                notes = self.retrieve_notes(recipient)
                input_mode = self.retrieve_input_mode(recipient, notes)
            else:
                raise MusicSheetMakerError('Could not retrieve input_modes because no notes were given.')

        self.get_song_parser().set_input_mode(input_mode)

    def set_song_metadata(self, recipient, meta=None, song_key=None):

        if meta is None:
            (title, artist, transcript) = self.retrieve_song_metadata(recipient)
        else:
            (title, artist, transcript) = meta

        if song_key is None:
            song_key = self.retrieve_query_result(recipient, '_key', 'C')

        self.get_song().set_meta(title=title, artist=artist, transcript=transcript, song_key=song_key)

    def parse_song(self, recipient, notes=None, song_key=None, octave_shift=None):

        if notes is None:
            notes = self.retrieve_notes(recipient)

        if octave_shift is None:
            octave_shift = self.retrieve_query_result(recipient, 'octave_shift', 0)

        if song_key is None:
            song_key = self.retrieve_query_result(recipient, '_key', 'C')

        song = self.get_song_parser().parse_song(song_lines=notes, song_key=song_key, octave_shift=octave_shift)
        
        self.set_song(song)

        return


    def render_song(self, recipient, render_modes=None, aspect_ratio=AspectRatio.WIDESCREEN, song_bpm=Resources.DEFAULT_BPM):

        if render_modes is None:
            if self.is_music_cog(recipient):
                render_modes = self.music_cog_render_modes
            else:
                render_modes = self.render_modes_enabled
        
        if not isinstance(song_bpm, (float, int)):
            song_bpm = Resources.DEFAULT_BPM

        if not isinstance(aspect_ratio, AspectRatio):
            aspect_ratio = AspectRatio.WIDESCREEN
        
        if not self.is_command_line(recipient):
            self.css_mode = CSSMode.EMBED
                
        if self.is_command_line(recipient):
            print("=" * 40)

        if self.is_music_cog(recipient):
            theme = Resources.MUSIC_COG_THEME
        elif self.is_command_line(recipient):
            theme = Resources.COMMAND_LINE_THEME
        elif self.is_sky_music_website(recipient):
            theme = Resources.SKY_MUSIC_WEBSITE_THEME
        else:
            theme = Resources.get_default_theme()

        song_bundle = SongBundle()
        song_bundle.set_meta(self.get_song().get_meta())

        for render_mode in render_modes:
            buffers = self.get_song().render(render_mode=render_mode, aspect_ratio=aspect_ratio, song_bpm=song_bpm, css_mode=self.css_mode, theme=theme)  # A list of IOString or IOBytes buffers
            
            if buffers is not None:
                song_bundle.add_render(render_mode, buffers)
                if self.is_command_line(recipient):
                    song_title = song_bundle.get_sanitized_song_title()
                    self.send_buffers_to_files(song_title, render_mode, buffers, recipient=recipient)
                        
        return song_bundle


    def send_buffers_to_files(self, song_title, render_mode, buffers, recipient, prerequisites=None, execute=True):
        """
        Writes the content of an IOString or IOBytes buffer list to one or several files.
        Command line only
        """
        song_renderer = SongRenderer(self.locale)
        
        file_paths = song_renderer.write_buffers_to_files(song_title, render_mode, buffers, self.song_dir_out)
        
        numfiles = len(file_paths)
        
        if numfiles == 1:

            replacements = {'render_mode': render_mode.get_short_desc(self.locale),
                            'song_file': str(self.shortest_path(file_paths[0]))
                            }

            i_song_files = self.communicator.send_stock_query('one_song_file', recipient=recipient,
            replacements=replacements, prerequisites=prerequisites)

        elif numfiles > 1:

            replacements = {'render_mode': render_mode.get_short_desc(self.locale),
                            'songs_out': str(self.shortest_path(self.song_dir_out)),
                            'num_files': str(numfiles),
                            'first_file': str(os.path.split(file_paths[0])[1]),
                            'last_file': str(os.path.split(file_paths[-1])[1])
                            }
            i_song_files = self.communicator.send_stock_query('several_song_files', recipient=recipient,
            replacements=replacements, prerequisites=prerequisites)
            
        else:
            replacements = {'render_mode': render_mode.get_short_desc(self.locale)}
            i_song_files = self.communicator.send_stock_query('no_song_file', recipient=recipient,
            replacements=replacements, prerequisites=prerequisites)

        if execute:
            recipient.execute_queries(i_song_files)
            result = i_song_files.get_reply().get_result()
            return i_song_files, result
        else:
            return i_song_files, None


    def send_json_url(self, recipient, song_bundle, skyjson_api_key=None, prerequisites=None, execute=True):
        
        json_buffers = song_bundle.get_buffers(RenderMode.SKYJSON)
        
        if json_buffers:
                        
            url = skyjson_sr.SkyjsonSongRenderer(locale=self.locale).generate_url(json_buffers[0], skyjson_api_key)
            
            replacements={'url': url}
            
            if url:
                i_url = self.communicator.send_stock_query('skyjson_url', recipient=recipient,
                                                             replacements=replacements, prerequisites=prerequisites)
            else:
                i_url = None
        else:
            i_url = None
            
        
        if execute and i_url is not None:
            recipient.execute_queries(i_url)
            ok = i_url.get_reply().get_result()
            return i_url, ok
        else:
            return i_url, None
    

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
            res = self.set_song_parser(recipient=recipient)
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

    def retrieve_song_metadata(self, recipient):
        """
        Retrieves song meta data from previous answered queries.
        Should work, but not fully tested
        """
        title = self.retrieve_query_result(recipient, 'song_title', 'Untitled')
        artist = self.retrieve_query_result(recipient, 'original_artist', '')
        transcript = self.retrieve_query_result(recipient, 'transcript_writer', '')

        return title, artist, transcript


    def retrieve_notes(self, recipient):
        """
        Retrieves notes from previous answered queries.
        Should work, but not fully tested
        """
        notes = ''
        
        q_notes_file = self.communicator.recall_by_recipient(recipient, criterion="file|notes_file",
                                                             filters=["valid_reply"], sort_by="date")
        if len(q_notes_file) != 0:
            result = q_notes_file[-1].get_reply().get_result()
            file_path = os.path.join(self.song_dir_in, os.path.normpath(result))
            isfile = os.path.isfile(file_path)

            if isfile and self.is_command_line(recipient):
                notes = self.read_file(file_path)
            else:
                notes = result.split(os.linesep)
            return notes

        q_notes = self.communicator.recall_by_recipient(recipient, criterion="notes", filters=["valid_reply"],
                                                        sort_by="date")
        if len(q_notes) != 0:
            notes = q_notes[-1].get_reply().get_result().split(os.linesep)
            
        return notes

    def retrieve_input_mode(self, recipient, notes=None):
        """
        Retrieves input mode (musical notation) from previous answered queries.
        Should work, but not fully tested
        """        
        try:
            input_mode = self.get_song_parser.get_input_mode()
        except AttributeError:
            input_mode = None

        if input_mode is None:            
            input_mode = self.retrieve_query_result(recipient, ReplyType.INPUTMODE)
            
        if input_mode is None: 
            notes = self.retrieve_notes(recipient)
            input_mode = self.get_song_parser().get_possible_modes(notes)[0]

        return input_mode


    def retrieve_render_modes(self, recipient):
        """
        Retrieves render modes from previous answered queries.
        Should work, but not fully tested
        """       
        if self.is_music_cog(recipient):
            return self.music_cog_render_modes

        render_modes = self.retrieve_query_result(recipient, 'render_modes', default=self.render_modes_enabled) 
                    
        return render_modes

    
    def retrieve_query_result(self, recipient, criterion, default=None):
        """
        Retrieves reply from previously replied query
        Should work, but not fully tested
        """        
        qs = self.communicator.recall_by_recipient(recipient, criterion=criterion, filters=["valid_reply"],
                                                        sort_by="date")

        if len(qs) != 0:
            q = qs[-1]
            if q.get_expect_reply():
                reply_result = q.get_reply().get_result()
                if reply_result not in (None, '', []):
                    return reply_result
            
        return default
