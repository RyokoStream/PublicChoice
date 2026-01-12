from otree.api import *
import random
import statistics

class C(BaseConstants):
    NAME_IN_URL = 'publiclottery'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 3
    PRIZE_PER_PERSON = 1000 
    WIN_PROB = 0.5

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    final_price = models.IntegerField(initial=0)
    reached_agreement = models.BooleanField(initial=False)
    lottery_win = models.BooleanField()

class Player(BasePlayer):
    proposal = models.IntegerField(
        label="あなたの提案額（0〜1000円）",
        min=0, max=1000
    )

class Propose(Page):
    form_model = 'player'
    form_fields = ['proposal']

    @staticmethod
    def is_displayed(player):
        if player.round_number == 1:
            return True
        return not player.group.in_round(player.round_number - 1).reached_agreement

    @staticmethod
    def vars_for_template(player):
        # 変数を極限まで減らしました
        return {
            'round_num': player.round_number
        }

class WaitAfterPropose(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        players = group.get_players()
        proposals = [p.proposal for p in players if p.proposal is not None]
        
        if len(set(proposals)) == 1:
            group.reached_agreement = True
            group.final_price = proposals[0]
        else:
            group.reached_agreement = False
            if group.round_number == C.NUM_ROUNDS:
                group.final_price = int(statistics.median(proposals))

        if group.reached_agreement or group.round_number == C.NUM_ROUNDS:
            group.lottery_win = random.random() < C.WIN_PROB
            for p in players:
                p.payoff = (C.PRIZE_PER_PERSON if group.lottery_win else 0) - group.final_price
                p.participant.vars['public_lottery_payoff'] = p.payoff

class Results(Page):
    @staticmethod
    def is_displayed(player):
        return player.group.reached_agreement or player.round_number == C.NUM_ROUNDS

page_sequence = [Propose, WaitAfterPropose, Results]