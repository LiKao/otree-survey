from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants, pages


class Demographics(Page):
    def vars_for_template(self):
    	page = pages[self.round_numer]
		return {
			"title" 	: page.title(),
			"questions"	: page.questions()
		}


page_sequence = [Demographics]
