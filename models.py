from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)


author = 'Tillmann Nett'

doc = """
Simple app for collecting demographic data.

Definitions for demographic data are taken from a short XML file.
"""

### Read XML definitions:



class Constants(BaseConstants):
    name_in_url = 'Demographics'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass
