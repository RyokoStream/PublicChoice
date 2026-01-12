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

# --- PAGES ---

class Propose(Page):
    form_model = 'player'
    form_fields = ['proposal']

    @staticmethod
    def is_displayed(player):
        if player.round_number == 1:
            return True
        try:
            prev_group = player.group.in_round(player.round_number - 1)
            return not prev_group.reached_agreement
        except:
            return True

    @staticmethod
    def vars_for_template(player):
        group = player.group
        group_size = len(group.get_players())
        prize_total = group_size * C.PRIZE_PER_PERSON
        
        history = []
        for r in range(1, player.round_number):
            try:
                g = group.in_round(r)
                round_proposals = []
                for p_in_g in g.get_players():
                    # HTMLのあらゆる変数名（id, id_in_group, value, proposal）に対応
                    round_proposals.append({
                        'id': p_in_g.id_in_group,
                        'id_in_group': p_in_g.id_in_group,
                        'value': p_in_g.field_maybe_none('proposal'),
                        'proposal': p_in_g.field_maybe_none('proposal'),
                    })
                
                history.append(dict(
                    round=r,
                    round_number=r,
                    proposals=round_proposals,
                ))
            except:
                continue
        
        return dict(
            round_number=player.round_number,
            num_rounds=C.NUM_ROUNDS,
            lottery_text=f"公共くじ：当たり {prize_total}円／はずれ 0円",
            history=history,
            prize_total=prize_total,
            group_size=group_size
        )

class WaitAfterPropose(WaitPage):
    title_text = "待機中"
    body_text = "他の参加者の入力を待っています。"

    @staticmethod
    def after_all_players_arrive(group: Group):
        players = group.get_players()
        proposals = [p.field_maybe_none('proposal') for p in players if p.field_maybe_none('proposal') is not None]
        
        if len(proposals) < C.PLAYERS_PER_GROUP:
            return

        all_same = len(set(proposals)) == 1
        group.prize_total = len(players) * C.PRIZE_PER_PERSON

        if all_same:
            group.reached_agreement = True
            group.final_price = proposals[0]
        elif group.round_number == C.NUM_ROUNDS:
            group.reached_agreement = False
            group.final_price = int(statistics.median(proposals))

        # 結果が決まったら利得を計算し、保存する
        if group.reached_agreement or group.round_number == C.NUM_ROUNDS:
            group.lottery_win = random.random() < C.WIN_PROB
            prize_each = C.PRIZE_PER_PERSON if group.lottery_win else 0
            for p in players:
                p.payoff = prize_each - group.final_price
                
                # 【最重要】KeyErrorを回避するための二重保存
                # 1. settings.py の定義への保存（試行）
                try:
                    p.participant.public_lottery_payoff = p.payoff
                except:
                    pass
                
                # 2. participant.vars への保存（確実）
                p.participant.vars['public_lottery_payoff'] = p.payoff

class Results(Page):
    @staticmethod
    def is_displayed(player):
        # 連結実験時はここでは表示せず、最後（final_results）に出す
        is_combined = 'combined' in player.session.config.get('name', '').lower()
        if is_combined:
            return False
        return player.group.reached_agreement or player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player):
        group = player.group
        players = group.get_players()
        
        return dict(
            prize_total      = group.prize_total,
            proposals        = [p.field_maybe_none('proposal') for p in players],
            final_price      = group.final_price,
            reached_agreement= group.reached_agreement,
            group_investment = group.final_price * len(players),
            group_size       = len(players),
            lottery_win      = group.lottery_win,
            per_capita_prize = C.PRIZE_PER_PERSON,
            payoff           = player.payoff
        )

page_sequence = [Propose, WaitAfterPropose, Results]