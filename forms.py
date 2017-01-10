from django import forms
from django.utils.safestring import mark_safe
from django.utils.html import format_html

import logging
logger = logging.getLogger(__name__)

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

class TextForm(object):
	def __init__(self, textq, required):
		self._textq = textq
		self._required = required

	def __str__(self):
		output = []
		output.append( format_html('<input type="text" name="{}" {}><br>', self._textq.question.variable, self._required))
		return mark_safe("\n".join(output))
		

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
