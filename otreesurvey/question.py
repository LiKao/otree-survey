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
        if self.question.has_text():
            output.append(format_html("<h4>{}</h4>", self.question.text))

        if self.question.has_note():
            output.append(format_html("<span>{}</span><br>", self.question.note))
        output.append('<div class="question_content">')
        output.append(self.question.render_question())
        output.append("</div>")
        output.append("</div>")

        for q in self._question.followups:
            output.append( str(q.as_p()) )

        return mark_safe("\n".join( output ))

    def __str__(self):
        return self._html_out()

class Question(object):
    def __init__(self, variable, qtype, text = None, note = None, optional = False):
        self._variable      = variable
        self._type          = qtype
        self._text          = text
        self._note          = note
        self._optional      = optional
        self._typehandler   = QuestionType.create( self.type, self )
        self._htmlid        = None
        self._followups     = []
  
    def render_question(self):
        if self._optional:
            required = ""
        else:
            required = "required"

        return str( self.typehandler.as_form( required ) )

    @property
    def htmlid(self):
        if self._htmlid is None:
            return "question_" + self._variable
        else:
            return self._htmlid

    @htmlid.setter
    def htmlid(self, value):
        self._htmlid = value

    @property
    def variable(self):
        return self._variable

    @property
    def type(self):
        return self._type

    @property
    def typehandler(self):
        return self._typehandler

    def has_text(self):
        return self._text is not None

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value

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

    def addFollowup(self, followup):
        self._followups.append( followup )

    @property
    def followups(self):
        return self._followups

    def __str__(self):
        return self._variable

    def as_p(self):
        return QuestionForm(self)

class Followup(object):
    def __init__(self):
        self._questions = []

    def as_p(self):
        output = []
        output.append( '<div class="followup">' )
        output.append( '<div class="collapse">')
        for question in self._questions:
            output.append( str(question.as_p()) )
        output.append( '</div>' )
        output.append( '</div>' )

        return mark_safe("\n".join( output ))

    def addQuestion(self, question):
        self._questions.append(question)


def followupFromXml(xml):
    rv = Followup()
    for qdef in xml:
        rv.addQuestion( questionFromXml(qdef) )
    return rv

def questionFromXml(xml):
    if "variable" not in xml.attrib:
            raise ImproperlyConfigured("Question is missing variable definition in lines %d-%d" %(xml.start_line_number, xml.end_line_number) )

    variable    = xml.get("variable")
    qtype       = xml.tag.lower()
    text        = xml.findtext("text")
    note        = xml.findtext("note")
    optional    = bool(xml.findtext("optional", False))

    try:
        rv = Question(variable, qtype, text, note, optional)
    except QuestionTypeUndefined as e:
        raise ImproperlyConfigured('Question type "%s" not defined in lines %d-%d' %(e.type, xml.start_line_number, xml.end_line_number))
    
    for fdef in xml.iterfind("followup"):
        rv.addFollowup( followupFromXml(fdef) )

    rv.typehandler.parseXml( xml )

    return rv
