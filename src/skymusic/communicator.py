import io, re
from src.skymusic.modes import InputMode, RenderMode, ReplyType
from src.skymusic.communication import QueryOpen, QueryChoice, QueryMultipleChoices, QueryMemory, Information
from src.skymusic import Lang

"""
Classes to ask and answer questions called Query and Reply between the bot and the music sheet maker
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


class QueriesExecutionAbort(Exception):
    """
    A special exception to abort execution of queries in execute_queries (and create_song)
    """

    def __init__(self, queries, explanations=None):
        if not isinstance(queries, (list, set)):
            queries = [queries]
        self.queries = queries
        self.explanations = explanations

    def __repr__(self):
        queries_str = ', '.join([str(query) for query in self.queries])
        return f"{self.__class__.__name__}, queries={queries_str}, explanations={self.explanations}"

    def __str__(self):
        return str(self.queries)

    pass


class Communicator:

    def __init__(self, owner, locale):
        self.owner = owner
        self.memory = QueryMemory(self.owner)
        self.name = self.owner.get_name()
        self.locale=self.set_locale(locale)
        # A dictionary of standard queries arguments
        # The key must be lower case without blanks, use _ instead
        # TODO: create generic (quasi-empty) stock queries, such as Information to output dome text
        self.query_stock = {
            # Queries asked by the Player / Music Cog
            'create_song': {'class': QueryOpen.__name__,
                            'handler': 'create_song',  # The name of the method that must be executed by the recipient
                            'question': 'create_song',
                            'reply_type': ReplyType.OTHER
                            },

            # Generic Query
            'information': {'class': Information.__name__,
                            'handler': 'None',
                            'question': '',
                            'reply_type': ReplyType.TEXT
                            },

            'instructions_stdout': {'class': Information.__name__,
                                    'handler': 'None',
                                    'foreword': Lang.get_string("stock_queries/instructions_stdout/foreword", self.locale),
                                    'question': Lang.get_string("stock_queries/instructions_stdout/question", self.locale),
                                    'afterword': Lang.get_string("stock_queries/instructions_stdout/afterword", self.locale),
                                    'input_tip': Lang.get_string("stock_queries/instructions_stdout/input_tip", self.locale),
                                    'help_text': Lang.get_string("stock_queries/instructions_stdout/help_text", self.locale)
                                    },

           'instructions_website': {'class': Information.__name__,
                                    'handler': 'None',
                                    'foreword': Lang.get_string("stock_queries/instructions_website/foreword", self.locale),
                                    'question': Lang.get_string("stock_queries/instructions_website/question", self.locale),
                                    'afterword': Lang.get_string("stock_queries/instructions_website/afterword", self.locale),
                                    'input_tip': Lang.get_string("stock_queries/instructions_website/input_tip", self.locale),
                                    'help_text': Lang.get_string("stock_queries/instructions_website/help_text", self.locale)
                                    },
                                        
            'instructions_botcog': {'class': Information.__name__,
                                    'handler': 'None',
                                    'foreword': Lang.get_string("stock_queries/instructions_botcog/foreword", self.locale),
                                    'question': Lang.get_string("stock_queries/instructions_botcog/question", self.locale),
                                    'afterword': Lang.get_string("stock_queries/instructions_botcog/afterword", self.locale),
                                    'input_tip': Lang.get_string("stock_queries/instructions_botcog/input_tip", self.locale),
                                    'help_text': Lang.get_string("stock_queries/instructions_botcog/help_text", self.locale)
                                    },

            'render_modes': {'class': QueryMultipleChoices.__name__,
                             'handler': 'None',
                             'foreword': Lang.get_string("stock_queries/render_modes/foreword", self.locale),
                             'question': Lang.get_string("stock_queries/render_modes/question", self.locale),
                             'afterword': Lang.get_string("stock_queries/render_modes/afterword", self.locale),
                             'input_tip': Lang.get_string("stock_queries/render_modes/input_tip", self.locale),
                             'help_text': Lang.get_string("stock_queries/render_modes/help_text", self.locale),
                             'reply_type': ReplyType.RENDERMODES,
                             'limits': []
                             },

                'aspect_ratio': {'class': QueryOpen.__name__,
                             'handler': 'None',
                             'foreword': Lang.get_string("stock_queries/aspect_ratio/foreword", self.locale),
                             'question': Lang.get_string("stock_queries/aspect_ratio/question", self.locale),
                             'afterword': Lang.get_string("stock_queries/aspect_ratio/afterword", self.locale),
                             'input_tip': Lang.get_string("stock_queries/aspect_ratio/input_tip", self.locale),
                             'help_text': Lang.get_string("stock_queries/aspect_ratio/help_text", self.locale),
                             'reply_type': ReplyType.NUMBER,
                             'limits': [0.1, 10.0]
                             },

            'song_title': {'class': QueryOpen.__name__,
                           'handler': 'None',
                           'foreword': Lang.get_string("stock_queries/song_title/foreword", self.locale),
                           'question': Lang.get_string("stock_queries/song_title/question", self.locale),
                           'afterword': Lang.get_string("stock_queries/song_title/afterword", self.locale),
                           'input_tip': Lang.get_string("stock_queries/song_title/input_tip", self.locale),
                           'help_text': Lang.get_string("stock_queries/song_title/help_text", self.locale),
                           'reply_type': ReplyType.TEXT,
                           'limits': None
                           },

            'original_artist': {'class': QueryOpen.__name__,
                                'handler': 'None',
                                'foreword': Lang.get_string("stock_queries/original_artist/foreword", self.locale),
                                'question': Lang.get_string("stock_queries/original_artist/question", self.locale),
                                'afterword': Lang.get_string("stock_queries/original_artist/afterword", self.locale),
                                'input_tip': Lang.get_string("stock_queries/original_artist/input_tip", self.locale),
                                'help_text': Lang.get_string("stock_queries/original_artist/help_text", self.locale),
                                'reply_type': ReplyType.TEXT,
                                'limits': None
                                },

            'transcript_writer': {'class': QueryOpen.__name__,
                                  'handler': 'None',
                                  'foreword': Lang.get_string("stock_queries/transcript_writer/foreword", self.locale),
                                  'question': Lang.get_string("stock_queries/transcript_writer/question", self.locale),
                                  'afterword': Lang.get_string("stock_queries/transcript_writer/afterword", self.locale),
                                  'input_tip': Lang.get_string("stock_queries/transcript_writer/input_tip", self.locale),
                                  'help_text': Lang.get_string("stock_queries/transcript_writer/help_text", self.locale),
                                  'reply_type': ReplyType.TEXT,
                                  'limits': None
                                  },

            'notes_file': {'class': QueryOpen.__name__,
                           'handler': 'None',
                           'foreword': Lang.get_string("stock_queries/notes_file/foreword", self.locale),
                           'question': Lang.get_string("stock_queries/notes_file/question", self.locale),
                           'afterword': Lang.get_string("stock_queries/notes_file/afterword", self.locale),
                           'input_tip': Lang.get_string("stock_queries/notes_file/input_tip", self.locale),
                           'help_text': Lang.get_string("stock_queries/notes_file/help_text", self.locale),
                           'reply_type': ReplyType.OTHER,
                           'limits': None
                           },

            'file': {'class': QueryOpen.__name__,
                     'handler': 'None',
                     'foreword': Lang.get_string("stock_queries/file/foreword", self.locale),
                     'question': Lang.get_string("stock_queries/file/question", self.locale),
                     'afterword': Lang.get_string("stock_queries/file/afterword", self.locale),
                     'input_tip': Lang.get_string("stock_queries/file/input_tip", self.locale),
                     'help_text': Lang.get_string("stock_queries/file/help_text", self.locale),
                     'reply_type': ReplyType.FILEPATH,
                     'limits': '.'
                     },

            'notes': {'class': QueryOpen.__name__,
                      'handler': 'None',
                      'foreword': Lang.get_string("stock_queries/notes/foreword", self.locale),
                      'question': Lang.get_string("stock_queries/notes/question", self.locale),
                      'afterword': Lang.get_string("stock_queries/notes/afterword", self.locale),
                      'input_tip': Lang.get_string("stock_queries/notes/input_tip", self.locale),
                      'help_text': Lang.get_string("stock_queries/notes/help_text", self.locale),
                      'reply_type': ReplyType.TEXT,
                      'limits': None
                      },

            'one_input_mode': {'class': Information.__name__,
                               'handler': 'None',
                               'foreword': Lang.get_string("stock_queries/one_input_mode/foreword", self.locale),
                               'question': Lang.get_string("stock_queries/one_input_mode/question", self.locale),
                               'afterword': Lang.get_string("stock_queries/one_input_mode/afterword", self.locale),
                               'input_tip': Lang.get_string("stock_queries/one_input_mode/input_tip", self.locale),
                               'help_text': Lang.get_string("stock_queries/one_input_mode/help_text", self.locale)
                            },                               
                                                       
            'musical_notation': {'class': QueryChoice.__name__,
                                 'handler': 'None',
                                 'foreword': Lang.get_string("stock_queries/musical_notation/foreword", self.locale),
                                 'question': Lang.get_string("stock_queries/musical_notation/question", self.locale),
                                 'afterword': Lang.get_string("stock_queries/musical_notation/afterword", self.locale),
                                 'input_tip': Lang.get_string("stock_queries/musical_notation/input_tip", self.locale),
                                 'help_text': Lang.get_string("stock_queries/musical_notation/help_text", self.locale),
                                 'reply_type': ReplyType.INPUTMODE,
                                 'limits': []
                                 },

            'no_possible_key': {'class': Information.__name__,
                                'handler': 'None',
                                'foreword': Lang.get_string("stock_queries/no_possible_key/foreword", self.locale),
                                'question': Lang.get_string("stock_queries/no_possible_key/question", self.locale),
                                'afterword': Lang.get_string("stock_queries/no_possible_key/afterword", self.locale),
                                'input_tip': Lang.get_string("stock_queries/no_possible_key/input_tip", self.locale),
                                'help_text': Lang.get_string("stock_queries/no_possible_key/help_text", self.locale)
                                },

            'one_possible_key': {'class': Information.__name__,
                                 'handler': 'None',
                                 'foreword': Lang.get_string("stock_queries/one_possible_key/foreword", self.locale),
                                 'question': Lang.get_string("stock_queries/one_possible_key/question", self.locale),
                                 'afterword': Lang.get_string("stock_queries/one_possible_key/afterword", self.locale),
                                 'input_tip': Lang.get_string("stock_queries/one_possible_key/input_tip", self.locale),
                                 'help_text': Lang.get_string("stock_queries/one_possible_key/help_text", self.locale)
                                 },

            'possible_keys': {'class': QueryChoice.__name__,
                              'handler': 'None',
                              'foreword': Lang.get_string("stock_queries/possible_keys/foreword", self.locale),
                              'question': Lang.get_string("stock_queries/possible_keys/question", self.locale),
                              'afterword': Lang.get_string("stock_queries/possible_keys/afterword", self.locale),
                              'input_tip': Lang.get_string("stock_queries/possible_keys/input_tip", self.locale),
                              'help_text': Lang.get_string("stock_queries/possible_keys/help_text", self.locale),
                              'reply_type': ReplyType.NOTE,
                              'limits': []
                              },

            'recommended_key': {'class': QueryOpen.__name__,
                              'handler': 'None',
                              'foreword': Lang.get_string("stock_queries/recommended_key/foreword", self.locale),
                              'question': Lang.get_string("stock_queries/recommended_key/question", self.locale),
                              'afterword': Lang.get_string("stock_queries/recommended_key/afterword", self.locale),
                              'input_tip': Lang.get_string("stock_queries/recommended_key/input_tip", self.locale),
                              'help_text': Lang.get_string("stock_queries/recommended_key/help_text", self.locale),
                              'reply_type': ReplyType.NOTE,
                              'limits': None
                              },
                            
            'octave_shift': {'class': QueryOpen.__name__,
                             'handler': 'None',
                             'foreword': Lang.get_string("stock_queries/octave_shift/foreword", self.locale),
                             'question': Lang.get_string("stock_queries/octave_shift/question", self.locale),
                             'afterword': Lang.get_string("stock_queries/octave_shift/afterword", self.locale),
                             'input_tip': Lang.get_string("stock_queries/octave_shift/input_tip", self.locale),
                             'help_text': Lang.get_string("stock_queries/octave_shift/help_text", self.locale),
                             'reply_type': ReplyType.NUMBER,
                             'limits': [-6, 6]
                             },

            'one_song_file': {'class': Information.__name__,
                              'handler': 'None',
                              'foreword': Lang.get_string("stock_queries/one_song_file/foreword", self.locale),
                              'question': Lang.get_string("stock_queries/one_song_file/question", self.locale),
                              'afterword': Lang.get_string("stock_queries/one_song_file/afterword", self.locale),
                              'input_tip': Lang.get_string("stock_queries/one_song_file/input_tip", self.locale),
                              'help_text': Lang.get_string("stock_queries/one_song_file/help_text", self.locale)
                              },

            'several_song_files': {'class': Information.__name__,
                             'handler': 'None',
                             'foreword': Lang.get_string("stock_queries/several_song_files/foreword", self.locale),
                             'question': Lang.get_string("stock_queries/several_song_files/question", self.locale),
                             'afterword': Lang.get_string("stock_queries/several_song_files/afterword", self.locale),
                             'input_tip': Lang.get_string("stock_queries/several_song_files/input_tip", self.locale),
                             'help_text': Lang.get_string("stock_queries/several_song_files/help_text", self.locale)
                             },
                             
            'no_song_file': {'class': Information.__name__,
                             'handler': 'None',
                             'foreword': Lang.get_string("stock_queries/no_song_file/foreword", self.locale),
                             'question': Lang.get_string("stock_queries/no_song_file/question", self.locale),
                             'afterword': Lang.get_string("stock_queries/no_song_file/afterword", self.locale),
                             'input_tip': Lang.get_string("stock_queries/no_song_file/input_tip", self.locale),
                             'help_text': Lang.get_string("stock_queries/no_song_file/help_text", self.locale)
                             },

            'few_errors': {'class': Information.__name__,
                             'handler': 'None',
                             'foreword': Lang.get_string("stock_queries/few_errors/foreword", self.locale),
                             'question': Lang.get_string("stock_queries/few_errors/question", self.locale),
                             'afterword': Lang.get_string("stock_queries/few_errors/afterword", self.locale),
                             'input_tip': Lang.get_string("stock_queries/few_errors/input_tip", self.locale),
                             'help_text': Lang.get_string("stock_queries/few_errors/help_text", self.locale)
                             },
                                                                                                                                           
            'many_errors': {'class': Information.__name__,
                             'handler': 'None',
                             'foreword': Lang.get_string("stock_queries/many_errors/foreword", self.locale),
                             'question': Lang.get_string("stock_queries/many_errors/question", self.locale),
                             'afterword': Lang.get_string("stock_queries/many_errors/afterword", self.locale),
                             'input_tip': Lang.get_string("stock_queries/many_errors/input_tip", self.locale),
                             'help_text': Lang.get_string("stock_queries/many_errors/help_text", self.locale)
                             },

            }

    def __str__(self):

        return f"<{self.__class__.__name__} of '{self.owner.get_name()}' with {len(self.memory)} stored queries>"

    def __getattr__(self, attr_name):
        """
        Default function to call in case no one else is found.
        """
        if 'memory' in self.__dict__.keys():
            return getattr(self.memory, attr_name)
        else:
            raise AttributeError(f"type object {repr(type(self).__name__)} has no attribute 'memory'")

    def get_name(self):
        return self.name
    
    def get_locale(self):        
        return self.locale


    def set_locale(self, locale):
        
        self.locale = Lang.check_locale(locale)
        
        if self.locale is None: 
            try:
                self.locale = Lang.check_locale(self.owner.get_locale())
            except:
                pass
            if self.locale is None: 
                self.locale = Lang.guess_locale()
                print(f"**WARNING: bad locale type {locale} passed to Communicator. Reverting to {self.locale}")
                
        return self.locale


    def send_stock_query(self, stock_query_name, recipient, foreword_rep=(), question_rep=(), afterword_rep=(),
                         helptext_rep=(), **kwargs):
        """
        Create and send a query from a catalog, overriding some parameters with kwargs
        """
        try:
            stock_query_name = stock_query_name.lower().replace(' ', '_')
            stock_query = self.query_stock[stock_query_name]
        except KeyError:
            raise CommunicatorError(f"{stock_query_name} is not a standard query")

        method_args = stock_query.copy()
        method_args.pop('class')  # The class was used and is not an argument for Query
        method_args.pop('handler')  # The handler is not useful here and is not an argument for Query
        method_args['name'] = stock_query_name
        method_args['sender'] = self.owner
        method_args['recipient'] = recipient
        method_args.update(kwargs)  # Merge tuples to override default parameters with optional keyword arguments
        if 'foreword' in method_args.keys() and len(foreword_rep) > 0:
            try:
                method_args['foreword'] = method_args['foreword'].format(*foreword_rep)
            except TypeError:
                print('\n***Warning: foreword_rep does not match pattern in foreword.\n')
        if 'question' in method_args.keys() and len(question_rep) > 0:
            try:
                method_args['question'] = method_args['question'].format(*question_rep)
            except TypeError:
                print('\n***Warning: question_rep does not match pattern in question.\n')
        if 'afterword' in method_args.keys() and len(afterword_rep) > 0:
            try:
                method_args['afterword'] = method_args['afterword'].format(*afterword_rep)
            except TypeError:
                print('\n***Warning: afterword_rep does not match pattern in afterword.\n')

        if 'help_text' in method_args.keys() and len(helptext_rep) > 0:
            try:
                method_args['help_text'] = method_args['help_text'].format(*helptext_rep)
            except TypeError:
                print('\n***Warning: help_text_rep does not match pattern in help_text.\n')

        query_object = eval(
            stock_query['class'])  # supposes we have imported QueryChoice, QueryOpen, QueryBoolean, Information, etc

        q = query_object(**method_args)  # Creates the Query
        self.memory.store(q)
        q.check_sender(allowed=self.owner)
        q.send(recipient=recipient)

        return q

    def receive(self, queries):

        if not isinstance(queries, list):
            queries = [queries]

        for q in queries:
            if q.check_recipient(allowed=self.owner):
                self.memory.store(q)
                # TODO: check for duplicates before storing?

    def query_to_stdout(self, query):
        """
        Returns a text that can be printed in the standard output
        """
        question = str(query.get_result())
        return question

    def reply_to_website_result(self, reply):

        song_bundle = reply.get_result()  # Should be a SongBundle object

        result_dict = {}
        
        result_dict.update({'song_meta': song_bundle.get_meta()})
        result_dict.update({'song_files': []})
        result_dict.update({'saves': []})

        sanitized_title = re.sub(r'[\\/:"*?<>|]', '', re.escape(song_bundle.get_meta()['title'])).strip()
        if len(sanitized_title) == 0:
            sanitized_title = 'Untitled'

        for render_mode, buffers in song_bundle.get_all_renders().items():

            if not isinstance(render_mode, RenderMode):
                raise CommunicatorError(f"Unexpected type for song_bundle key:{type(render_mode)}")
            if not isinstance(buffers, (list, tuple)):
                raise CommunicatorError(f"Unexpected type for song_bundle value:{type(buffers)}")            
            if not isinstance(buffers[0], (io.BytesIO, io.StringIO)):
                raise CommunicatorError(f"Unexpected type for song_bundle value:{type(buffers[0])}")
            
            result_dict['song_files'] += [{'file_type': render_mode.mime_type, 'base_name': sanitized_title+'_', 'number': i,
                                'ext': render_mode.extension} for i, buffer in enumerate(buffers)]
            
            result_dict['saves'] += [{'name': sanitized_title + '_' + str(i) + render_mode.extension, 'buffer': buffer} for i, buffer
                         in enumerate(buffers)]
            
        return result_dict


    def queries_to_website_questions(self, queries):
        '''
        Returns a dictionary of arguments to be used to create Question, Choices
        by the web app music_maker in sky-music-website-project
        '''
        if not isinstance(queries, (list, set)):
            queries = [queries]

        queries_kwargs = []

        for query in queries:
            limits = query.get_limits()

            # Question keyword arguments dictionary
            if isinstance(query, QueryMultipleChoices):
                multiple_choices = True
            else:
                multiple_choices = False

            question_dict = {'foreword': query.get_foreword().strip(), 'question': query.get_question().strip(),
                             'afterword': query.get_afterword().strip(),
                             'help_text': query.get_help_text().strip(), 'input_tip': query.get_input_tip().strip(),
                             'identifier': query.get_identifier(),
                             'expect_answer': query.get_expect_reply(), 'multiple_choices': multiple_choices}

            # Choices keyword arguments dictionary
            if isinstance(query, (QueryMultipleChoices, QueryChoice)):
                if isinstance(limits[0], InputMode):
                    choices_dicts = [{'number': i, 'text': str(limit)} for i, limit in enumerate(limits)]
                elif isinstance(limits[0], RenderMode):
                    choices_dicts = [{'number': i, 'text': str(limit)} for i, limit in enumerate(limits)]
                else:
                    choices_dicts = [{'number': i, 'text': str(limit).strip()} for i, limit in enumerate(limits)]
            else:
                choices_dicts = []

            # Answer keyword arguments dictionary
            try:
                answer_text = query.get_reply().get_answer()
                if answer_text is None:
                    answer_text = ''
            except AttributeError:
                answer_text = ''

            if 'notes' in query.get_name().strip().lower():  # FIXME: this trick is a bit ugly (not very robust)
                answer_dict = {'answer_length': 'long', 'long_text': str(answer_text), 'short_text': ''}
            else:
                answer_dict = {'answer_length': 'short', 'long_text': '', 'short_text': str(answer_text)}

            # Dictionary or dictionaries
            queries_kwargs += [{'question': question_dict, 'choices': choices_dicts, 'answer': answer_dict}]

        return queries_kwargs  # List of queries dictionaries

    def query_to_discord(self, query):
        """
        Returns a text that can be sent to a Discord utils.Question model
        TODO: send just a text or a dictionary of arguments?
        """
        result = {}
        
        limits = query.get_limits()
        if query.help_required:
            question_text = '\n'.join([query.get_help_text().strip(), query.get_foreword().strip(), query.get_question().strip()])
        else:
            question_text = '\n'.join([query.get_foreword().strip(), query.get_question().strip()])
            
        result.update({'question': question_text})

        # options keyword arguments dictionary
        if isinstance(query, (QueryMultipleChoices, QueryChoice)) and query.get_reply_type() is not ReplyType.NOTE:
            result.update({'options': [{'number': i, 'text': str(limit).strip()} for i, limit in enumerate(limits)]})

        result.update({'result': query.get_result()})

        return result
    

    def discord_to_query(self, utils_question):

        # TODO: This is the tricky part: how do we transform a free-text question in a precise Query?
        # => Requires interpreting strings or finding key strings within a sentence
        # This is usually done in the Cog, note here
        return
