from otree.api import *

class C(BaseConstants):
    NAME_IN_URL = "mpl_japanese"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    mpl_risk_json = models.LongStringField(blank=True)
    mpl_amb_json = models.LongStringField(blank=True)


