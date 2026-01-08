from otree.api import models, BaseConstants, BaseSubsession, BaseGroup, BasePlayer, Currency
from otree.models import player, subsession

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    chose_lottery = models.BooleanField()
    won_lottery = models.BooleanField()

class Trial(ExtraModel):
    sure_payoff = models.CurrencyField()
    lottery_high = models.CurrencyField()
    lottery_low = models.CurrencyField()
    probability_percent = models.IntegerField()
    chose_lottery = models.BooleanField()
    is_selected = models.BooleanField(initial=False)
