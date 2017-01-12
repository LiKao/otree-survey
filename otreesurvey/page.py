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

    def addquestion(self, question):
        if question.variable in self._variables:
            raise DuplicateVariableError('Duplicate variable "%s" in Page "%s"' %(question.variable, self.title))

        self._variables.add( question.variable )
        self._questions.append( question )


    def setsurvey(self, survey):
        self._surveys.add( survey )

    def __len__(self):
        return len(self._questions)

    def __iter__(self):
        return self._questions.__iter__()

def pageFromXml(xml):
    if "title" not in xml.attrib:
        raise ImproperlyConfigured("Page title missing at lines %d-%d" %(xml.start_line_number, xml.end_line_number))
    title = xml.get( "title" )
    rv = PageDef( title )

    for qdef in xml:
        question = questionFromXml(qdef)
        rv.addquestion(question)

    return rv