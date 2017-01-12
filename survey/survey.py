from otree.api import models
from otree.api import BasePlayer

import logging
logger = logging.getLogger(__name__)

from .xml       import XmlParse
from .page      import Page

import os
cwd = os.getcwd()

class Survey(object):
    def __init__(self, name, fname):
        self._name = name

        pdefs = XmlParse("%s/%s" %(name,fname))
        self._pages = [Page(p) for p in pdefs.iterfind("page")]    

    def create_player(self):
        model_attrs = {'__module__': self._name + ".models"}

        for page in self._pages:
            for question in page:
                model_attrs[question.variable] = models.CharField()

        model_cls = type('Player', (BasePlayer,), model_attrs)
        return model_cls



