import re, os
from modes import ReplyType, InputMode, RenderMode
from datetime import datetime
import hashlib
import io
import Lang

class QueryError(Exception):
    def __init__(self, explanation):
        self.explanation = explanation

    def __str__(self):
        return str(self.explanation)

    pass


class InvalidReplyError(QueryError):
    pass


class InvalidQueryError(QueryError):
    pass


class QueryMemoryError(QueryError):
    pass


class InvalidQueryTypeError(InvalidQueryError):
    def __init__(self, explanation, obj_in, type_expect):
        self.explanation = explanation + ': ' + str(type_expect.__name__) + ' expected, ' + str(
            type(obj_in).__name__) + ' given.'
        super().__init__(self.explanation)

    pass


class QueryRepliedError(QueryError):
    pass


class Reply:
    """
    A Reply to be attached to a Query
    """

    def __init__(self, query, answer):

        self.query = query  # the question that was asked in the first place
        self.answer = answer # The raw answer from the other party
        self.result = None # The processed answer, ready for external use
        self.is_valid = None

        if not isinstance(query, Query):
            raise InvalidReplyError('this reply does not follow any query')
            
        self.sanitize_answer()

    def __repr__(self):
        try:
            sender_name = str(self.query.get_sender().get_name())
            recipient_name = str(self.query.get_recipient().get_name())
        except AttributeError:
            sender_name = str(self.query.get_sender())
            recipient_name = str(self.query.get_recipient())
            
        string = '<' + self.__class__.__name__ + ' from ' + sender_name + ' to ' + recipient_name + ': '
        if isinstance(self.get_result(), str):
            string += repr(self.get_result())
        else:
            string += str(self.get_result())
        string += ', valid=' + str(self.get_validity())
        string += '>'

        return string

    def get_answer(self):
        return self.answer

    def sanitize_answer(self):
        
        answer = self.answer
        if isinstance(answer, str):
            answer = answer.strip()
        if self.query.get_reply_type() == ReplyType.INTEGER:
            if answer == '':
                answer = '0'
        
        self.answer = answer

    def get_validity(self):
        if self.is_valid is not True:
            self.is_valid = self.query.check_reply()
        return self.is_valid

    def build_result(self):
        """
        Builds the result of the Reply, useful to music-maker,
        from self.answer, the raw input from the user
        """
        if not self.get_validity():
            self.result = None
            return self.result

        if isinstance(self.query, QueryBoolean):
            self.result = (self.query.get_answer_index() % 2 == 0)
        elif isinstance(self.query, QueryMultipleChoices):
            indices = self.query.get_answer_indices() #Must be checked before QueryChoice because it is a subclass
            self.result = [self.query.get_limits()[index] for index in indices]
        elif isinstance(self.query, QueryChoice):
            index = self.query.get_answer_index() #QueryChoices always have limits
            self.result = self.query.get_limits()[index]
        else:#QueryOpen
            self.result = self.answer
            if self.query.reply_type == ReplyType.INTEGER:
                self.result = int(self.answer)

        return self.result

    def get_result(self):
        if self.result is None:
            self.build_result()
        return self.result


