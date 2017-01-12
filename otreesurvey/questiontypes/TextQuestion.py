from django.utils.safestring import mark_safe
from django.utils.html import format_html

from .QuestionType import QuestionType

class TextForm(object):
	def __init__(self, textq, required):
		self._textq = textq
		self._required = required

	def __str__(self):
		output = []
		output.append( format_html('<input type="text" name="{}" {}><br>', self._textq.question.variable, self._required))
		return mark_safe("\n".join(output))

class TextQuestion(QuestionType):
    def __init__(self, question):
        super(TextQuestion, self).__init__( question )

    def parseXml(self, xml):
    	pass

    def as_form(self, required=""):
        return TextForm( self, required=required )