import io, re
from skymusic.modes import InputMode, RenderMode, ReplyType
from skymusic.communication import QueryOpen, QueryChoice, QueryBoolean, QueryMultipleChoices, QueryMemory, Information
from skymusic import Lang, QueryStock

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
        self.query_stock = QueryStock.load(locale)

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

    def get_stock_query(self, stock_query_name):
        
        try:
            stock_query_name = stock_query_name.lower().replace(' ', '_').replace('-', '_')
            stock_query_dict = self.query_stock[stock_query_name]
            return stock_query_dict
        except KeyError:
            raise CommunicatorError(f"{stock_query_name} is not a standard query")
        

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


    def send_stock_query(self, stock_query_name, recipient, replacements=None, **kwargs):
        """
        Create and send a query from a catalog, overriding some parameters with kwargs
        """
        stock_query_dict = self.get_stock_query(stock_query_name)
        
        method_args = stock_query_dict.copy()
        method_args.pop('class')  # The class was used and is not an argument for Query
        method_args.pop('handler')  # The handler is not useful here and is not an argument for Query
        if replacements is not None:
            for k in method_args:
                try:
                    method_args[k] = method_args[k].format_map(replacements)
                except (KeyError, AttributeError):
                    pass
        method_args['name'] = stock_query_name
        method_args['sender'] = self.owner
        method_args['recipient'] = recipient
        method_args.update(kwargs)  # Merge tuples to override default parameters with optional keyword arguments
        
        # Supposes we have imported QueryChoice, QueryOpen, QueryBoolean, Information, etc
        q = stock_query_dict['class'](**method_args)  # Creates the Query
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
                # Duplicates will be remived by clean()

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

        sanitized_filename = song_bundle.get_sanitized_song_filename()
        if len(sanitized_filename) == 0:
            sanitized_filename = Lang.get_string("song_meta/untitled", self.locale)

        for render_mode, buffers in song_bundle.get_renders().items():

            if not isinstance(render_mode, RenderMode):
                raise CommunicatorError(f"Unexpected type for song_bundle key:{type(render_mode)}")
            if not isinstance(buffers, (list, tuple)):
                raise CommunicatorError(f"Unexpected type for song_bundle value:{type(buffers)}")            
            if not isinstance(buffers[0], (io.BytesIO, io.StringIO)):
                raise CommunicatorError(f"Unexpected type for song_bundle value:{type(buffers[0])}")
            
            result_dict['song_files'] += [{'file_type': render_mode.mime_type, 'base_name': sanitized_filename+'_', 'number': i,
                                'ext': render_mode.extension} for i, buffer in enumerate(buffers)]
            
            result_dict['saves'] += [{'name': sanitized_filename + '_' + str(i) + render_mode.extension, 'buffer': buffer} for i, buffer
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
                    choices_dicts = [{'number': i, 'text': limit.get_short_desc(self.locale)} for i, limit in enumerate(limits)]
                elif isinstance(limits[0], RenderMode):
                    choices_dicts = [{'number': i, 'text': limit.get_short_desc(self.locale)} for i, limit in enumerate(limits)]
                else:
                    choices_dicts = [{'number': i, 'text': str(limit).strip()} for i, limit in enumerate(limits)]
            else:
                choices_dicts = []
                
            # Answer keyword arguments dictionary
            try:
                answer_text = query.get_reply().get_answer()
            except AttributeError:
                answer_text = query.get_default_answer()
                #answer_text = ''
            
            if answer_text is None:
                answer_text = ''
            
            if query.expect_long_answer:  # FIXME: this trick is a bit ugly (not very robust)
                answer_dict = {'answer_length': 'long', 'long_text': str(answer_text), 'short_text': ''}
            else:
                answer_dict = {'answer_length': 'short', 'long_text': '', 'short_text': str(answer_text)}

            # Dictionary or dictionaries
            queries_kwargs += [{'question': question_dict, 'choices': choices_dicts, 'answer': answer_dict}]

        return queries_kwargs  # List of queries dictionaries

    def query_to_discord(self, query):
        """
        Returns a text that can be sent to a Discord utils.Question model
        """
        result = {}
        
        limits = query.get_limits()
        if query.help_required:
            question_text = '\n'.join([query.get_help_text().strip(), query.get_foreword().strip(), query.get_question().strip()])
        else:
            question_text = '\n'.join([query.get_foreword().strip(), query.get_question().strip()])
            
        result.update({'question': question_text})

        # options keyword arguments dictionary
        if isinstance(query, QueryBoolean):
            result.update({'yesnos': [{'number': i, 'text': str(limit).strip()} for i, limit in enumerate(limits)]})
        elif isinstance(query, (QueryMultipleChoices, QueryChoice)) and query.get_reply_type() is not ReplyType.NOTE:
            result.update({'options': [{'number': i, 'text': str(limit).strip()} for i, limit in enumerate(limits)]})

        result.update({'result': query.get_result()})

        return result

