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
		output.append( format_html('<input type="hidden" name="{}" value="[]" class="checkbox_input">', self._buttonq.question.variable) )
		output.append( format_html('<div id="checkboxes_{}">', self._buttonq.question.variable ))
		for idn, choice in enumerate( self._buttonq ):
			idstr = "%s_%d" %(self._buttonq.question.variable, idn)
			default = ""
			if choice.default:
				default = "checked"

			# freetext = ""
			# if choice.has_freetext():
			# 	freetext = format_html('data-freetext="{}"', choice.id)

			output.append( format_html('<input type="checkbox" name="{0}" value="{1}" id="{0}" {2}>', 
							idstr, choice.value, default) )
			output.append( format_html('<label for="{}">{}</label><br>', idstr, choice.text))
		output.append( '</div>' )

		output.append( '<script>' )
		output.append( """
			$("#checkboxes_{0} input").change(function(){{
				cval = new Set( JSON.parse( $("input[name='{0}']").val() ) );
				if( $(this).is(":checked") ) {{
					cval.add( $(this).attr("value") );
				}} else {{
					cval.delete( $(this).attr("value") );
				}}		
				$("input[name='{0}']").val( JSON.stringify( Array.from( cval ) ) ).change();
			}})""".format( self._buttonq.question.variable))
		output.append( '</script>' )

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
