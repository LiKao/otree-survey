import logging
logger = logging.getLogger(__name__)

from .question      import questionFromXml

class PageDef(object):
    def __init__(self, title):
        self._title = title
        logger.info('Creating page "%s"' % self._title)
        self._questions = []

    @property
    def title(self):
        return self._title

    @property
    def questions(self):
        return self._questions

    def addquestion(self, question):
        self._questions.append( question )

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