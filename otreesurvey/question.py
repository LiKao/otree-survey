from .questiontypes import QuestionType
from .questiontypes import QuestionTypeUndefined

from django.utils.safestring import mark_safe
from django.utils.html import format_html

from django.core.exceptions import ImproperlyConfigured

from uuid import uuid4

import logging
logger = logging.getLogger(__name__)

class QuestionForm(object):
    def __init__(self, question):
        self._question = question

    @property
    def question(self):
        return self._question

    def _html_out(self):
        output = []
        output.append('<div class="question">')
        output.append(format_html("<h4>{}</h4>", self.question.text))

        if self.question.has_note():
            output.append(format_html("<span>{}</span><br>", self.question.note))
        output.append('<div class="question_content">')
        output.append(self.question.render_question())
        output.append("</div>")
        output.append("</div>")

        return mark_safe("\n".join( output ))

    def __str__(self):
        return self._html_out()

class Question(object):
    def __init__(self, variable, qtype, text, note = None, optional = False):
        self._variable      = variable
        self._type          = qtype
        self._text          = text
        self._note          = note
        self._optional      = optional
        self._typehandler   = QuestionType.create( self.type, self )
  
    def render_question(self):
        if self._optional:
            required = ""
        else:
            required = "required"

        return str( self.typehandler.as_form( required ) )

    @property
    def variable(self):
        return self._variable

    @property
    def type(self):
        return self._type

    @property
    def typehandler(self):
        return self._typehandler

    @property
    def text(self):
        return self._text

    def has_note(self):
        return self._note is not None

    @property
    def note(self):
        return self._note

    @note.setter
    def note(self, value):
        self._note = value

    @property
    def optional(self):
        return self._optional

    @optional.setter
    def optional(self, value):
        self._optional = value

    def __str__(self):
        return self._variable

    def as_p(self):
        return QuestionForm(self)

def questionFromXml(xml):
    if "variable" not in xml.attrib:
            raise ImproperlyConfigured("Question is missing variable definition in lines %d-%d" %(xml.start_line_number, xml.end_line_number) )

    variable    = xml.get("variable")
    qtype       = xml.tag.lower()
    text        = xml.findtext("text")

    if text is None:
        raise ImproperlyConfigured("No text for Question definition in lines %d-%d" %(xml.start_line_number, xml.end_line_number) )

    note        = xml.findtext("note")
    optional    = bool(xml.findtext("optional", False))

    try:
        rv = Question(variable, qtype, text, note, optional)
    except QuestionTypeUndefined as e:
        raise ImproperlyConfigured('Question type "%s" not defined in lines %d-%d' %(e.type, xml.start_line_number, xml.end_line_number))

    rv.typehandler.parseXml( xml )

    return rv
