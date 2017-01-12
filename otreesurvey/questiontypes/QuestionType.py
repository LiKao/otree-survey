class QuestionTypeUndefined(KeyError):
    def __init__(self, qtype):
        super(QuestionTypeUndefined, self).__init__( qtype )
        self._type = qtype

    @property
    def type(self):
        return self._type


class QuestionType(object):
    """Base class for all types of questions.
    Types are added to Question objects, to define what kind of data is
    accepted and how the question should be displayed.

    QuestionTypes can define new methods, that will be made accessible from
    the wrapping Question object"""

    # Global registry for all kinds of types that are defined
    types_registry = {}

    def __init__(self, question):
        self._question = question

    def as_form(self, required=""):
        raise NotImplementedError("Method as_form not defined for question of type %s " % self.question.type)

    @property
    def question(self):
        return self._question

    @classmethod
    def register(cls, key, qtype):
        cls.types_registry[key] = qtype

    @classmethod
    def create(cls, key, question):
        if key not in cls.types_registry:
            raise QuestionTypeUndefined(key)
        return cls.types_registry[key]( question )