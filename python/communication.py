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

from modes import ReplyType
from PIL import Image


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


class Reply:

    def __init__(self, query):

        self.query = query  # the question that was asked in the first place
        self.result = None
        self.isvalid = None
        if not isinstance(query, Query):
            raise InvalidReplyError('this reply does not follow any query.')

    def get_result(self):
        if self.isvalid:
            return self.result
        else:
            return None

    def set_result(self, result):
        self.result = result

    def get_validity(self):
        if self.isvalid is None:
            self.isvalid = self.check_result()
        return self.isvalid

    def check_result(self):
        """
        Only the Query can tell if the result is valid.
        """
        self.isvalid = self.question.check_result()
        return self.isvalid


class Query:

    def __init__(self, sender=None, recipient=None, question=None, foreword=None, afterword=None, reply_type=ReplyType.TEXT,limits=None):
        """
        A question object

        Choices are for questions where the user chooses from multiple limits
        """
        '''
        TO-DOs:
        a question is a request for information
        it has one or several formulations
        it has one or several possible replies
        it is repeated (or not) after a given time if no reply is given
        it is repeated (or not) if a blank reply is given
        for some questions there is a default reply (yes/no questions, and choice within a set, eg song key), for other not (open questions, such as “composer name”)
        a question has a “replied”/“not replied” status
        “reply” could be a property of question or a separate object
        the internal reply can be different from the reply you give out (for instance, the reply to ‘what is the song key?’ can be C, but you give the reply 'do' instead).
        etc
        '''
        self.sender = sender
        self.recipient = recipient
        self.question = question
        self.foreword = foreword
        self.afterword = afterword
        self.reply_type = reply_type
        self.limits = limits
        self.result = None

        '''
        TODO: decide how to check for sender and recipient types:
            - by checking the class of the sender object
            - by comparing sender to a list of strings, so the sender must send an identification string 
            - by asking the send back who is his (eg sender.get_type(), if such a property exist)
            => the choice will depend on the bot structure (since we can do whatever we want with music cog)
            => a possibility is to check first if the sender is music cog, and if not (AttributeError), then it is the bot
        '''
        self.valid_locutors = ['bot', 'music-cog']

        self.reply = None
        self.is_replied = False

        self.is_sent = False
        self.sender_type = None
        self.recipient_type = None
        self.type = None  # Yes/no, list of limits, open-ended — from QueryType # Overidden by the derived classes
        self.depends_on = []  # A list of other Querys objects (or class types?) that this depends on
        # TODO: decide how depends_on will be set
        self.is_asked = False
        self.is_reply_valid = None
        self.is_replied = False

    def get_sender(self):
        return self.sender

    def get_recipient(self):
        return self.recipient

    def get_question(self):
        return self.question

    def get_reply(self):
        return self.reply

    def get_foreword(self):
        return self.foreword

    def get_afterword(self):
        return self.afterword

    def get_limits(self):
        return self.limits

    def get_is_replied(self):
        return self.is_replied

    def check_sender(self):
        if self.sender is not None:
            # TODO: more elaborate checking
            # if isinstance(self.sender, bot) or ...
            if not type(self.sender) == type(self.valid_locutors[0]):
                raise InvalidQueryError(
                    'invalid sender. It must be of ' + repr(type(self.valid_locutors[0]).__name__) + ' type and among ' + str(
                        self.valid_locutors))
            else:
                if self.sender in self.valid_locutors:
                    return True
        else:
            raise InvalidQueryError('invalid sender. Sender is ' + str(self.sender))
            
        return False

    def check_recipient(self):
        if self.recipient is not None:
            # TODO: more elaborate checking
            if self.recipient == self.sender:
                raise InvalidQueryError('sender cannot ask a question to itself.')
            return True
        else:
            raise InvalidQueryError('invalid recipient. Recipient is ' + str(self.recipient))
        
        return False

    def check_question(self):
        if self.question is not None:
            # TODO: add checking among more types, if needed
            if isinstance(self.result, str):
                return True
            else:
                raise InvalidQueryError('only string (str) questions are allowed at the moment.')
        else:
            raise InvalidQueryError('question is undefined.')
            
        return False

    def check_limits(self):
        if self.limits is not None:
            if isistance(self.limits, list) or isinstance(self.limits, tuple):
                item = self.limits[0]
            else:
                item = self.limits
            if (self.reply_type == ReplyType.TEXT or self.reply_type == ReplyType.NOTE) and not isinstance(item, str):
                raise QueryError('incorrect limits type. str expected, ' + str(type(item).__name__)+ 'given.')
            if self.reply_type == ReplyType.INTEGER:
               try:
                   int(item)
               except:
                   raise QueryError('incorrect limit passed to Query')
            if self.reply_type == None:
                if isinstance(item,str):
                    try:
                        int(item)
                        self.reply_type = ReplyType.INTEGER
                    except:
                         self.reply_type = ReplyType.TEXT

    def check_reply(self):
        if isinstance(self.reply, Reply):
            # TODO: add checks for testing the validity of the reply
            # for instance, if a music key is expected, check that it belongs to a dictionary
            # check for length, type, length
            # Typically this method is overridden by derived classes
            self.is_replied = True

            if self.reply.get_result() is not None:
                self.is_reply_valid = True
            else:
                self.is_reply_valid = False
        else:
            self.is_replied = False
        return self.is_reply_valid

    def build_result(self):

        return self.get_result()  # Generic return, will be overridden in derived classes

    def send(self):
        """
            Querying is a protocol during which you first check that you are allowed to speak, that
            there is someone to listen, that your question is meaningful (or allowed)
            and then you can send your query
        """
        self.check_sender()
        self.check_recipient()
        self.check_question()
        self.build_result()
        self.is_sent = True
        self.is_replied = False  # TODO: decide whether asking again resets the question to unreplied to (as here)

        return is_sent

    def receive_reply(self, reply):
        self.reply = reply
        is_reply_valid = self.check_reply()
        if is_reply_valid is not None:
            self.is_replied = True
        # TODO: decide if is_replied must be set to False of the reply is invalid.
        return self.is_replied


