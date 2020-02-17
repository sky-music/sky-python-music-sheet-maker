import re
from modes import ReplyType, InputMode
from datetime import datetime


# from PIL import Image


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

    def __init__(self, query, answer=None):

        self.query = query  # the question that was asked in the first place
        self.result = None
        self.answer = answer
        self.is_valid = None

        if not isinstance(query, Query):
            raise InvalidReplyError('this reply does not follow any query')

    def __str__(self):
        string = '<' + self.__class__.__name__ + ' from ' + str(self.query.get_recipient()) + ' to ' + str(
            self.query.get_sender()) + ': '
        if isinstance(self.get_result(), str):
            string += repr(self.get_result())
        else:
            string += str(self.get_result())
        string += '>'

        return string

    def get_result(self):
        return self.result

    def set_result(self, result):
        self.result = result

    def get_validity(self):
        if self.is_valid is None:
            self.is_valid = self.check_result()
        return self.is_valid

    def build_result(self):
        self.result = self.answer

    def check_result(self):
        """
        Only the Query can tell if the result is valid
        """
        self.is_valid = self.query.check_reply()
        return self.is_valid


class Query:

    def __init__(self, sender=None, recipient=None, question=None, foreword=None, afterword=None,
                 reply_type=ReplyType.OTHER, limits=None, prerequisites=None):
        """
        A question object

        Choices are for questions where the user chooses 1 item from multiple choices
        Boolean means choosing between 2 choices
        """

        self.sender = sender
        self.recipient = recipient
        self.question = question
        self.foreword = foreword
        self.afterword = afterword
        self.reply_type = reply_type  # Expected type of the reply, among ReplyType
        self.limits = limits  # Choices, regexp...
        self.prerequisites = prerequisites  # Other Queries required to reply to this Query
        self.UID = None  # A unique ID based on the Query content, excluding the timestamp
        self.sent_time = None  # The timestamp at which the Query was sent()

        '''
        TODO: decide how to check for sender and recipient types:
            - by checking the class of the sender object
            - by comparing sender to a list of strings, so the sender must send an identification string
            - by asking the send back who is his (eg sender.get_type(), if such a property exist)
            => the choice will depend on the bot structure (since we can do whatever we want with music cog)
            => a possibility is to check first if the sender is music cog, and if not (AttributeError), then it is the bot
        '''
        self.valid_locutors = ['bot', 'music-sheet-maker']  # A list of valid locutors

        self.reply = None  # Reply object
        self.result = None  # The full question with foreword and afterword
        self.is_sent = False  # The send() command has been called
        self.is_replied = False  # Has been assigned a Reply object

    def __str__(self):
        string = '<' + self.__class__.__name__ + ' ' + str(self.get_UID()) + ' from ' + str(self.sender) + ' to ' + str(
            self.recipient) + ': ' + repr(self.question) + ', ' + str(self.reply_type) + ' expected'
        try:
            self.get_limits()[0]
            string += ', within ' + str(self.limits)
        except (TypeError, IndexError):
            pass
        string += '>'

        return string

    def get_sender(self):
        return self.sender

    def get_recipient(self):
        return self.recipient

    def get_question(self):
        return self.question

    def get_result(self):
        return self.result

    def set_result(self, result):
        self.result = result

    def get_reply(self):
        return self.reply

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

    def get_reply_type(self):
        return self.reply_type

    def get_limits(self):
        return self.limits

    def get_is_replied(self):
        return self.is_replied

    def get_is_sent(self):
        return self.is_sent

    def get_UID(self):
        return self.UID

    def get_sent_time(self):
        return self.sent_time

    def get_prerequisites(self):
        if self.prerequisites is None:
            return []
        if len(self.prerequisites) == 0:
            return []
        if not isinstance(self.prerequisites, (list, tuple)):
            return [self.prerequisites]
        else:
            return self.prerequisites

    def check_sender(self):
        if self.sender is None:
            raise InvalidQueryError('invalid sender. Sender is ' + str(self.sender))
        else:
            if len(self.valid_locutors) == 0:
                return True
            else:
                # TODO: more elaborate checking
                # if isinstance(self.sender, bot) or ...
                if type(self.sender) != type(self.valid_locutors[0]):
                    raise InvalidQueryError('invalid sender. It must be of ' \
                                            + repr(type(self.valid_locutors[0]).__name__) \
                                            + ' type and among ' + str(self.valid_locutors))
                else:
                    if self.sender in self.valid_locutors:
                        return True

        return False

    def check_recipient(self):
        if self.recipient is None:
            raise InvalidQueryError('invalid recipient ' + str(self.recipient))
        else:
            if len(self.valid_locutors) == 0:
                return True
            else:
                # TODO: more elaborate checking
                if self.recipient == self.sender:
                    raise InvalidQueryError('sender cannot ask a question to itself')

                if type(self.recipient) != type(self.valid_locutors[0]):
                    raise InvalidQueryError('invalid recipient. It must be of ' \
                                            + repr(type(self.valid_locutors[0]).__name__) \
                                            + ' type and among ' + str(self.valid_locutors))

                return True

        return False

    def check_question(self):
        if self.question is not None:
            # TODO: add checking among more types, if needed
            if isinstance(self.question, str):
                return True
            else:
                raise InvalidQueryError('only string (str) questions are allowed at the moment')
        else:
            raise InvalidQueryError('question is None')

        return False

    def check_limits(self):

        limits = self.get_limits()

        if limits is None:
            return True
        else:
            try:
                item = limits[0]
            except (IndexError, TypeError):
                item = limits

            if (self.reply_type == ReplyType.TEXT or self.reply_type == ReplyType.NOTE) and not isinstance(item, str):
                raise InvalidQueryTypeError('incorrect limits type', item, str)

            if self.reply_type == ReplyType.INTEGER:
                try:
                    int(item)
                except:
                    raise InvalidQueryTypeError('incorrect limits type', item, int)

            if self.reply_type == ReplyType.INPUTMODE and not isinstance(item, InputMode):
                raise InvalidQueryTypeError('incorrect limits type', item, InputMode)

            if any([type(limit) != type(item) for limit in limits]):
                raise InvalidQueryError('limits are not all of the same type')

            # smart guess of some types
            if self.reply_type is None:
                if isinstance(item, str):
                    try:
                        int(item)
                        self.reply_type = ReplyType.INTEGER
                    except:
                        self.reply_type = ReplyType.TEXT
                elif isinstance(item, InputMode):
                    self.reply_type = ReplyType.INPUTMODE
                else:
                    # TODO: decide if its better to leave it to none instead
                    self.reply_type = ReplyType.OTHER

    def check_reply(self):

        if not isinstance(self.reply, Reply):

            self.is_replied = False
            return None

        else:
            # TODO: add checks for testing the validity of the reply
            # check for length, type, length
            # Typically this method is overridden by derived classes
            self.is_replied = True
            self.reply.is_valid = False

            answer = self.reply.get_result()

            if answer is not None:
                if self.get_reply_type() in [ReplyType.TEXT, ReplyType.NOTE, ReplyType.INTEGER]:
                    if isinstance(answer, str):
                        self.reply.is_valid = True
                elif self.get_reply_type() == ReplyType.INPUTMODE:
                    if isinstance(answer, InputMode) or isinstance(answer, str):
                        self.reply.is_valid = True
                else:
                    self.reply.is_valid = True

            return self.reply.is_valid

    def build_result(self):

        result = [self.get_foreword()]
        result += [self.get_question()]
        result += [self.get_afterword()]
        result = '\n'.join(filter(None, result))
        self.set_result(result)
        return result  # Generic return, will be overridden in derived classes

    def stamp(self):
        """
        Assigns an UID and a timestamp to the Query
        
        """
        self.UID = hash(','.join([str(self.get_sender()), str(self.get_recipient()), str(self.get_result()),
                                  str(self.get_limits()), str(self.get_prerequisites())]))

        self.sent_time = datetime.timestamp(datetime.now())

        return self.UID, self.sent_time

    def send(self):
        """
            Querying is a protocol during which you first check that you are allowed to speak, that
            there is someone to listen, that your question is meaningful (or allowed)
            and then you can send your query
        """
        if self.is_replied:
            if self.reply.check_reply():
                raise QueryRepliedError('this question has already been answered')
        self.check_sender()
        self.check_recipient()
        self.check_question()
        self.check_limits()
        self.build_result()
        self.stamp()
        self.is_sent = True
        # TODO: decide whether asking again resets the question to unreplied to (as here)
        self.is_replied = False

        return self.is_sent

    def receive(self, reply_result, prerequisite=None):
        # TODO: maybe it is iseless to pass seld as argument to reply since rely is already a property of self
        self.reply = Reply(self, reply_result)
        self.reply.build_result()
        is_reply_valid = self.reply.check_result()
        if is_reply_valid is not None:
            self.is_replied = True
        # TODO: decide if is_replied must be set to False of the reply is invalid.
        return self.is_replied


