from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

from . import forms

from django.core.exceptions import ImproperlyConfigured

from uuid import uuid4

import logging

logger = logging.getLogger(__name__)

import os
dir_path = os.path.dirname(os.path.realpath(__file__))

author = 'Tillmann Nett'

doc = """
Simple app for collecting demographic data.

Definitions for demographic data are taken from a short XML file.
"""

### Read XML definitions:

import sys

# Taken from http://stackoverflow.com/questions/6949395/is-there-a-way-to-get-a-line-number-from-an-elementtree-element
#
# Force python XML parser not faster C accelerators
# because we can't hook the C implementation
sys.modules['_elementtree'] = None
import xml.etree.ElementTree as XML

# This extension of the XML-Parser allows us to retrieve the
# Line number from the elements for better error reporting
class LineNumberingParser(XML.XMLParser):
        def _start(self, *args, **kwargs):
                # Here we assume the default XML parser which is expat
                # and copy its element position attributes into output Elements
                element = super(self.__class__, self)._start(*args, **kwargs)
                element.start_line_number = self.parser.CurrentLineNumber
                element.start_column_number = self.parser.CurrentColumnNumber
                element.start_byte_index = self.parser.CurrentByteIndex
                return element

        def _end(self, *args, **kwargs):
                element = super(self.__class__, self)._end(*args, **kwargs)
                element.end_line_number = self.parser.CurrentLineNumber
                element.end_column_number = self.parser.CurrentColumnNumber
                element.end_byte_index = self.parser.CurrentByteIndex
                return element

def XmlParse(filename):
    logger.info("Reading XML File %s" % filename)
    return XML.parse(filename, parser=LineNumberingParser())

pdefs = XmlParse(dir_path + "/Questionaire.xml")

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

class QuestionType(object):
    def __init__(self, qdef, question):
        self._question = question

    def as_form(self, required=""):
        raise NotImplementedError("Method as_form not defined for question of type %s " % self.question.type)

    @property
    def question(self):
        return self._question

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

class RadioQuestion(ChoiceQuestion):
    def __init__(self, qdef, question):
        super(RadioQuestion, self).__init__( qdef, question )

    def as_form(self, required=""):
        return forms.RadioForm( self, required=required)

class SelectQuestion(ChoiceQuestion):
    def __init__(self, qdef, question):
        super(SelectQuestion, self).__init__( qdef, question )

    def as_form(self, required=""):
        return forms.SelectForm( self, required=required )
        
class ButtonQuestion(ChoiceQuestion):
    def __init__(self, qdef, question):
        super(ButtonQuestion, self).__init__( qdef, question )

    def as_form(self, required=""):
        return forms.ButtonForm( self, required=required )

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

class TextQuestion(QuestionType):
    def __init__(self,qdef, question):
        super(TextQuestion, self).__init__( qdef, question )

    def as_form(self, required=""):
        return forms.TextForm( self, required=required )
        

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

class Page(object):
    def __init__(self, pdef):
        self._title = pdef.get("title")
        logger.info("Creating page %s" % self.title)
        self._questions = [Question(q) for q in pdef]

    @property
    def title(self):
        return self._title

    @property
    def questions(self):
        return self._questions

    def __len__(self):
        return len(self.questions)

    def __iter__(self):
        return self.questions.__iter__()


pages = [Page(p) for p in pdefs.iterfind("page")]


class Constants(BaseConstants):
    name_in_url = 'Demographics'
    players_per_group = None
    num_rounds = len( pages )


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass
