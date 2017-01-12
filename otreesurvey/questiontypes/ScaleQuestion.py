from django.utils.safestring import mark_safe
from django.utils.html import format_html

from .QuestionType import QuestionType

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
    def __init__(self, question):
        super(ScaleQuestion, self).__init__( question )
        self._left      = ""
        self._right     = ""
        self._points    = 7

    @property
    def left(self):
        return self._left

    @left.setter
    def left(self, value):
        self._left = value

    @property
    def right(self):
        return self._right

    @right.setter
    def right(self, value):
        self._right = value

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, value):
        if value < 3:
            raise ValueError("Number of points for likert scale less than 3")
        self._points = value


    def parseXml(self, xml):
        self.left   = xml.findtext("left", "")
        self.right  = xml.findtext("right", "")
        if "points" in xml.attrib:
            self.points = int( xml.get("points") )

    def __len__(self):
        return self.points

    def as_form(self, required=""):
        return ScaleForm( self, required=required )