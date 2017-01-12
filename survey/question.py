from django import forms
from django.utils.safestring import mark_safe
from django.utils.html import format_html

from django.core.exceptions import ImproperlyConfigured

from uuid import uuid4

import logging
logger = logging.getLogger(__name__)

class QuestionType(object):
    def __init__(self, qdef, question):
        self._question = question

    def as_form(self, required=""):
        raise NotImplementedError("Method as_form not defined for question of type %s " % self.question.type)

    @property
    def question(self):
        return self._question


class Choice(object):
    def __init__(self, cdef):
        if "value" not in cdef.attrib:
            raise ImproperlyConfigured("Value for choice missing in definitaion at lines %d-%d" %(cdef.start_line_number, qdef.end_line_number))
        self._value=cdef.get("value")
        self._text =cdef.text
        self._id   = uuid4().hex
        if "default" in cdef.attrib:
            logger.info("Default value: %s" % self._value)
            self._default = bool(cdef.get("default"))
        else:
            self._default = False

        if "freetext" in cdef.attrib:
            self._freetext = str(cdef.get( "freetext" ))
            if self._freetext == "":
                self._freetext = self.text + ":"
        else:
            self._freetext = None

    @property
    def id(self):
        return self._id

    @property
    def value(self):
        return self._value

    @property
    def text(self):
        return self._text

    def has_freetext(self):
        return self._freetext is not None

    @property
    def freetext(self):
        return self._freetext

    def default(self):
        return self._default



class ChoiceQuestion(QuestionType):
    def __init__(self, qdef, question):
        self._choices   = [Choice(c) for c in  qdef.iterfind("choice")]
        if len(self._choices) > 0:
            self._has_default = max([c.default() for c in self._choices])
        else:
            self._has_default = False

        logger.info("Question has default: %s" % self._has_default)

        super(ChoiceQuestion, self).__init__(qdef, question)

    def __getitem__(self, i):
        return self._choices[ i ]

    def __iter__(self):
        return self._choices.__iter__()

    def has_default(self):
        return self._has_default


class RadioForm(object):
	def __init__(self, radioq, required=""):
		self._radioq = radioq
		self._required = required

	def __str__(self):
		output = []
		idn = 0
		for choice in self._radioq:
			idn = idn + 1
			idstr = "%s_%d" %(self._radioq.question.variable, idn)
			default = ""
			if choice.default():
				default = "checked"

			freetext = ""
			if choice.has_freetext():
				freetext = format_html('data-freetext="{}"', choice.id)

			output.append( format_html('<input type="radio" name="{}" value="{}" id="{}" {} {} {}>', 
							self._radioq.question.variable, choice.value, idstr, default, self._required, freetext) )
			output.append( format_html('<label for="{}">{}</label><br>', idstr, choice.text))

		for choice in self._radioq:
			if choice.has_freetext():
				output.append( format_html('<div id="freetext_{}" class="collapse">', choice.id))
				output.append( format_html('<label for="freetext_{}_fld">{}</label>', choice.id, choice.freetext) )
				output.append( format_html('<input type="text" name="{}_freetext[]" id="freetext_{}_fld"><br>', 
								self._radioq.question.variable, choice.id))
				output.append("</div>")


		return mark_safe("\n".join(output))

class RadioQuestion(ChoiceQuestion):
    def __init__(self, qdef, question):
        super(RadioQuestion, self).__init__( qdef, question )

    def as_form(self, required=""):
        return forms.RadioForm( self, required=required)


class SelectForm(object):
	def __init__(self, selectq, required=""):
		self._selectq = selectq
		self._required = required

	def __str__(self):
		output = []
		output.append( format_html('<select name="{}" {}>', self._selectq.question.variable, self._required))
		if not self._selectq.has_default():
			output.append('<option disabled selected value></option>')
		for choice in self._selectq:
			default = ""
			if choice.default():
				default = "selected"

			freetext = ""
			if choice.has_freetext():
				freetext = format_html('data-freetext="{}"', choice.id)
			output.append( format_html('<option value="{}" {} {}>{}</option>', choice.value, default, freetext, choice.text) )
		output.append("</select>")

		for choice in self._selectq:
			if choice.has_freetext():
				output.append( format_html('<div id="freetext_{}" class="collapse">', choice.id))
				output.append( format_html('<label for="freetext_{}_fld">{}</label>', choice.id, choice.freetext) )
				output.append( format_html('<input type="text" name="{}_freetext[]" id="freetext_{}_fld"><br>', 
								self._selectq.question.variable, choice.id))
				output.append( "</div>")
				

		return mark_safe("\n".join(output))

class SelectQuestion(ChoiceQuestion):
    def __init__(self, qdef, question):
        super(SelectQuestion, self).__init__( qdef, question )

    def as_form(self, required=""):
        return forms.SelectForm( self, required=required )

