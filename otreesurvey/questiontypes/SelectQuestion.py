from django.utils.safestring import mark_safe
from django.utils.html import format_html

from .ChoiceQuestion import ChoiceQuestion

class SelectForm(object):
	def __init__(self, selectq, required=""):
		self._selectq = selectq
		self._required = required

	def __str__(self):
		output = []
		output.append( format_html('<select name="{}" {}>', self._selectq.question.variable, self._required))
		if not self._selectq.has_default:
			output.append('<option disabled selected value></option>')
		for choice in self._selectq:
			default = ""
			if choice.default:
				default = "selected"

			# freetext = ""
			# if choice.has_freetext():
			# 	freetext = format_html('data-freetext="{}"', choice.id)
			output.append( format_html('<option value="{}" {} >{}</option>', choice.value, default, choice.text) )
		output.append("</select>")

		# for choice in self._selectq:
		# 	if choice.has_freetext():
		# 		output.append( format_html('<div id="freetext_{}" class="collapse">', choice.id))
		# 		output.append( format_html('<label for="freetext_{}_fld">{}</label>', choice.id, choice.freetext) )
		# 		output.append( format_html('<input type="text" name="{}_freetext[]" id="freetext_{}_fld"><br>', 
		# 						self._selectq.question.variable, choice.id))
		# 		output.append( "</div>")
				

		return mark_safe("\n".join(output))

class SelectQuestion(ChoiceQuestion):
    def __init__(self, question):
        super(SelectQuestion, self).__init__( question )

    def as_form(self, required=""):
        return SelectForm( self, required=required )