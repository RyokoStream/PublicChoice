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

class Propose(Page):
    form_model = 'player'
    form_fields = ['proposal']

    @staticmethod
    def is_displayed(player):
        # 1ラウンド目は必ず表示
        if player.round_number == 1:
            return True
        # 2回目以降は、前のラウンドで合意が「成立していない」場合のみ表示
        prev_g = player.group.in_round(player.round_number - 1)
        return prev_g.reached_agreement == False

    @staticmethod
    def vars_for_template(player):
        # HTMLが要求する変数をすべて網羅
        history = []
        for r in range(1, player.round_number):
            g = player.group.in_round(r)
            history.append({
                'round': r,
                'proposals': [{'id': p.id_in_group, 'proposal': p.field_maybe_none('proposal')} for p in g.get_players()]
            })
        return {
            'round_number': player.round_number,
            'num_rounds': C.NUM_ROUNDS,
            'history': history,
            'prize_total': C.PLAYERS_PER_GROUP * C.PRIZE_PER_PERSON,
            'lottery_text': f"当たり {C.PLAYERS_PER_GROUP * C.PRIZE_PER_PERSON}円 / はずれ 0円"
        }

class WaitAfterPropose(WaitPage):
    title_text = "判定中"
    body_text = "全員の入力を確認しています。"

    @staticmethod
    def after_all_players_arrive(group: Group):
        players = group.get_players()
        proposals = [p.proposal for p in players if p.proposal is not None]
        
        # 合意判定
        if len(set(proposals)) == 1:
            group.reached_agreement = True
            group.final_price = proposals[0]
        else:
            group.reached_agreement = False
            if group.round_number == C.NUM_ROUNDS:
                group.final_price = int(statistics.median(proposals))

        # 最終結果の計算と保存
        if group.reached_agreement or group.round_number == C.NUM_ROUNDS:
            group.lottery_win = random.random() < C.WIN_PROB
            prize_each = C.PRIZE_PER_PERSON if group.lottery_win else 0
            for p in players:
                p.payoff = prize_each - group.final_price
                # 他のアプリへ引き継ぐための保存
                p.participant.vars['public_lottery_payoff'] = p.payoff
                p.participant.vars['final_price'] = group.final_price
                p.participant.vars['reached_agreement'] = group.reached_agreement

class Results(Page):
    @staticmethod
    def is_displayed(player):
        # 連結版(combined)でない、かつ（合意した or 最終ラウンド）
        is_combined = 'combined' in player.session.config.get('name', '').lower()
        if is_combined:
            return False
        return player.group.reached_agreement or player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player):
        group = player.group
        return {
            'payoff': player.payoff,
            'final_price': group.final_price,
            'lottery_win': group.lottery_win,
            'reached_agreement': group.reached_agreement,
            'proposals': [p.proposal for p in group.get_players()],
        }

page_sequence = [Propose, WaitAfterPropose, Results]