class Query:

    def __init__(self, name=None, sender=None, recipient=None, question=None, foreword=None, afterword=None, help_text=None, input_tip=None, reply_type=ReplyType.OTHER, limits=None, prerequisites=None):
        """
        The general Query class

        QueryChoice is for questions where the user chooses 1 item from multiple choices
        QueryMultipleChoice is for questions where the user chooses several items from multiple choices
        QueryBoolean means choosing between 2 choices
        QueryOpen is for an open-ended query
        """
        if name is None:
            name = question
        self.name = name
        self.sender = sender
        self.recipient = recipient
        self.question = question #The core question
        self.foreword = foreword
        self.afterword = afterword
        self.help_text = help_text
        self.input_tip = input_tip
        self.reply_type = reply_type  # Expected type of the reply, among ReplyType
        #Repairing limits:
        if not isinstance(limits, (list,tuple,set,type(None))):
            self.limits = [limits]
        else:
            self.limits = limits # Choices, regexp...
        #Repairing prerequisites:
        if not isinstance(prerequisites, (list,set,type(None))):
            self.prerequisites = [prerequisites]
        else:
            self.prerequisites = prerequisites # Other Queries required to reply to this Query
        self.identifier = None# An almost-unique ID based on the Query content, excluding the timestamp
        self.sent_time = None  # The timestamp at which the Query was sent()
        self.expect_reply = True # Currently used for Information queries

        self.valid_locutors_names = ['music-cog', 'music-sheet-maker', 'command-line', 'sky-music-website']  # A list of valid locutors for security purposes

        self.reply = None  # Reply object
        self.result = None  # The full question with foreword and afterword
        self.is_sent = False  # The send() command has been called
        self.is_replied = False  # Has been assigned a Reply object
        self.help_required = False

        self.check_and_pack() # Checks the input parameters and build the result
        
    def __repr__(self):
        try:
            sender_name = self.sender.get_name()
        except AttributeError:
            sender_name = None
        try:
            recipient_name = self.recipient.get_name()
        except AttributeError:
            recipient_name = None
        string = '<' + self.__class__.__name__ + ' ' + str(self.get_identifier()) + ' from ' + str(sender_name) + ' to ' + str(recipient_name) + ': ' + repr(self.question)[:20] + '..., ' + str(self.reply_type) + ' expected'
        
        try:
            limits = self.get_limits()
            limits[0]
            string += ', within ' + str(limits)
        except (TypeError, IndexError):
            pass
        string += ', answer='
        is_valid = self.get_reply_validity()
        if is_valid is True:
            string += 'valid'
        elif is_valid is None:
            string += 'None'
        else:
            string += 'invalid'
        string += '>'

        return string

    def get_name(self):
        return self.name

    def get_sender(self):
        return self.sender

    def get_recipient(self):
        return self.recipient

    def get_sender_locale(self):
        
        try:
            return self.get_sender().get_locale()
        except AttributeError:
            pass

    def get_recipient_locale(self):
        
        try:
            return self.get_sender().get_locale()
        except AttributeError:
            pass

    def get_question(self):
        if self.question is None:
            return ''
        else:
            return self.question

    def get_result(self):
        return self.result

    def get_reply(self):
        return self.reply #Returns the latest reply

    def get_foreword(self):
        if self.foreword is None:
            return ''
        else:
            return self.foreword

    def get_afterword(self):
        if self.afterword is None:
            return ''
        else:
            return self.afterword

    def get_help_text(self):
        if self.help_text is None:
            return ''
        else:
            return self.help_text

    def get_input_tip(self):
        if self.input_tip is None:
            return ''
        else:
            return self.input_tip

    def get_reply_type(self):
        return self.reply_type

    def get_expect_reply(self):
        return self.expect_reply

    def get_limits(self):
        """
        Returns None or a list with len>0
        """
        if self.limits is None:
            #return None
            return [] #another possibility
        else:
            try:
                self.limits[0]
                return self.limits
            except IndexError:
                return None
            except TypeError:
                return [self.limits]

    def get_is_replied(self):
        return self.is_replied

    def get_reply_validity(self):
        try:
            return self.reply.get_validity()
        except AttributeError:
            return None

    def get_is_sent(self):
        return self.is_sent

    def get_identifier(self):
        return self.identifier

    def get_sent_time(self):
        return self.sent_time

    def get_prerequisites(self):
        """
        Returns None or a list with len>0
        """
        if self.prerequisites is None:
            #return None
            return [] #another possibility
        else:
            try:
                self.prerequisites[0]
                return self.prerequisites
            except IndexError:
                return []
            except TypeError:
                return [self.prerequisites]
    
    def get_locutor_name(self, locutor):
        '''
        Try really hard to find a name for the locutor
        '''
        if isinstance(locutor, str):
            locutor_name = locutor
        else:
            try:
                locutor_name = locutor.get_name().lower().strip()
            except AttributeError:
                try:
                    locutor_name = locutor.__name__.lower().strip()
                except AttributeError:
                    locutor_name = type(locutor).__name__.lower().strip()
        return locutor_name.lower().strip()    
    
    
    def check_locutor(self, locutor, allowed='all', forbidden=None):

        def get_list_and_sanitize(obj):
            if not isinstance(obj, (list, tuple)):
                objects = [obj]
            if isinstance(objects[0], str):
                objects = [obj.lower().strip() for obj in objects]
            return objects

        locutor_ok = True

        if locutor is None:
            locutor_ok = False
            return locutor_ok
            # raise InvalidQueryError('invalid locutor for ID=' + str(self.get_identifier()) + ': ' + str(locutor))

        if len(self.valid_locutors_names) != 0:
            # Try to retrieve the locutor name

            locutor_name = self.get_locutor_name(locutor)

            if locutor_name not in self.valid_locutors_names:
                locutor_ok = False
                print('locutor is not in internal validation list')

        if allowed != 'all':
            allowed = get_list_and_sanitize(allowed)
            if (locutor not in allowed) and (locutor_name not in allowed):
                locutor_ok = False
                raise InvalidQueryError('locutor not allowed for Query ID=' + str(self.get_identifier()) + \
                                        ': ' + repr(str(locutor)) + '. It must be among ' + str(allowed))

        if forbidden is not None:
            forbidden = get_list_and_sanitize(forbidden)
            if (locutor in forbidden) or locutor_name in forbidden:
                locutor_ok = False
                raise InvalidQueryError('locutor forbidden for Query ID=' + str(self.get_identifier()) + \
                                        ': ' + repr(str(locutor)) + '. It must not be among ' + str(forbidden))

        return locutor_ok

    def check_sender(self, allowed='all', forbidden=None):

        sender_ok = self.check_locutor(self.sender, allowed, forbidden)

        if not sender_ok:
            raise InvalidQueryError('invalid sender for Query ID=' + str(self.get_identifier()) + \
                                    ': ' + repr(str(self.sender)) + '. It must be among ' + str(
                self.valid_locutors_names))

        return sender_ok

    def check_recipient(self, allowed='all', forbidden=None):

        recipient_ok = self.check_locutor(self.recipient, allowed, forbidden)

        if not recipient_ok:
            raise InvalidQueryError('invalid recipient for Query ID=' + str(self.get_identifier()) + \
                                    ': ' + repr(str(self.sender)) + '. It must be among ' + str(
                self.valid_locutors_names))

        if self.recipient == self.sender:
            raise InvalidQueryError('sender cannot ask a question to itself')

        return recipient_ok

    def check_question(self):
        
        # TODO: add checking among more types, if needed
        if isinstance(self.get_question(), str):
            return True
        else:
            raise InvalidQueryError('only string (str) questions are allowed at the moment')

        return False

    def check_limits(self):

        limits = self.get_limits()
        if limits is None:
            return True
        else:
            try:
                if len(limits) == 0:
                    return True
            except TypeError:
                pass
            
        #From now on limits is an non empty list or a non-None object
        if self.reply_type in [ReplyType.TEXT, ReplyType.NOTE, ReplyType.FILEPATH] and not isinstance(limits[0], str):
            raise InvalidQueryTypeError('incorrect limits type', limits[0], str)

        if self.reply_type == ReplyType.INTEGER:
            try:
                int(limits[0])
            except:
                raise InvalidQueryTypeError('incorrect limits type', limits[0], int)

        if self.reply_type == ReplyType.INPUTMODE and not isinstance(limits[0], InputMode):
            raise InvalidQueryTypeError('incorrect limits type', limits[0], InputMode)

        if self.reply_type == ReplyType.RENDERMODES and not isinstance(limits[0], RenderMode):
            raise InvalidQueryTypeError('incorrect limits type', limits[0], RenderMode)

        if self.reply_type == ReplyType.FILEPATH:
            if os.path.isdir(limits[0]):
                pass
            elif len(limits[0]) >= 2 and len(limits[0]) <= 5:
                #limits is an extension
                pass
            else: #Limits is neither an extension or a directory
                InvalidQueryError('limit is neither a directory or an extension')

        if any([type(limit) != type(limits[0]) for limit in limits]):
            raise InvalidQueryError('limits are not all of the same type')

        # Smart guess of some common types
        if self.reply_type is None:
            if isinstance(limits[0], str):
                try:
                    int(limits[0])
                    self.reply_type = ReplyType.INTEGER
                except:
                    self.reply_type == ReplyType.TEXT
            elif isinstance(limits[0], InputMode):
                self.reply_type = ReplyType.INPUTMODE
            elif isinstance(limits[0], RenderMode):
                self.reply_type = ReplyType.RENDERMODES
            else:
                self.reply_type = ReplyType.OTHER
           
        return True     
                
                
    def check_reply(self):
         
        if self.help_required:
            return False        
        
        if not isinstance(self.reply, Reply):
            
            self.is_replied = False
            return None

        else:
 
            self.is_replied = True
            is_reply_valid = False
            answers = self.reply.get_answer() #answer exists because reply is a Reply object
            limits = self.get_limits()
                        
            if answers is None:
                return False
            else:
                               
                if not self.expect_reply: # An answer is expected, whatever it is
                    return True
                
                if not isinstance(answers, list):
                    answers = [answers]
  
                if any([type(answer) != type(answers[0]) for answer in answers]):
                    return False
                                
                if self.reply_type in [ReplyType.TEXT, ReplyType.NOTE, ReplyType.FILEPATH]:
                    if isinstance(answers[0], str):
                        is_reply_valid = True
                elif self.reply_type == ReplyType.INTEGER:
                    try:
                        int(answers[0])
                        is_reply_valid = True
                    except:
                        is_reply_valid = False
                elif self.reply_type == ReplyType.INPUTMODE:
                    if isinstance(answers[0], InputMode) or isinstance(answers[0], (str,int)):
                        is_reply_valid = True #An input mode can be chosen using its order number in a list or its string description
                elif self.reply_type == ReplyType.RENDERMODES:
                    if isinstance(answers[0], RenderMode) or isinstance(answers[0], (str,int)):
                        is_reply_valid = True #A render mode can be chosen using its order number in a list or its string description
                elif self.reply_type == ReplyType.BUFFERS:

                    try:
                        buffers, render_modes = answers[0]
                    except (TypeError, ValueError):
                        is_reply_valid = False
                    else:
                        if isinstance(buffers[0],(io.BytesIO, io.StringIO)) and isinstance(render_modes[0], RenderMode):
                            is_reply_valid = True
                        else:
                            is_reply_valid = False

                else:
                    is_reply_valid = True

                if self.reply_type == ReplyType.FILEPATH and limits is not None:
                    '''
                    Checks if the file exist in the directories and with the extensions specified in limits
                    '''
                    directories = [lim for lim in limits if os.path.isdir(lim)]
                    extensions = [lim for lim in limits if not os.path.isdir(lim) and len(lim) >= 2 and len(lim) <= 5]
                    extensions = ['.'+ext.split('.')[-1] for ext in extensions]
                    
                    directories += ['.']


                    if all([not os.path.isfile(os.path.normpath(os.path.join(directory, answers[0]))) for directory in directories]) and len(directories) != 0:

                        is_reply_valid = False
                                        
                    if all([re.search(ext,os.path.splitext(answers[0])[-1]) is None for ext in extensions]) and len(extensions) != 0:

                        is_reply_valid = False
                
                #Maybe limits is an integer range
                if self.reply_type == ReplyType.INTEGER and limits is not None and is_reply_valid is True:
                    try:
                        num = int(answers[0])
                        low_lim = min(limits)
                        high_lim = max(limits)
                        if low_lim <= num <= high_lim:
                            is_reply_valid = True
                        else:
                            is_reply_valid = False
                    except (ValueError, TypeError):
                        pass

        return is_reply_valid
    

    def check_prerequisites(self):
        """
        Checks that all prerequisites Queries have been satisfied, i.e. received a valid Reply
        """
        pre = self.get_prerequisites()
        if pre is None:
            satisfied = True
        elif len(pre) == 0:
            satisfied = True
        else:
            satisfied = all([q.get_reply_validity() for q in pre])

        return satisfied
    

    def build_result(self):
        """
        The result is the complete query, with foreword, afterword, et caetera
        This a generic return, that is  overridden in derived classes
        """
        result = []
        if self.help_required:
            result += [self.get_help_text()+'\n']
        result += [self.get_foreword()]
        result += [self.get_question()]
        result += [self.get_afterword()]
 
        try:
            result = '\n'.join(filter(None, result))
        except:
            pass
        self.result = result
        return result
    

    def hash_identifier(self):
        """
        Builds an ID of the Query. Two queries with the same ID are considered as duplicates.
        """
        
        sender_name = self.get_locutor_name(self.get_sender())
        recipient_name = self.get_locutor_name(self.get_recipient())
        
        hashables = [sender_name, recipient_name, self.get_foreword(), self.get_question(), self.get_afterword(), 
        self.get_limits(), self.get_prerequisites()]
        hashables = [str(hashable).lower().strip() for hashable in hashables]
        #self.identifier = hash(','.join(hashables)) #Python built-in has method, changes at each python sessions
        m = hashlib.md5()
        for hashable in hashables:
            m.update(hashable.encode())
        self.identifier = m.hexdigest()
        #hashlib md5, session-persistent hasho

        return self.identifier
    

    def check_and_pack(self):
        """
        Checks the fundamental properties normally passed as inputs, builds the complete question (.result) and creates an ID
        """
        self.check_sender()
        self.check_recipient()
        self.check_question()
        self.check_limits()
        self.build_result()
        self.hash_identifier()
        

    def stamp(self):
        """
        Assigns a sent timestamp to the Query
        """
        self.sent_time = datetime.timestamp(datetime.now())

        return self.sent_time
    

    def send(self, recipient=None):
        """
        Querying is a protocol during which you first check that you are allowed to speak, that
        there is someone to listen, that your question is meaningful (or allowed) and then you can send your query
        """
        if self.is_replied and self.get_reply_validity():
            raise QueryRepliedError('this question has already been correctly answered, you don''t need to send it twice.')
        #self.check_and_pack() I dunno if an additional checking is necessary
        self.stamp()
        self.is_sent = True
        # TODO: decide whether asking again resets the question to unreplied to (as here)

        self.is_replied = False

        if recipient is None:
            recipient = self.get_recipient()

        recipient.receive(self)  # Assumes that all recipients contain a method to receive() queries

        return self.is_sent
    

    def reply_to(self, answer):
        """
        Assigns a Reply to the Query
        Caution: lists, tuples and sets are considered as a single object
        """    
        try:
            if self.help_required is not (answer[0].strip() == '?'):
                self.help_required = not self.help_required
                self.build_result()
        except (IndexError, AttributeError, TypeError):
            self.help_required = False #Important: to avoid looping over an empty string
            
        reply = Reply(self, answer)
        self.reply = reply
        reply.build_result()
        reply.get_validity()
        pre_satisfied = self.check_prerequisites()
        if not pre_satisfied:
            raise InvalidReplyError('This Query requires other queries to be satisfied first.')
        # TODO: decide if is_replied must be set to False if the reply is invalid.
        return reply


