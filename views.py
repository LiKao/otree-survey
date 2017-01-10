from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants, pages
from .forms  import QuestionForm

class Demographics(Page):
    def vars_for_template(self):
        page = pages[self.round_number - 1]
        return {
            "title"     : page.title,
            "questions" : page.questions
        }


page_sequence = [Demographics]
