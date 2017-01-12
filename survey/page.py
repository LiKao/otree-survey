import logging
logger = logging.getLogger(__name__)

from .question      import Question

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