class QueryChoice(Query):
    """
    Query with multiple choices, defined in self.limits
    A QueryChoice accepts several answers. It is up to the user to handle one or several.
    """

    def __init__(self, *args, **kwargs):

        try:
            kwargs['limits'][0]
        except (TypeError, IndexError, KeyError):
            raise InvalidQueryError('QueryChoice called with no choices')

        super().__init__(*args, **kwargs)

    
    def build_result(self):
        
        result = []
        if self.help_required:
            result += [self.get_help_text()]
        result += [self.get_foreword()]
        result += [self.get_question()]
        
        if self.reply_type == ReplyType.NOTE:
            result[-1] += ' among ' + ', '.join(list(self.get_limits()))
        elif self.reply_type in [ReplyType.INPUTMODE, ReplyType.RENDERMODES]:
            choices = [str(i) + ') '+ str(choice.get_short_desc(self.get_recipient_locale())) for i, choice in enumerate(self.get_limits())]
            result[-1] += ' among:\n\n' + '\n'.join(choices)
        else:
            choices = [str(i) + ') '+ str(choice) for i, choice in enumerate(self.get_limits())]
            result[-1] += ' among:\n\n' + '\n'.join(choices)
       
        result += [self.get_afterword()]

        self.result = '\n'.join(filter(None, result)) + '\n'

        return self.result


    def check_reply(self):

        # Performs basic checking against ReplyType
        is_reply_valid = super().check_reply()

        if is_reply_valid is not True:
            return is_reply_valid
        else:
            if self.get_answer_index() is None: #answer exists otherwise is_reply_valid would be false
                is_reply_valid = False
            
            return is_reply_valid
        

    def get_answer_index(self, answer=None):
        """
        Returns the index i of the answer among n choices/limits (0<=i<=n), for QueryChoice and QueryBoolean
        """
        if answer is None:
            answer = self.reply.get_answer()
        
        choices = self.get_limits()  #limits cannot be None in QueryChoices, we made sure of that

        if isinstance(answer, str):
            answer = answer.lower().strip() #Sanitization for comparison
        
        if isinstance(choices[0], str):
            choices = [c.lower().strip() for c in choices]
        elif isinstance(choices[0], (InputMode, RenderMode)):
            choices = [str(c).lower().strip() for c in choices]

        try:
            index = choices.index(answer) #Tries to find the answer directly in choices=self.limits
        except ValueError:
            try:  # Maybe answer is not a choice, but the choice index (0-n)
                index = int(answer)
                if index < 0 or index > len(choices):
                    index = None
            except (ValueError, IndexError, TypeError):
                index = None
            
        return index



