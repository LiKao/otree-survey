from django.utils.safestring import mark_safe
from django.utils.html import format_html

from .QuestionType import QuestionType

class TextForm(object):
	def __init__(self, textq, required):
		self._textq = textq
		self._required = required

	def __str__(self):
		output = []
		if self._textq.has_label():
			output.append( format_html('<label for="{}">{}</label>', self._textq.question.htmlid, self._textq.label) )

		output.append( format_html('<input type="text" name="{}" {} id="{}"><br>', self._textq.question.variable, self._required, self._textq.question.htmlid))
		return mark_safe("\n".join(output))

class TextQuestion(QuestionType):
    def __init__(self, question, label=None):
        super(TextQuestion, self).__init__( question )
        self._label = label

    @property
    def label(self):
    	return self._label

    @label.setter
    def label(self, value):
    	self._label = value

    def has_label(self):
    	return self._label is not None

    def parseXml(self, xml):
    	self.label = xml.findtext("label")

    def as_form(self, required=""):
        return TextForm( self, required=required )