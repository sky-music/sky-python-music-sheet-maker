import re
from modes import ReplyType, InputMode
from datetime import datetime


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
        string += ', valid=' + self.get_validity()
        string += '>'

        return string

    def get_answer(self):
        return self.answer

    def get_validity(self):
        if self.is_valid is not True:
            self.is_valid = self.query.check_reply()
        return self.is_valid

    def build_result(self):

        if self.get_validity() == False:
            self.result = None
            return self.result

        if isinstance(self.query, QueryBoolean):
            self.result = (self.query.get_answer_index() % 2 == 0)
        elif isinstance(self.query, QueryChoice):
            self.result = self.query.get_answer_index()
        else:
            self.result = self.answer
            if self.query.reply_type == ReplyType.INTEGER:
                self.result = int(self.answer)

        return self.result

    def get_result(self):
        if self.result == None:
            self.build_result()
        return self.result


class Query:

    def __init__(self, sender=None, recipient=None, question=None, foreword=None, afterword=None,
                 reply_type=ReplyType.OTHER, limits=None, prerequisites=None):
        """
        A generic Query object

        QueryChoice is for questions where the user chooses 1 item from multiple choices
        QueryBoolean means choosing between 2 choices
        QueryOpen is for an open-ended query
        """

        self.sender = sender
        self.recipient = recipient
        self.question = question
        self.foreword = foreword
        self.afterword = afterword
        self.reply_type = reply_type  # Expected type of the reply, among ReplyType
        self.limits = limits  # Choices, regexp...
        self.prerequisites = prerequisites  # Other Queries required to reply to this Query
        self.identifier = None  # A unique ID based on the Query content, excluding the timestamp
        self.sent_time = None  # The timestamp at which the Query was sent()
        self.expect_reply = True

        '''
        TODO: decide how to check for sender and recipient types:
            - by checking the class of the sender object
            - by comparing sender to a list of strings, so the sender must send an identification string
            - by asking the send back who is his (eg sender.get_type(), if such a property exist)
            => the choice will depend on the bot structure (since we can do whatever we want with music cog)
            => a possibility is to check first if the sender is music cog, and if not (AttributeError), then it is the bot
        '''
        self.valid_locutors_names = ['music-cog', 'music-sheet-maker', 'command-line']  # A list of valid locutors

        self.reply = None  # Reply object
        self.result = None  # The full question with foreword and afterword
        self.is_sent = False  # The send() command has been called
        self.is_replied = False  # Has been assigned a Reply object

        self.check_and_pack()

    def __str__(self):
        string = '<' + self.__class__.__name__ + ' ' + str(self.get_identifier()) + ' from ' + str(
            self.sender.get_name()) + ' to ' + str(
            self.recipient.get_name()) + ': ' + repr(self.question) + ', ' + str(self.reply_type) + ' expected'
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

    def get_sender(self):
        return self.sender

    def get_recipient(self):
        return self.recipient

    def get_question(self):
        return self.question

    def get_result(self):
        return self.result

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

    def get_expect_reply(self):
        return self.expect_reply

    def get_limits(self):
        '''
        Returns None or a list with len>0
        '''
        if self.limits is None:
            return None
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
            return self.get_reply().get_validity()
        except AttributeError:
            return None

    def get_is_sent(self):
        return self.is_sent

    def get_identifier(self):
        return self.identifier

    def get_sent_time(self):
        return self.sent_time

    def get_prerequisites(self):
        if self.prerequisites is None:
            return []
        if not isinstance(self.prerequisites, (list, tuple, set)):
            return [self.prerequisites]
        else:
            return self.prerequisites

    def check_locutor(self, locutor, allowed='all', forbidden=None):

        def get_name_and_sanitize(obj):
            if isinstance(obj, str):
                obj_name = obj
            else:
                try:
                    obj_name = obj.get_name().lower().strip()
                except AttributeError:
                    try:
                        obj_name = obj.__name__.lower().strip()
                    except AttributeError:
                        obj_name = type(obj).__name__.lower().strip()
            return obj_name.lower().strip()

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

            locutor_name = get_name_and_sanitize(locutor)

            if locutor_name not in self.valid_locutors_names:
                locutor_ok = False
                # print(locutor_name)
                # print(self.valid_locutors_names)
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
        if len(limits) == 0:
            return True

        if (self.reply_type == ReplyType.TEXT or self.reply_type == ReplyType.NOTE) and not isinstance(limits[0], str):
            raise InvalidQueryTypeError('incorrect limits type', limits[0], str)

        if self.reply_type == ReplyType.INTEGER:
            try:
                int(limits[0])
            except:
                raise InvalidQueryTypeError('incorrect limits type', limits[0], int)

        if self.reply_type == ReplyType.INPUTMODE and not isinstance(limits[0], InputMode):
            raise InvalidQueryTypeError('incorrect limits type', limits[0], InputMode)

        if any([type(limit) != type(limits[0]) for limit in limits]):
            raise InvalidQueryError('limits are not all of the same type')

        # smart guess of some types
        if self.reply_type is None:
            if isinstance(limits[0], str):
                try:
                    int(limits[0])
                    self.reply_type = ReplyType.INTEGER
                except:
                    self.reply_type = ReplyType.TEXT
            elif isinstance(limits[0], InputMode):
                self.reply_type = ReplyType.INPUTMODE
            else:
                # TODO: decide if its better to leave it to none instead
                self.reply_type = ReplyType.OTHER

    def check_reply(self):

        # if self.expect_reply is False:
        #    return True

        if not isinstance(self.reply, Reply):
            self.is_replied = False
            return None

        else:
            # TODO: add checks for testing the validity of the reply
            # check for length, type, length
            # Typically this method is overridden by derived classes

            self.is_replied = True
            is_reply_valid = False
            answer = self.get_reply().get_answer()
            limits = self.get_limits()

            if answer is not None:
                if self.get_reply_type() in [ReplyType.TEXT, ReplyType.NOTE]:
                    if isinstance(answer, str):
                        is_reply_valid = True
                elif self.get_reply_type() == ReplyType.INTEGER:
                    try:
                        int(answer)
                        is_reply_valid = True
                    except:
                        is_reply_valid = False
                elif self.get_reply_type() == ReplyType.INPUTMODE:
                    if isinstance(answer, InputMode) or isinstance(answer, str):
                        is_reply_valid = True
                else:
                    is_reply_valid = True

                if self.get_reply_type() == ReplyType.INTEGER and limits is not None and is_reply_valid is True:
                    try:
                        num = int(answer)
                        low_lim = min(limits)
                        high_lim = max(limits)
                        if num >= low_lim and num <= high_lim:
                            is_reply_valid = True
                        else:
                            is_reply_valid = False
                    except (ValueError, TypeError):
                        pass

            return is_reply_valid

    def check_prerequisites(self):

        pre = self.get_prerequisites()
        if len(pre) == 0:
            satisfied = True
        else:
            satisfied = all([q.get_reply_validity() for q in pre])

        return satisfied

    def build_result(self):
        """
        The result is the complete query, with foreword, afterword, et caetera
        """
        result = [self.get_foreword()]
        result += [self.get_question()]
        result += [self.get_afterword()]
        result = '\n'.join(filter(None, result))
        self.result = result
        return result  # Generic return, will be overridden in derived classes

    def hash_identifier(self):
        """
        Builds an ID of the Query. Two queries with the same ID are considered as duplicates. 
        """
        hashables = [self.get_sender(), self.get_recipient(), self.get_result(), self.get_limits(),
                     self.get_prerequisites()]
        hashables = [str(hashable).lower().strip() for hashable in hashables]
        self.identifier = hash(','.join(hashables))

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
        if self.is_replied:
            if self.reply.check_reply():
                raise QueryRepliedError('this question has already been correctly answered')
        self.check_and_pack()
        self.stamp()
        self.is_sent = True
        # TODO: decide whether asking again resets the question to unreplied to (as here)

        self.is_replied = False

        if recipient is None:
            recipient = self.get_recipient()

        recipient.receive(self)  # Assumes that all recipients contain a method to handle queries

        return self.is_sent

    def reply_to(self, answer):
        """
        Assigns a Reply to the Query
        """
        # if self.expect_reply is False:
        #    raise InvalidReplyError('This Query doesnt expect a Reply')

        self.reply = Reply(self, answer)
        self.reply.build_result()
        self.reply.get_validity()
        pre_satisfied = self.check_prerequisites()
        if not pre_satisfied:
            raise InvalidReplyError('This Query requires other queries to be satisfied first.')
        # is_reply_valid = self.get_reply_validity()

        # self.is_replied = True
        # TODO: decide if is_replied must be set to False of the reply is invalid.
        return self.reply


