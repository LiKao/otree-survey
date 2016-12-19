from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

from django.core.exceptions import ImproperlyConfigured

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

class Question(object):
    def __init__(self, qdef):
        if "variable" not in qdef.attrib:
            raise ImproperlyConfigured("Question is missing variable definition in lines %d-%d" %(qdef.start_line_number, qdef.end_line_number) )
        self._variable  = qdef.get("variable")
        self._type      = qdef.tag
        logger.info("Creating question %s of type %s" % (self.variable(),self.type()))

    def variable(self):
        return self._variable

    def type(self):
        return self._type

class Page(object):
    def __init__(self, pdef):
        self._title = pdef.get("title")
        logger.info("Creating page %s" % self.title()) 
        self._questions = [Question(q) for q in pdef]

    def title(self):
        return self._title

    def questions(self):
        return self._questions

pages = [Page(p) for p in questions.iterfind("page")]


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