class QueryChoice(Query):
    """
    Query with multiple choices
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self.limits[0]
        except (TypeError, IndexError):
            raise InvalidQueryError('QueryChoice called with no choices')

    def build_result(self):

        result = self.get_foreword()

        if self.get_limits() is not None:
            result += '\n'

        # TODO: handles types other than string
        for i, choice in enumerate(self.get_limits()):

            if self.reply_type == ReplyType.NOTE:
                if i > 0:
                    choice_str = ', '
                else:
                    choice_str = ''
                choice_str += str(choice)

            elif self.reply_type == ReplyType.INPUTMODE:
                choice_str = str(i) + ') ' + choice.value[2] + '\n'
                # modes_list[i] = mode

            else:
                choice_str = str(i) + ') ' + str(choice) + '\n'

            result += choice_str

        result += self.get_afterword()

        self.set_result(result)

        return result

    def check_reply(self):

        # Performs basic checking against ReplyType
        self.reply.is_valid = super().check_reply()

        if self.reply.is_valid is not True:
            return self.reply.is_valid

        answer = self.reply.get_result()
        choices = self.get_limits()

        if isinstance(answer, str):
            answer = answer.lower().strip()
        if isinstance(choices[0], str):
            choices = [c.lower().strip() for c in choices]

        if answer is None:
            self.reply.is_valid = False
        elif answer in choices:
            self.reply.is_valid = True
        else:
            try:
                choices[int(answer)]
                self.reply.is_valid = True
            except:
                self.reply.is_valid = False

        return self.reply.is_valid


class QueryBoolean(QueryChoice):
    """
    A yes/no, true/false question type
    """

    def __init__(self, **kwargs):
        # repairing missing choices
        self.default_limits = ('y', 'n')
        try:
            kwargs['limits'][0]
            kwargs['limits'][1]
            if len(kwargs['limits']) != 2:
                kwargs['limits'] = self.default_limits
        # TODO: decide whether we want to repair limits only if len()!=2, or also if len() is odd (then treat each 2
        #  limits as a possible yes/no couple), or raise an error
        except:
            kwargs['limits'] = self.default_limits
        super().__init__(**kwargs)

    def build_result(self):

        result = []

        result += [self.get_foreword()]
        result += [self.get_question() + ' (' + (self.limits[0] +
                                                 '/' + self.limits[1]) + ')']
        result += [self.get_afterword()]
        result = '\n'.join(filter(None, result))
        self.set_result(result)
        return result


class QueryOpen(Query):
    """
    An open-ended Query,
    excepted that a string answer can be checked against a regular expression in limits
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def check_reply(self):

        self.reply.is_valid = super().check_reply()

        if self.reply.is_valid is not True:
            return self.reply.is_valid

        try:
            match = re.search(self.get_limits(), self.reply.get_result())
            if match is None:
                self.reply.is_valid = False
        except TypeError:
            pass

        return self.reply.is_valid