class QueryChoice(Query):
    """
    Query with multiple choices, defined in self.limits
    """

    def __init__(self, *args, **kwargs):

        try:
            kwargs['limits'][0]
        except (TypeError, IndexError, KeyError):
            raise InvalidQueryError('QueryChoice called with no choices')

        super().__init__(*args, **kwargs)

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

        self.result = result

        return result

    def check_reply(self):

        # Performs basic checking against ReplyType
        is_reply_valid = super().check_reply()

        if is_reply_valid is not True:
            return is_reply_valid

        answer_index = self.get_answer_index()

        if answer_index is None:
            is_reply_valid = False
        else:
            is_reply_valid = True

        return is_reply_valid

    def get_answer_index(self):

        answer = self.reply.get_answer()
        choices = self.get_limits()

        if isinstance(answer, str):
            answer = answer.lower().strip()
        if isinstance(choices[0], str):
            choices = [c.lower().strip() for c in choices]

        try:
            index = choices.index(answer)
        except ValueError:
            try:  # Maybe answer is the choice index (0-n)
                index = int(answer)
                if index < 0 or index > len(choices):
                    index = None
            except (ValueError, IndexError, TypeError):
                index = None

        return index


class QueryBoolean(QueryChoice):
    """
    A yes/no, true/false question type
    """

    def __init__(self, *args, **kwargs):
        # repairing missing choices
        self.default_limits = ['y', 'n']
        try:
            kwargs['limits'][0]
            kwargs['limits'][1]
            if len(kwargs['limits']) != 2:
                kwargs['limits'] = self.default_limits
        # TODO: decide whether we want to repair limits only if len()!=2, or also if len() is odd (then treat each 2
        #  limits as a possible yes/no couple), or raise an error
        except:
            kwargs['limits'] = self.default_limits
        super().__init__(*args, **kwargs)

    def build_result(self):

        result = []

        result += [self.get_foreword()]
        result += [self.get_question() + ' (' + (self.get_limits()[0] +
                                                 '/' + self.get_limits()[1]) + ')']
        result += [self.get_afterword()]
        result = '\n'.join(filter(None, result))
        self.result = result
        return result