class QueryMultipleChoices(QueryChoice):
    """
    Query with several choices, defined in self.limits
    A QueryMultipleChoice accepts several answers.
    self.answer must be given as a list, eg ['answer1', 'answer2']
    """

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
 

    def check_reply(self):

        # Performs basic checking against ReplyType
        is_reply_valid = Query.check_reply(self)

        if is_reply_valid is not True:
            return is_reply_valid
        else:
            indices = self.get_answer_indices()
            if any([index is None for index in indices]):#also return False if indices is empty
                is_reply_valid = False
            
            return is_reply_valid
       

    def reply_to(self, answer):
        """
        Assigns a Reply to the Query, using answer as input
        If input is a string it is splitted using common column separators
        Caution: an answer tuple is considered as a single object
        """
        
        if isinstance(answer, str):
            answers = list(filter(None,re.split(r'\t| |,|;', answer)))
            if answers == []:
                answers = ['']
        elif not isinstance(answer, list):
            answers = [answer] #maybe the user has selected only 1 choice
        else:
            answers = answer
        
        super().reply_to(answers) #does self.answer=answer


    def get_answer_indices(self):
        
        answers = self.reply.get_answer()
        if not isinstance(answers, (list, set)):
            answers = [answers]  #repairing non-list answers o avoid looping over chars in a string
                
        return [QueryChoice.get_answer_index(self,answer) for answer in answers]


