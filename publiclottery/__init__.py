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
    prize_total = models.IntegerField(initial=0)
    lottery_win = models.BooleanField()

class Player(BasePlayer):
    proposal = models.IntegerField(
        label="購入額（0〜1000円）",
        min=0, max=1000
    )

# --- ページ定義 ---

class Propose(Page):
    form_model = 'player'
    form_fields = ['proposal']

    @staticmethod
    def is_displayed(player):
        if player.round_number == 1:
            return True
        # 前のラウンドを参照し、合意済みならスキップ
        prev_round = player.round_number - 1
        return not player.group.in_round(prev_round).reached_agreement

    @staticmethod
    def vars_for_template(player):
        group_size = C.PLAYERS_PER_GROUP
        prize_total = group_size * C.PRIZE_PER_PERSON
        
        history = []
        for r in range(1, player.round_number):
            g = player.group.in_round(r)
            round_proposals = []
            for p_in_g in g.get_players():
                round_proposals.append({
                    'id': p_in_g.id_in_group,
                    'proposal': p_in_g.field_maybe_none('proposal'),
                })
            history.append(dict(round=r, proposals=round_proposals))
        
        return dict(
            history=history,
            prize_total=prize_total,
            group_size=group_size
        )

class WaitAfterPropose(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        players = group.get_players()
        # proposalが入っていない場合に備えてデフォルト値(0)を考慮
        proposals = [p.proposal if p.proposal is not None else 0 for p in players]
        
        all_same = len(set(proposals)) == 1
        group.prize_total = len(players) * C.PRIZE_PER_PERSON

        if all_same:
            group.reached_agreement = True
            group.final_price = proposals[0]
        elif group.round_number == C.NUM_ROUNDS:
            group.reached_agreement = False
            group.final_price = int(statistics.median(proposals))
        else:
            group.reached_agreement = False
            group.final_price = 0

        # 合意した、あるいは最終回の場合に計算を実行
        if group.reached_agreement or group.round_number == C.NUM_ROUNDS:
            group.lottery_win = random.random() < C.WIN_PROB
            prize_each = C.PRIZE_PER_PERSON if group.lottery_win else 0
            
            for p in players:
                p.payoff = prize_each - group.final_price
                # HTMLで呼び出す可能性のある名前をすべて「確実」に保存
                p.participant.vars['public_lottery_payoff'] = p.payoff
                p.participant.vars['final_price'] = group.final_price
                p.participant.vars['reached_agreement'] = group.reached_agreement

class Results(Page):
    @staticmethod
    def is_displayed(player):
        is_combined = 'combined' in player.session.config.get('name', '').lower()
        if is_combined:
            return False
        return player.group.reached_agreement or player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player):
        return {
            'payoff': player.payoff,
            'final_price': player.group.final_price,
            'lottery_win': player.group.lottery_win,
        }

page_sequence = [Propose, WaitAfterPropose, Results]