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
        # HTMLで使う変数を、過不足なく「辞書」として渡します
        history_data = []
        for r in range(1, player.round_number):
            g = player.group.in_round(r)
            proposals = [p.field_maybe_none('proposal') for p in g.get_players()]
            history_data.append({'round': r, 'proposals': proposals})
        
        return {
            'round_num': player.round_number,
            'max_rounds': C.NUM_ROUNDS,
            'history': history_data,
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
            prize_each = C.PRIZE_PER_PERSON if group.lottery_win else 0
            for p in players:
                p.payoff = prize_each - group.final_price
                p.participant.vars['public_lottery_payoff'] = p.payoff

class Results(Page):
    @staticmethod
    def is_displayed(player):
        return player.group.reached_agreement or player.round_number == C.NUM_ROUNDS

page_sequence = [Propose, WaitAfterPropose, Results]