class QueryBoolean(QueryChoice):
    """
    A yes/no, true/false question type
    """

    def __init__(self, *args, **kwargs):
        # repairing missing choices
        self.default_limits = ['y', 'n']
        try:
            kwargs['limits'] = list(kwargs['limits'])
            if len(kwargs['limits']) % 2 != 0: # a tuple of couples is accepted: (yes,no,true,false,oui,non)
                kwargs['limits'] = self.default_limits
        except:
            kwargs['limits'] = self.default_limits
            
        super().__init__(*args, **kwargs)

    def build_result(self):

        result = []

        if self.help_required:
            result += [self.get_help_text()]
        result += [self.get_foreword()]
        result += [self.get_question() + ' (' + (self.get_limits()[0] +
                                                 '/' + self.get_limits()[1]) + ')']
        result += [self.get_afterword()]
        result = '\n'.join(filter(None, result))
        self.result = result
        return result


class QueryOpen(Query):
    """
    An open-ended Query, with almost no restriction on the answer
    excepted that a string answer can be checked against a regular expression in self.limits
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def check_reply(self):
        
        is_reply_valid = super().check_reply()

        if is_reply_valid is False:
            return is_reply_valid
        else:
            limits = self.get_limits()
            answer = self.reply.get_answer() #answer exists otherwise is_reply_valid would be false
            
            if limits is not None: 
                if len(limits) == 1 and self.reply_type == ReplyType.TEXT:
                    try:
                        regex = re.compile(limits[0])
                        if regex.search(answer) is None:#self.limits can be a RegEx
                            is_reply_valid = False
                    except (re.error, TypeError):
                        pass
    
            return is_reply_valid


class Information(QueryOpen):
    """
    An object passed to the recipient without expecting an answer
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expect_reply = False