class ButtonForm(object):
	def __init__(self, buttonq, required=""):
		self._buttonq  = buttonq
		self._required = required

	def __str__(self):
		output = []
		idn = 0
		for choice in self._buttonq:
			idn = idn + 1
			idstr = "%s_%d" %(self._buttonq.question.variable, idn)
			default = ""
			if choice.default():
				default = "checked"

			freetext = ""
			if choice.has_freetext():
				freetext = format_html('data-freetext="{}"', choice.id)

			output.append( format_html('<input type="checkbox" name="{}" value="{}" id="{}" {} {}>', 
							self._buttonq.question.variable, choice.value, idstr, default, freetext) )
			output.append( format_html('<label for="{}">{}</label><br>', idstr, choice.text))

		for choice in self._buttonq:
			if choice.has_freetext():
				output.append( format_html('<div id="freetext_{}" class="collapse">', choice.id))
				output.append( format_html('<label for="freetext_{}_fld">{}</label>', choice.id, choice.freetext) )
				output.append( format_html('<input type="text" name="{}_freetext[]" id="freetext_{}_fld"><br>', 
								self._buttonq.question.variable, choice.id))
				output.append( "</div>")

		return mark_safe("\n".join(output))
        
class ButtonQuestion(ChoiceQuestion):
    def __init__(self, qdef, question):
        super(ButtonQuestion, self).__init__( qdef, question )

    def as_form(self, required=""):
        return forms.ButtonForm( self, required=required )


class ScaleForm(object):
	def __init__(self, scaleq, required):
		self._scaleq  = scaleq
		self._required = required

	def __str__(self):
		output = []
		# Table definition
		output.append('<table class="likert">')
		# Header / Anchors
		output.append("<tr>")
		output.append( format_html("<th>{}</th>", self._scaleq.left))
		for i in range( len(self._scaleq) - 2 ):
			output.append("<th></th>")
		output.append( format_html("<th>{}</th>", self._scaleq.right))
		output.append("</tr>")

		# Actual scale
		output.append("<tr>")
		for i in range( len(self._scaleq) ):
			output.append( format_html('<td><input type="radio" name="{}" value="{}" {}></td>', self._scaleq.question.variable, i+1, self._required))
		output.append("</tr>")

		output.append("</table>")
		return mark_safe("\n".join(output))       

class ScaleQuestion(QuestionType):
    def __init__(self, qdef, question):
        super(ScaleQuestion, self).__init__( qdef, question )
        self._left = qdef.find("left").text
        self._right = qdef.find("right").text

        if "points" in qdef.attrib:
            self._points = int( qdef.get("points") )
        else:
            self._points = 7

        if self._points < 3:
            raise ImproperlyConfigured("Number of points for Likert scale less than three")

    @property
    def left(self):
        return self._left

    @property
    def right(self):
        return self._right

    @property
    def points(self):
        return self._points

    def __len__(self):
        return self.points

    def as_form(self, required=""):
        return forms.ScaleForm( self, required=required )


class TextForm(object):
	def __init__(self, textq, required):
		self._textq = textq
		self._required = required

	def __str__(self):
		output = []
		output.append( format_html('<input type="text" name="{}" {}><br>', self._textq.question.variable, self._required))
		return mark_safe("\n".join(output))

class TextQuestion(QuestionType):
    def __init__(self,qdef, question):
        super(TextQuestion, self).__init__( qdef, question )

    def as_form(self, required=""):
        return forms.TextForm( self, required=required )


class QuestionForm(object):
	def __init__(self, question):
		self._question = question

	@property
	def question(self):
		return self._question

	def _required(self):
		if self.question.optional:
			return ""
		else:
			return "required"

	def _html_out(self):
		output = []
		output.append('<div class="question">')
		output.append(format_html("<h4>{}</h4>", self.question.text))

		if self.question.has_note():
			output.append(format_html("<span>{}</span><br>", self.question.note))
		output.append('<div class="question_content">')
		output.append(self.question.as_form( required=self._required() ))
		output.append("</div>")
		output.append("</div>")

		return mark_safe("\n".join( output ))

	def __str__(self):
		return self._html_out()

class Question(object):
    def __init__(self, qdef):
        if "variable" not in qdef.attrib:
            raise ImproperlyConfigured("Question is missing variable definition in lines %d-%d" %(qdef.start_line_number, qdef.end_line_number) )
        self._variable  = qdef.get("variable")
        self._type      = qdef.tag.lower()
        self._text      = qdef.find("text").text
        self.make_type( qdef )
        
        if qdef.find("note") is not None:
            self._note      = qdef.find("note").text
        else:
            self._note      = None

        if "optional" in qdef.attrib:
            self._optional = bool(qdef.get("optional"))
        else:
            self._optional = False
        logger.info("Creating question %s of type %s" % (self.variable,self.type))

    def _make_type_textfield(self, qdef):
        return TextQuestion(qdef, self)

    def _make_type_scale(self, qdef):
        return ScaleQuestion(qdef, self)

    def _make_type_button(self, qdef):
        return ButtonQuestion(qdef, self)

    def _make_type_radio(self, qdef):
        return RadioQuestion(qdef, self)

    def _make_type_selection(self, qdef):
        return SelectQuestion(qdef, self)

    def _make_type_default(self, qdef):
        raise ImproperlyConfigured("Question type %s not defined" % self.type)

    def make_type(self, qdef):
        self._qtype = getattr(self,"_make_type_%s"%(self.type), self._make_type_default)( qdef )

    def as_form(self, required=""):
        return str( self._qtype.as_form( required=required ) )

    @property
    def variable(self):
        return self._variable

    @property
    def type(self):
        return self._type

    @property
    def text(self):
        return self._text

    def has_note(self):
        return self._note is not None

    @property
    def note(self):
        return self._note

    @property
    def optional(self):
        return self._optional

    def __str__(self):
        return self._variable

    def as_p(self):
        return forms.QuestionForm(self)