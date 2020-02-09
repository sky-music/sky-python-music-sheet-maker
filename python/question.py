'''
Classes to ask and answer questions between the bot and the music cog.
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

'''

from modes import QuestionType

class QuestionError(Exception):
    def __init__(self, explanation):
        self.explanation = explanation

    def __str__(self):
        return str(self.explanation)

    pass


class InvalidQuestionError(QuestionError):
    pass
    
class InvalidAnswerError(QuestionError):
    pass

class Answer():
	
	def __init__(self, question):
		
		self.question = question # the Question object this Answer responds to
		self.answer = None
		self.isvalid = None
		if not isinstance(question, Question):
			raise InvalidAnswerError('this answer has no question.')
		
	def get_answer(self):
		if self.isvalid:
			return self.answer
		else:
			return None
		
	def set_answer(self, answer):
		self.answer = answer
		
	def get_validity(self):
		if self.isvalid == None:
			self.isvalid = self.check_answer()
		return self.isvalid
		
	def check_answer(self):
		"""
		Only the Question can tell if the answer is valid.
		"""
		self.isvalid = self.question.check_answer()
		return self.isvalid

class Question:

    def __init__(self, sender=None, recipient=None, question=None, information_before=None, information_after=None,
                 choices=None):
        """
        A question object

        Choices are for questions where the user chooses from multiple choices
        """
        '''
        TO-DOs:
        a question is a request for information
        it has one or several formulations
        it has one or several possible answers
        it is repeated (or not) after a given time if no answer is given
        it is repeated (or not) if a blank answer is given
        for some questions there is a default answer (yes/no questions, and choice within a set, eg song key), for other not (open questions, such as “composer name”)
        a question has an “answered”/“not answered” status
        “answer” could be a property of question or a separate object
        the internal answer can be different from the answer you give out (for instance, the answer to ‘what is the song key?’ can be C, but you give the answer 'do' instead).
        etc
        '''
        self.sender = sender
        self.recipient = recipient
        self.question = question
        self.information_before = information_before
        self.information_after = information_after
        self.choices = choices

        '''
        TODO: decide how to check for sender and recipient types:
            - by checking the class of the sender object
            - by comparing sender to a list of strings, so the sender must send an identification string 
            - by asking the send back who is his (eg sender.get_type(), if such a property exist)
            => the choice will depend on the bot structure (since we can do whatever we want with music cog)
            => a possibility is to check first if the sender is music cog, and if not (AttributeError), then it is the bot
        '''
        self.valid_locutors = ['bot', 'music-cog']

        self.answer = None

        self.sender_type = None
        self.recipient_type = None
        self.type = None  # Yes/no, list of choices, open-ended — from QuestionType # Overidden by the derived classes
        self.depends_on = []  # A list of other Questions objects (or class types?) that this depends on
        # TODO: decide how depends_on will be set
        self.is_asked = False
        self.is_answer_valid = None
        self.is_answered = False

    def get_sender(self):
        return self.sender

    def get_recipient(self):
        return self.recipient

    def get_question(self):
        return self.question

    def get_answer(self):
        return self.answer

    def get_information_before(self):
        return self.information_before

    def get_information_after(self):
        return self.information_after

    def get_choices(self):
        return self.choices

    def get_is_answered(self):
        return self.is_answered

    def check_sender(self):
        if self.sender is not None:
            # TODO: more elaborate checking
            # if isinstance(self.sender, bot) or ...
            if not type(self.sender) == type(self.valid_locutors[0]):
                raise InvalidQuestionError(
                    'invalid sender. It must be a ' + type(self.valid_locutors[0]) + ' among ' + str(
                        self.valid_locutors))
            else:
                if self.sender in self.valid_locutors:
                    return True
        else:
            raise InvalidQuestionError('invalid sender. Sender is ' + str(self.sender))

    def check_recipient(self):
        if self.recipient is not None:
            # TODO: more elaborate checking
            if self.recipient == self.sender:
                raise InvalidQuestionError('sender cannot ask a question to itself.')
            return True
        else:
            raise InvalidQuestionError('invalid recipient. Recipient is ' + str(self.recipient))

    def check_question(self):
        if self.question is not None:
            # TODO: add checking among more types, if needed
            if isinstance(self.question, str):
                return True
            else:
                raise InvalidQuestionError('only string (str) question are allowed at the moment.')
        else:
            raise InvalidQuestionError('question is undefined.')

    def check_answer(self):
        if isinstance(self.answer, Answer):
            # TODO: add checks for testing the validity of the answer
            # for instance, if a music key is expected, check that it belongs to a dictionary
            # check for length, type, length
            # Typically this method is overridden by derived classes
            self.is_answered = True
            
            if self.answer.get_answer() is not None:
                self.is_answer_valid = True
            else:
                self.is_answer_valid = False
        else:
             self.is_answered = False
        return self.is_answer_valid

    def build_question(self):

        return self.get_question()  # Generic return, will be overridden in derived classes

    def ask(self):
        """
            Asking is a protocol during which you first check that you are allowed to speak, that
            there is someone to listen, that your question is meaningful (or allowed)
            and then you can ask it
        """
        self.check_sender()
        self.check_recipient()
        self.check_question()

        self.is_asked = True
        self.is_answered = False  # TODO: decide whether asking again resets the question to unanswered (as here)

        self.build_question()

        return self.get_question()

    def give_answer(self, answer):
        self.answer = answer
        is_answer_valid = self.check_answer()
        if is_answer_valid is not None:
            self.is_answered = True
        # TODO: decide if is_answered must be set to False of the answer is invalid.
        return self.get_information_after()


