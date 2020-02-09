from question import QuestionError, Question


class InvalidAnswerError(QuestionError):
    pass


class Answer:

    def __init__(self, question):

        self.question = question  # the Question object this Answer responds to
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
        if self.isvalid is None:
            self.isvalid = self.check_answer()
        return self.isvalid

    def check_answer(self):
        """
        Only the Question can tell if the answer is valid.
        """
        self.isvalid = self.question.check_answer()
        return self.isvalid
