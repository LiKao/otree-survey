from django.utils.safestring import mark_safe
from django.utils.html import format_html

from .ChoiceQuestion import ChoiceQuestion

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
            if choice.default:
                default = "checked"

            # freetext = ""
            # if choice.has_freetext():
            #     freetext = format_html('data-freetext="{}"', choice.id)

            output.append( format_html('<input type="radio" name="{}" value="{}" id="{}" {} {}>', 
                            self._radioq.question.variable, choice.value, idstr, default, self._required) )
            output.append( format_html('<label for="{}">{}</label><br>', idstr, choice.text))

        # for choice in self._radioq:
        #     if choice.has_freetext():
        #         output.append( format_html('<div id="freetext_{}" class="collapse">', choice.id))
        #         output.append( format_html('<label for="freetext_{}_fld">{}</label>', choice.id, choice.freetext) )
        #         output.append( format_html('<input type="text" name="{}_freetext[]" id="freetext_{}_fld"><br>', 
        #                         self._radioq.question.variable, choice.id))
        #         output.append("</div>")


        return mark_safe("\n".join(output))

class RadioQuestion(ChoiceQuestion):
    def __init__(self, question):
        super(RadioQuestion, self).__init__( question )

    def as_form(self, required=""):
        return RadioForm( self, required=required)