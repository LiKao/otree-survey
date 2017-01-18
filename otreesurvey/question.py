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

    # Variable only gets the variable for
    # this one question for identification
    # purposes.
    # allVariables will both get the
    # variables for this question as well
    # as for any follow up question.
    def allVariables(self):
        rv = [ self.variable ]
        for fup in self.followups:
            for q in fup.questions:
                rv.extend( q.allVariables() )
        return rv


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
        logger.info('Adding followup for value "{}" on question "{}" '.format(followup.value, self.variable) )
        self._followups.append( followup )
        followup.setParent( self )

    @property
    def followups(self):
        return self._followups

    def __str__(self):
        return self._variable

    def as_p(self):
        return QuestionForm(self)

class Followup(object):
    def __init__(self, value):
        self._value     = value
        self._questions = []
        self._parent    = None
        self._id        = uuid4().hex

    def as_p(self):
        output = []
        output.append( format_html('<div class="followup" id="followup_{}" data-followup-variable="{}" >', self.id, self.parent.variable) )
        output.append( '<div class="collapse">')
        for question in self.questions:
            output.append( str(question.as_p()) )
        output.append( '</div>' )
        output.append( '</div>' )

        output.append( '<script>')
        output.append( """
            $("[name='{0}']").change(function(e){{
                div = $("#followup_{2}").children("div")
                
                activated = false
                if( $(this).is(".checkbox_input") ) {{
                     values = new Set( JSON.parse( $(this).val() ) );
                     activated = values.has( "{1}" );
                }} else {{
                    activated = $(this).val() == "{1}"
                }}

                if( activated ) {{
                    div.collapse("show");
                    // Check which ones we have to reactivate now.
                    div.find("[data-followup-required='{2}']").attr("required", true);
                }} else {{
                    div.collapse("hide");
                    // We are hiding it. We need to remove all required attributes.
                    // since we are not limiting the check to anything,
                    // this will both remove this one as well as all further
                    // followups
                    div.find("[required]").attr("required", false);
                }}
            }});""".format(self.parent.variable, self.value, self.id))

        output.append("""
            $(document).ready(function() {{
                div = $("#followup_{0}").children("div");
                // First call to collapse always shows (even if passed with option "hide")
                // unless toggle:false is set.
                // Set this attribute everywhere when the page is loaded.
                // See: https://github.com/twbs/bootstrap/issues/5859
                div.collapse( {{'toggle': false}});
                
                // Currently we assume that the fields are hidden
                // for these fields, there must not be any "required"
                // attribute, because participants cannot enter anything
                // here.
                requireds = div.find("[required]");
                // We need to know when we have to restore the "required"
                // attribute.
                // Since document.ready is called in order of registration,
                // all follow ups below this one will already have been
                // deleted. Therefore, we can just register this question
                // id as a trigger for reactivating the required attribute
                requireds.attr("data-followup-required", "{0}");
                requireds.attr("required", false);
            }});""".format( self.id ) )

        output.append( '</script>')

        return mark_safe("\n".join( output ))

    @property
    def questions(self):
        return self._questions

    def addQuestion(self, question):
        logger.info('Adding question "{}" on followup for value "{}"'.format(question.variable, self.value))
        self._questions.append(question)

    def setParent(self, question):
        self._parent = question

    @property
    def value(self):
        return self._value

    @property
    def id(self):
        return self._id

    @property
    def parent(self):
        return self._parent


def followupFromXml(xml):
    if "value" not in xml.attrib:
        raise ImproperlyConfigured("Follow up is missing value definition in lines %d-%d" %(xml.start_line_number, xml.end_line_number) )

    value = xml.get("value")
    rv = Followup( value )
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
