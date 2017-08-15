from otree.api import models
from otree.api import BasePlayer
from otree.api import Page

from uuid import uuid4

import logging
logger = logging.getLogger(__name__)

from .xml           import XmlParse
from .page          import pageFromXml
from .exceptions    import *

class BaseSurveyPage(Page):
    template_name = "Survey/Survey.html"

    def get_context_data(self, **kwargs):
        context = super(BaseSurveyPage, self).get_context_data( **kwargs )
        context["title"]        = self.page.title
        context["questions"]    = self.page.questions
        return context

    @property
    def survey(self):
        # Known reference in Player created by "contribute_to_class"
        return self.player._survey

    @property
    def page(self):
        return self.survey.page( self.round_number )

    def post(self, *args, **kwargs):
        nrv = super(BaseSurveyPage, self).post(request, *args, **kwargs)
        for varname in self.page.variables:
            if varname in self.form.data:
                setattr(self.player, varname, self.form.data[varname])
        return nrv

class Survey(object):
    def __init__(self, name):
        self._id        = uuid4().hex    
        self._name      = name
        self._pages     = []
        self._pageids   = set()
        self._variables = set()

    def add_pageDef(self, page):
        if self.has_pageDef( page ):
            raise DuplicatePageError('Page "%s" added multiple times to same survey' % page.title)

        self._pageids.add( page.id )
        self._pages.append( page )

        if not page.is_in_survey( self ):
            page.set_survey( self )

    def add_variable(self, varname):
        if self.has_variable( varname ):
            raise DuplicateVariableError('Duplicate variable "%s" for same survey defined' %(varname, self.title))

        self._variables.add( varname )

    def has_pageDef(self, page):
        return page.id in self._pageids

    def has_variable(self, varname):
        return varname in self._variables

    @property
    def num_rounds(self):
        return len(self._pages)

    @property
    def id(self):
        return self._id

    def page(self, round_number):
        return self._pages[ round_number - 1 ]

    def contribute_to_class( self, cls, name ):
        setattr(cls, name, self)
        # We add an additional name at a known place for later reference
        # in the page.
        # TODO: Find a better way to get the actual object into Player model
        setattr(cls, "_survey", self)
        for page in self._pages:
            for varname in page.variables:
                models.CharField().contribute_to_class(cls, varname)


# TODO: Currently, if we want to add additional structures, we have an NxM situation here
# Solution: Make the construction independent from the parsing using a visitor pattern
def surveyFromXml(surveyname, xml):
    rv = Survey(surveyname)
    for pdef in xml.iterfind("page"):
        page = pageFromXml( pdef )
        rv.add_pageDef( page )
    return rv

def surveyFromXmlFile(surveyname, filename):
    xml = XmlParse("%s/%s" % (surveyname, filename))
    return surveyFromXml(surveyname, xml)
