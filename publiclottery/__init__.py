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
    prize_total = models.IntegerField(initial=0)

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
        prev_g = player.group.in_round(player.round_number - 1)
        return not prev_g.reached_agreement

    @staticmethod
    def vars_for_template(player):
        total_p = C.PLAYERS_PER_GROUP * C.PRIZE_PER_PERSON
        history_data = []
        for r in range(1, player.round_number):
            g = player.group.in_round(r)
            props = [{'proposal': p.field_maybe_none('proposal')} for p in g.get_players()]
            history_data.append({'round': r, 'proposals': props})
        
        return dict(
            round_number      = player.round_number,
            num_rounds        = C.NUM_ROUNDS,
            lottery_text      = f"公共くじ：当たり {total_p}円／はずれ 0円",
            prize_total       = total_p,
            PLAYERS_PER_GROUP = C.PLAYERS_PER_GROUP,
            history           = history_data
        )

class WaitAfterPropose(WaitPage):
    title_text = "判定中"
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
            group.prize_total = C.PLAYERS_PER_GROUP * C.PRIZE_PER_PERSON
            prize_each = C.PRIZE_PER_PERSON if group.lottery_win else 0
            for p in players:
                p.payoff = prize_each - group.final_price
                p.participant.vars['public_lottery_payoff'] = p.payoff

class Results(Page):
    @staticmethod
    def is_displayed(player):
        return player.group.reached_agreement or player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player):
        # Results画面で必要な変数をすべて網羅
        return dict(
            payoff            = player.payoff,
            final_price       = player.group.final_price,
            lottery_win       = player.group.lottery_win,
            prize_total       = C.PLAYERS_PER_GROUP * C.PRIZE_PER_PERSON,
            reached_agreement = player.group.reached_agreement,
            round_number      = player.round_number,
            num_rounds        = C.NUM_ROUNDS
        )

page_sequence = [Propose, WaitAfterPropose, Results]