class Information:

    def __init__(self, text, sender=None, recipient=None):

        self.text = text
        self.sender = sender
        self.recipient = recipient


class QueryMemory:
    """
    Storage for Queries.
    With function to recall and erase Queries by type, property...
    Note that erasing a Query here does *not* delete the object in Python
    
    """

    def __init__(self):

        self.queries = []

    def __str__(self):

        return '<' + self.__class__.__name__ + ' with ' + str(len(self.queries)) + ' stored queries>'

    def __len__(self):

        return len(self.queries)

    def recall_last(self):
        """
        Recalls the last Query stored
        """
        if len(self.queries) > 0:
            return self.queries[-1]
        else:
            return None

    def recall_last_sent(self):
        """
        Recalls the most recent Query (the last one sent)
        """
        if len(self.queries) > 0:
            chronos = sorted(self.queries, key=Query.get_sent_time)
            return chronos[-1]
        else:
            return None

    def recall(self, criterion=None):
        """
        Recalls Queries matching criterion
        """
        if criterion is None or criterion == '':
            return self.queries

        if isinstance(criterion, int):
            try:
                q = self.queries[criterion]
                return q
            except IndexError:
                print('no query #' + str(criterion))
        else:
            q_found = []
            for q in self.queries:
                attr_vals = list(q.__dict__.values())
                if criterion in attr_vals:
                    q_found.append(q)
            return q_found

    def recall_unsent(self):

        qlist = [q for q in self.queries if q.get_is_sent() == False]
        return qlist

    def recall_replied(self):

        return [q for q in self.queries if q.get_is_replied()]

    def recall_unreplied(self):

        return [q for q in self.queries if not q.get_is_replied()]

    def recall_by_invalid_reply(self):

        q_replied = self.recall_replied()
        return [q for q in q_replied if not q.reply.get_validity()]

    def recall_repeated(self):
        """
        Recall queries that have been stored twice or more
        TODO: decide if we check for is_sent
        """
        queries = self.queries

        if len(queries) < 2:
            return None
        else:
            UIDs = [q.get_UID() for q in queries]

            seen = set()
            repeated = set()

            for UID in UIDs:
                if UID in seen:
                    repeated.add(UID)
                else:
                    seen.add(UID)

            repeated = [q for q in queries if q.get_UID() in repeated]

        return repeated

    def erase_repeated(self):
        """
        Erase repeated Queries, keeping the most recent in time
        
        """
        repeated = self.recall_repeated()

        # Probably the most recent query is the last one of the list but one never knows
        # Also, we can change the criterion from 'latest asked' to 'better answered'
        if len(repeated) >= 2:
            repeated = sorted(repeated, key=Query.get_sent_time)
            for q in repeated[0:-1]:
                self.queries.remove(q)
            return True
        else:
            return False

    def store(self, query):

        # TODO: add support for storing Information

        if isinstance(query, Query):
            self.queries.append(query)
        elif isinstance(query, (list, tuple)):
            for q in query:
                self.queries.append(q)
        else:
            raise InvalidQueryError('cannot store other objects than ' + str(Query.__name__))

        return True

    def erase_all(self):

        self.queries.clear()
        return True

    def erase(self, criterion=None):
        """
        Erases Queries matching criterion
        """
        if criterion in self.queries:
            # removes the query directly
            self.queries.remove(criterion)
            return True
        else:
            # searches for a query matching criterion and removes it
            if criterion is not None and criterion != '':
                [self.queries.remove(q) for q in self.recall(criterion)]
                return True
            else:
                return False

    def topological_sort(self):

        queries = self.queries.copy()

        if len(queries) <= 1:
            return queries

        edgeless_nodes = set()

        for i, q in enumerate(queries):
            if len(q.get_prerequisites()) == 0:
                edgeless_nodes.add((i, q))

        if len(edgeless_nodes) == 0:
            raise QueryMemoryError('Queries have a circular dependency')

        sorted_nodes = list()  # L

        i = 0
        while len(edgeless_nodes) > 0 and i < len(queries) ** 2:
            i += 1

            node = edgeless_nodes.pop()
            sorted_nodes.append(node)

            for m, query in enumerate(queries):
                edges = query.get_prerequisites()
                if node[1] in edges:
                    edges.remove(node[1])
                    if len(edges) == 0:
                        edgeless_nodes.add((m, query))

        if len(sorted_nodes) == len(self.queries):
            self.queries = [self.queries[node[0]] for node in sorted_nodes]
            return self.queries
        else:
            raise QueryMemoryError('Topological sort has failed at i=' + str(i))
            return None