class QueryOpen(Query):
    """
    An open-ended Query,
    excepted that a string answer can be checked against a regular expression in self.limits
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def check_reply(self):

        is_reply_valid = super().check_reply()

        if is_reply_valid is not True:
            return is_reply_valid

        try:
            match = re.search(self.get_limits(), self.reply.get_answer())
            if match is None:
                is_reply_valid = False
        except TypeError:
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
    Storage for Queries.
    With function to recall and erase Queries by type, property...
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
            'valid_reply': lambda q: q.get_reply_validity(), 'invalid_reply': lambda q: not q.get_reply_validity(),
            'from_me': lambda q: q.get_sender() == self.owner,
            'to_me': lambda q: q.get_recipient() == self.owner,
            'information': lambda q: not q.expect_reply(),
            'query': lambda q: q.expect_reply(),
        }

    def __str__(self):

        string = '<' + self.__class__.__name__
        if self.topic is not None:
            string += ' about ' + repr(self.topic)
        string += ' with ' + str(
            len(self.queries)) + ' stored queries>'
        return string

    def __len__(self):

        return len(self.queries)

    def print_out(self, filters=None, criterion=None):

        print(self)
        for i, q in enumerate(self.recall(filters=filters, criterion=criterion)):
            print('----query#' + str(i) + '----')
            print(q)
            print('---------------')

    # TODO: add a specific recall for information objects expect_reply = false

    def recall_filtered(self, filters=None):

        if filters is None:
            return self.queries
        else:
            queries = self.queries
            if not isinstance(filters, (list, tuple, set)):
                filters = [filters]
            for k in filters:
                queries = filter(self.query_filters[k], queries)
        return list(queries)

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
        '''
        Recalls the first query. If a topological sort has been made, it is the first one to be answered
        '''
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

    def recall_by_identifier(self, identifier, filters=None):
        """
        Recalls Queries with the given identifier
        """
        queries = self.recall_filtered(filters)
        return [q for q in queries if q.get_identifier() == identifier]

    def recall_by_sender(self, sender, filters=None):
        queries = self.recall_filtered(filters)
        return [q for q in queries if q.get_sender() == sender]

    def recall_by_recipient(self, recipient, filters=None):
        queries = self.recall_filtered(filters)
        return [q for q in queries if q.get_recipient() == sender]

    def has_query(self, criterion=None, filters=None):
        return len(self.recall(criterion=criterion, filters=filters) > 0)

    def recall_information(self, filters=None):

        queries = self.recall_filtered(filters)
        return [q for q in queries if q.get_expect_reply() == False]

    def recall(self, criterion=None, filters=None):
        """
        Recalls Queries matching criterion, which can be a list index, a string to be searched, or a Query identifier
        """
        queries = self.recall_filtered(filters)

        if criterion is None or criterion == '':
            return queries

        q_found = []
        if isinstance(criterion, int):
            try:
                q_found = queries[criterion]  # Maybe criterion is an index
            except IndexError:
                q_found = self.recall_by_identifier(criterion)  # Maybe criterion is an identifier
        elif isinstance(criterion, Query):  # Maybe criterion is a Query
            if criterion in queries:
                q_found.append(criterion)
        else:
            for q in queries:  # Maybe criterion is an attribute, some text for instance
                attr_vals = list(q.__dict__.values())
                if criterion in attr_vals:
                    q_found += [q]

        return q_found

    def recall_unsent(self, filters=None):
        queries = self.recall_filtered(filters)
        return [q for q in queries if q.get_is_sent() == False]

    def recall_replied(self, filters=None):
        queries = self.recall_filtered(filters)
        return [q for q in queries if q.get_is_replied()]

    def recall_unreplied(self, filters=None):
        queries = self.recall_filtered(filters)
        return [q for q in queries if not q.get_is_replied()]

    def recall_by_invalid_reply(self, filters=None):
        q_replied = self.recall_replied(filters=filters)
        return [q for q in q_replied if not q.reply.get_validity()]

    def recall_unsatisfied(self, filters=None):
        queries = self.recall_filtered(filters)
        return [q for q in queries if (not q.get_is_replied() or not q.get_reply_validity())]

    def recall_repeated(self, filters=None):
        """
        Recall queries that have been stored twice or more
        TODO: decide if we check for is_sent
        """
        queries = self.recall_filtered(filters)

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

        # print(self)
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

    def erase(self, filters=None, criterion=None):
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
        Sort queries by sent date
        """
        self.queries = sorted(self.queries, key=Query.get_sent_time)
        return self.queries

    def topological_sort(self):
        """
        Sort Queries by solving dependencies
        """
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
