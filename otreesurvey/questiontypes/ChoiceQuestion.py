from django.core.exceptions import ImproperlyConfigured
from uuid import uuid4

from .QuestionType import QuestionType

class Choice(object):
    def __init__(self, text, value, question):
        self._id        = uuid4().hex
        self._text      = text
        self._value     = value
        self._question  = question

    @property
    def id(self):
        return self._id

    @property
    def value(self):
        return self._value

    @property
    def text(self):
        return self._text

    @property
    def question(self):
        return self._question

    @property
    def default(self):
        return self.question.has_default and self.question.default.id == self.id

class DuplicateDefault(Exception):
    pass



class ChoiceQuestion(QuestionType):
    """Base class for any type of question that allows a multiple choice selection"""

    class ChoiceIterator(object):
        def __init__(self, question):
            self._question  = question
            self._iter      = question._ids.__iter__()
        
        def __iter__(self):
            return self

        def __next__(self):
            idx = self._iter.__next__()
            return self._question._choices[ idx ]

    
    def __init__(self, question):
        super(ChoiceQuestion, self).__init__(question)
        self._ids           = []
        self._choices       = {}
        self._default       = None

    def addchoice(self, text, value, default=False):
        choice = Choice(text, value, self)

        if default:
            if self._default is not None:
                raise DuplicateDefault()
            self._default = choice.id

        self._ids.append(choice.id)
        self._choices[choice.id] = choice

    def parseXml(self, xml):
        for cdef in xml.find("choices").iterfind("choice"):
            if "value" not in cdef.attrib:
                raise ImproperlyConfigured("Value for choice missing in definitaion at lines %d-%d" %(cdef.start_line_number, cdef.end_line_number))
            
            value   = cdef.get("value")
            text    = cdef.text
            default = bool(cdef.get("default", default=False))

            try:
                self.addchoice(text, value, default)
            except DuplicateDefault:
                raise ImproperlyConfigured("Duplicate default value defined in lines %d-%d" %(cdef.start_line_number, cdef.end_line_number))

    def __getitem__(self, i):
        return self._choices[ self._ids[ i ] ]

    def __iter__(self):
        iter = ChoiceQuestion.ChoiceIterator( self )
        return iter.__iter__()

    @property
    def has_default(self):
        return self._default is not None

    @property
    def default(self):
        if not self.has_default:
            return None
        return self._choices[ self._default ]
