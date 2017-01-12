from django.utils.safestring import mark_safe
from django.utils.html import format_html

from .ChoiceQuestion import ChoiceQuestion

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
			if choice.default:
				default = "checked"

			# freetext = ""
			# if choice.has_freetext():
			# 	freetext = format_html('data-freetext="{}"', choice.id)

			output.append( format_html('<input type="checkbox" name="{}" value="{}" id="{}" {}>', 
							self._buttonq.question.variable, choice.value, idstr, default) )
			output.append( format_html('<label for="{}">{}</label><br>', idstr, choice.text))

		# for choice in self._buttonq:
		# 	if choice.has_freetext():
		# 		output.append( format_html('<div id="freetext_{}" class="collapse">', choice.id))
		# 		output.append( format_html('<label for="freetext_{}_fld">{}</label>', choice.id, choice.freetext) )
		# 		output.append( format_html('<input type="text" name="{}_freetext[]" id="freetext_{}_fld"><br>', 
		# 						self._buttonq.question.variable, choice.id))
		# 		output.append( "</div>")

		return mark_safe("\n".join(output))
        
class ButtonQuestion(ChoiceQuestion):
    def __init__(self, question):
        super(ButtonQuestion, self).__init__( question )

    def as_form(self, required=""):
        return ButtonForm( self, required=required )
