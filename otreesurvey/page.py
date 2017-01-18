from uuid import uuid4

import logging
logger = logging.getLogger(__name__)

from .question      import questionFromXml
from .exceptions    import *

class PageDef(object):
    def __init__(self, title):
        logger.info('Creating survey page "%s"' % title)
        self._id        = uuid4().hex
        self._title     = title
        self._questions = []
        self._surveys   = set()
        self._surveyids = set()
        self._variables = set()

    @property
    def id(self):
        return self._id

    @property
    def title(self):
        return self._title

    @property
    def questions(self):
        return self._questions

    def add_question(self, question):
        logger.info('Adding question "{}" to page "{}"'.format( question.variable, self.title ) )
        self._questions.append( question )
        for varname in question.allVariables():
            if varname in self._variables:
                raise DuplicateVariableError('Duplicate variable "%s" in Page "%s"' %(varname, self.title))
            self._variables.add( varname )

            for survey in self._surveys:
                survey.add_variable( varname )

    def set_survey(self, survey):
        if self.is_in_survey( survey ):
            raise DuplicateSurveyRegisteredError('Same survey registered multiple times for page "%s"' % self.title)
        
        self._surveys.add( survey )
        self._surveyids.add( survey.id )

        for varname in self._variables:
            survey.add_variable( varname )

        if not survey.has_pageDef(self):
            survey.add_pageDef( self )

    def is_in_survey(self, survey):
        return survey.id in self._surveyids

    @property
    def variables(self):
        return self._variables

    def __len__(self):
        return len( self._questions )

    def __iter__(self):
        return self._questions.__iter__()

def pageFromXml(xml):
    if "title" not in xml.attrib:
        raise ImproperlyConfigured("Page title missing at lines %d-%d" %(xml.start_line_number, xml.end_line_number))
    title = xml.get( "title" )
    rv = PageDef( title )

    for qdef in xml:
        question = questionFromXml( qdef )
        rv.add_question( question )

    return rv