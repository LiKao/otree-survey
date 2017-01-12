from otree.api import models
from otree.api import BasePlayer
from otree.api import Page

from uuid import uuid4

import logging
logger = logging.getLogger(__name__)

from .xml       import XmlParse
from .page      import PageDef

class BaseSurveyPage(Page):
    template_name = "Survey/Survey.html"

    @property
    def survey(self):
        return self.__class__.survey

    @property
    def page(self):
        return self.survey.page( self.round_number )


    def vars_for_template(self):
        return {
            "title"     : self.page.title,
            "questions" : self.page.questions
        }

    def before_next_page(self):
        for question in self.page:
            vname = question.variable
            setattr(self.player, vname, self.form.data[vname])

class Survey(object):
    def __init__(self, name, fname):
        self._name = name

        pdefs = XmlParse("%s/%s" %(name,fname))
        self._pages = [PageDef(p) for p in pdefs.iterfind("page")]

    @property
    def num_rounds(self):
        return len(self._pages)

    def page(self, round_number):
        return self._pages[ round_number - 1 ]

    def create_player(self):
        model_attrs = {'__module__': self._name + ".models"}

        for page in self._pages:
            for question in page:
                model_attrs[question.variable] = models.CharField()

        model_cls = type('Player', (BasePlayer,), model_attrs)
        return model_cls

    def create_page(self):
        rv = []
        page_attrs = {'__module__': self._name + ".views"}
        page_attrs["survey"] = self

        page_cls = type("SurveyPage", (BaseSurveyPage,), page_attrs)
        return page_cls