class QuestionText(Question):
    """
        A class in which both the question and the answer are strings (including numbers parsed as text)
    """

    def check_question(self):
        if self.question_string is not None:
            if isinstance(self.question_string, str):
                return True
            else:
                raise InvalidQuestionError(
                    'Invalid question type. ' + type(self.question_string) + ' was given, str was expected.')
        else:
            raise InvalidQuestionError('Undefined question.')

    def check_answer(self):
        if self.answer is not None:
            if isinstance(self.answer, str):
                return True
            else:
                raise InvalidQuestionError(
                    'Invalid answer type. ' + type(self.answer) + ' was given, str was expected.')

    def build_question(self):

        self.question = self.get_information_before()

        if self.get_choices() is not None:
            self.question += '\n'

        for i, choice in enumerate(self.get_choices()):
            self.question += str(i) + ') '
            self.question += choice + '\n'

        return self.question  # Generic return, will be overridden in derived classes


class QuestionChoice(Question):
    
    """
    Question with multiple choices
    """

    def build_question(self):

        self.question = self.get_information_before()

        if self.get_choices() is not None:
            self.question += '\n'

        for i, choice in enumerate(self.get_choices()):
            self.question += str(i) + ') '
            self.question += choice + '\n'

        return self.question  # Generic return, will be overridden in derived classes


class QuestionSongMetadata(QuestionText):
    """
        Metadata currently includes:
            - title
            - original artist
            - transcript writer

        This is an open question: the answer can be anything, provided it is a string.
    """

    def __init__(self, **kwargs):
        super().__init__()

        self.type = QuestionType.OPEN
        self.choices = None  # choices are ignored


class QuestionSongNotation(QuestionText):
    """
        Song notation used by the player, defined by its name among a given list
    """

    def __init__(self, **kwargs):

        super().__init__()

        self.type = QuestionType.CHOICE

        try:
            self.choices[0]
        except (TypeError, IndexError):
            raise InvalidQuestionError('open question with no choices.')

    def check_answer(self):
        if self.answer is not None:
            if not isinstance(self.answer, str):
                raise InvalidQuestionError(
                    'Invalid answer type. ' + type(self.answer) + ' was given, str was expected.')
            else:
                if self.answer.lower() in [choice.lower() for choice in self.choices]:
                    return True