'''
class QueryText(Query):  # TODO: is this inherited from QueryOpen but the Reply needs to be a string?
    """
        A class in which both the question and the reply are strings (including numbers parsed as text)
    """

    def check_question(self):
        if self.question_string is not None:
            if isinstance(self.question_string, str):
                return True
            else:
                raise InvalidQueryError(
                    'Invalid question type. ' + type(self.question_string) + ' was given, str was expected.')
        else:
            raise InvalidQueryError('Undefined question.')

    def check_reply(self):
        if self.reply is not None:
            if isinstance(self.reply, str):
                return True
            else:
                raise InvalidQueryError(
                    'Invalid reply type. ' + type(self.reply) + ' was given, str was expected.')

    def build_question(self):

        self.question = self.get_foreword()

        return self.question  # Generic return, will be overridden in derived classes
'''


class QueryBoolean(Query):
    """
    a yes/no, true/false question type
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.limits == None:
            self.limits = ['y','n']
        else:
            if len(self.limits) is not 2:
                raise QueryError('incorrect limits argument passed to QueryBoolean')

    def build_result(self):
        self.result = self.get_foreword()
        self.result += self.get_question()
        self.result += self.limits[0] + '/' + self.limits[1]
        self.results +=self.afterwords
        return self.result
        


class QueryChoice(Query):
    """
    Query with multiple choices
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self.limits[0]
        except (TypeError, IndexError):
            raise InvalidQueryError('QueryChoice called with no choices.')

    def build_result(self):
        self.result = self.get_foreword()

        if self.get_limits() is not None:
            self.result += '\n'

        for i, choice in enumerate(self.get_limits()):
            self.result += str(i) + ') '
            self.result += choice + '\n'

        return self.result



class QueryOpen(Query):
    """
    Query open-ended
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.limits = None  # limits are ignored




'''


def check_reply(self):
        if self.reply is not None:
            if not isinstance(self.reply, str):
                raise InvalidQueryError(
                    'Invalid reply type. ' + type(self.reply) + ' was given, str was expected.')
            else:
                if self.reply.lower() in [choice.lower() for choice in self.limits]:
                    return True
                    
'''