class QueryMemory:
    """
    A volatile storage of Queries.
    With function to recall and erase Queries by type, property, content, ID...
    Note that erasing a Query here does *not* delete the object in Python
    """

    def __init__(self, owner, topic=None):

        self.owner = owner
        self.queries = []
        self.topic = topic  # A topic for this specific memory object
        self.query_filters = {
            'replied': lambda q: q.get_is_replied(),
            'sent': lambda q: q.get_is_sent(),
            'unreplied': lambda q: not q.get_is_replied(),
            'unsent': lambda q: not q.get_is_sent(),
            'valid_reply': lambda q: q.get_reply_validity(),
            'invalid_reply': lambda q: not q.get_reply_validity(),
            'unsatisfied': lambda q: not q.get_is_replied() or not q.get_reply_validity(),
            'from_me': lambda q: q.get_sender() == self.owner,
            'to_me': lambda q: q.get_recipient() == self.owner,
            'information': lambda q: not q.expect_reply(),
            'query': lambda q: q.expect_reply(),
        }
        self.query_sorting = {
                'date': Query.get_sent_time,
                'name': Query.get_name,
                'identifier': Query.get_identifier,
                'question': Query.get_question,
                'sender': Query.get_sender,
                'recipient': Query.get_recipient
                }

    def __repr__(self):

        string = '<' + self.__class__.__name__
        if self.topic is not None:
            string += ' about ' + repr(self.topic)
        string += ' with ' + str(
            len(self.queries)) + ' stored queries>'
        return string
    

    def __len__(self):

        return len(self.queries)
    

    def print_out(self, criterion=None, filters=None, sort_by=None):

        queries = self.recall(filters=filters, criterion=criterion, sort_by=sort_by)
        
        if len(queries) == 0:
            print('None')
        else:
            print(self)
            for i, q in enumerate(queries):
                print('----query#' + str(i) + '----')
                print(q)
                print('---------------')


    def recall_filtered(self, filters=None, sort_by=None):

        queries = self.queries.copy()

        if filters is not None:
            if not isinstance(filters, (list, tuple, set)):
                filters = [filters]
            for k in filters:
                queries = list(filter(self.query_filters[k], queries))
                
        if sort_by in self.query_sorting.keys():
            queries = sorted(queries, key=self.query_sorting[sort_by])
        
        return queries
    

    def recall_last(self, filters=None):
        """
        Recalls the last stored Query. If a topological sort has been made, it is the last one to be answered
        """
        queries = self.recall_filtered(filters)

        if len(queries) > 0:
            return queries[-1]
        else:
            return None
        

    def recall_first(self, filters=None):
        """
        Recalls the first query. If a topological sort has been made, it is the first one to be answered
        """
        queries = self.recall_filtered(filters)

        if len(queries) > 0:
            return queries[0]
        else:
            return None
        

    def recall_last_sent(self, filters=None):
        """
        Recalls the most recent Query (the last one sent, unsent queries have no daye)
        """
        queries = self.recall_filtered(filters)

        if len(queries) > 0:
            chronos = sorted(queries, key=Query.get_sent_time)
            return chronos[-1]
        else:
            return None
        

    def recall_by_identifier(self, identifier, filters=None, sort_by=None):
        """
        Recalls Queries with the given identifier
        """
        queries = self.recall_filtered(filters, sort_by)
        if isinstance(identifier, str):
            identifier = identifier.lower().strip()
        return [q for q in queries if q.get_identifier() == identifier]
          

    def recall_by_sender(self, sender, criterion=None, filters=None, sort_by=None):
        queries = self.recall(criterion=criterion, filters=filters, sort_by=sort_by)
        return [q for q in queries if q.get_sender() == sender]
                

    def recall_by_recipient(self, recipient, criterion=None, filters=None, sort_by=None):
        queries = self.recall(criterion=criterion, filters=filters, sort_by=sort_by)
        return [q for q in queries if q.get_recipient() == recipient]
                

    def has_query(self, criterion=None, filters=None):
        return len(self.recall(criterion=criterion, filters=filters) > 0)
    

    def recall_information(self, filters=None, sort_by=None):

        queries = self.recall_filtered(filters, sort_by)
        return [q for q in queries if q.get_expect_reply() == False]
    

    def recall(self, criterion=None, filters=None, sort_by=None):
        """
        Recalls Queries matching criterion, which can be a list index, a string to be searched, or a Query identifier
        """
        queries = self.recall_filtered(filters, sort_by)

        if criterion is None or criterion == '':
            return queries

        q_found = []
        if isinstance(criterion, int):
            try:
                q_found = queries[criterion]  # Maybe criterion is an index
            except IndexError:
                q_found = self.recall_by_identifier(criterion=criterion, filters=filters, sort_by=sort_by)  # Maybe criterion is an integer identifier
        elif isinstance(criterion, Query):  # Maybe criterion is a Query
            if criterion in queries:
                q_found.append(criterion)
        else:
            for q in queries:  # Maybe criterion is an attribute, some text for instance
                attr_vals = list(q.__dict__.values())
                if criterion in attr_vals:
                    q_found += [q]
            #Maybe criterion is a regular expression
            if len(q_found) == 0:
                try:
                    regex = re.compile(criterion.lower().strip())
                except:
                    pass
                else:
                    #Maybe criterion is a regular expression
                    for q in queries:
                        str_attr = filter(lambda x: isinstance(x,str),list(q.__dict__.values()))
                        if any([regex.search(attr.lower().strip()) is not None for attr in str_attr]):
                            q_found += [q]
                            
        return q_found


    def recall_unsent(self, filters=None, sort_by=None):
        queries = self.recall_filtered(filters, sort_by)
        return [q for q in queries if q.get_is_sent() == False]
    

    def recall_replied(self, filters=None, sort_by=None):
        queries = self.recall_filtered(filters, sort_by)
        return [q for q in queries if q.get_is_replied()]
    

    def recall_unreplied(self, filters=None, sort_by=None):
        queries = self.recall_filtered(filters, sort_by)
        return [q for q in queries if not q.get_is_replied()]

    
    def recall_by_invalid_reply(self, filters=None, sort_by=None):
        q_replied = self.recall_replied(filters, sort_by)
        return [q for q in q_replied if not q.get_reply_validity()]
    

    def recall_unsatisfied(self, filters=None, sort_by=None):
        queries = self.recall_filtered(filters, sort_by)
        return [q for q in queries if (not q.get_is_replied() or not q.get_reply_validity())]
    

    def recall_repeated(self, filters=None, sort_by=None):
        """
        Recall queries that have been stored twice or more
        """
        queries = self.recall_filtered(filters, sort_by)

        if len(queries) < 2:
            return None
        else:
            identifiers = [q.get_identifier() for q in queries]

            seen = set()
            repeated = set()

            for identifier in identifiers:
                if identifier in seen:
                    repeated.add(identifier)
                else:
                    seen.add(identifier)

            repeated = [q for q in queries if q.get_identifier() in repeated]

        return repeated
    

    def erase_repeated(self, filters=None):
        """
        Erase repeated Queries, keeping the most recent in time
        """
        repeated = self.recall_repeated(filters)

        # Probably the most recent query is the last one of the list but one never knows
        # Also, we can change the criterion from 'latest asked' to 'better answered'
        try:
            repeated[1]
            repeated = sorted(repeated, key=Query.get_sent_time)
            for q in repeated[0:-1]:
                self.queries.remove(q)
            return True
        except (IndexError, TypeError):
            return False
        

    def store(self, query):

        if isinstance(query, Query):
            self.queries.append(query)
        elif isinstance(query, (list, tuple)):
            for q in query:
                self.queries.append(q)
        else:
            raise InvalidQueryError('cannot store ' + str(type(query)) + ' in memory, only ' + str(Query.__name__) + ' are supported')

        return True
    

    def erase_all(self):

        self.queries.clear()
        return True
    

    def erase(self, criterion=None, filters=None):
        """
        Erases Queries matching criterion
        """
        queries = self.recall_filtered(filters)

        if criterion in queries:
            # removes the query directly
            self.queries.remove(criterion)
            return True

        # searches for a query matching criterion and removes it
        if criterion is not None and criterion != '':
            [self.queries.remove(q) for q in self.recall(filters=filters, criterion=criterion)]
            return True
        else:
            return False
        

    def clean(self):
        self.erase_repeated(filters=('unreplied'))
        # TODO: erase invalid replies?
        # for q in self.recall_by_invalid_reply():
        #    self.queries.remove(q)
        self.topological_sort()
        

    def flush(self):
        self.erase(filters=('replied'))
        self.topological_sort()
        # TODO: perform self.clean?
        

    def chronological_sort(self):
        """
        Sort self.queries by sent date and affects stored list
        """
        self.queries = sorted(self.queries, key=Query.get_sent_time)
        return self.queries
    

    def topological_sort(self):
        """
        Sort self.queries by solving dependencies, and affects stored list
        """
        queries = self.queries.copy() # A copy of the queries list with the real queries inside
        
        if len(queries) <= 1:
            return queries

        edgeless_nodes = set() # node = (i, query) where i is an integer

        for i, q in enumerate(queries):
            if len(q.get_prerequisites()) == 0:
                edgeless_nodes.add((i, q))

        if len(edgeless_nodes) == 0:
            raise QueryMemoryError('Queries have a circular dependency')
        
        
        sorted_nodes = list()  # L

        queries_egdes = [q.get_prerequisites().copy() for q in queries] # A copy of the prerequisites
        i = 0
        while len(edgeless_nodes) > 0 and i < len(queries) ** 2: # The algorithm complexity is not greater than n^2
            i += 1

            sorted_node = edgeless_nodes.pop()
            sorted_nodes.append(sorted_node) #If a node has not edge among remaining nodes to be sorted, then it is the next one in the sort order
            (sorted_node_n, sorted_node_q) = sorted_node
            #print('Added ' + str(sorted_node_q.get_name()) + ' to sorted_modes.')

            for (m, query_egdes), query in zip(enumerate(queries_egdes), queries):
                if sorted_node_q in query_egdes:
                    query_egdes.remove(sorted_node_q) # This node has been sorted, so it can be removed from dependencies
                    #print('Found in edges of ' + str(query.get_name()) + ': ' + str(sorted_node_q.get_name()))
                    if len(query_egdes) == 0:
                        edgeless_nodes.add((m, query))
                        #print('Added ' + str(query.get_name()) + ' to edgeless_nodes.')
        
        if len(sorted_nodes) == len(self.queries):
            self.queries = [self.queries[node[0]] for node in sorted_nodes]
            return self.queries
        else:
            raise QueryMemoryError('Topological sort has failed at i=' + str(i))
            return None


