from otree.api import *
import random
import statistics

class C(BaseConstants):
    NAME_IN_URL = 'public_lottery_v3' # URLの重複を避けるため更新
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 3
    PRIZE_PER_PERSON = 1000 
    WIN_PROB = 0.5
    TOTAL_PRIZE = PLAYERS_PER_GROUP * PRIZE_PER_PERSON

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

def vars_for_all_pages(player: Player):
    history_data = []
    # 過去のラウンドを遡る
    for r_num in range(1, player.round_number):
        try:
            g = player.group.in_round(r_num)
            
            # HTML側の {% for p in r.proposals %} が100%ループできるように
            # リストを明示的に作成します
            round_proposals = []
            for p in g.get_players():
                val = p.field_maybe_none('proposal')
                if val is not None:
                    # ここが line 34 の {{ p.proposal }} に直結します
                    round_proposals.append({'proposal': val})
            
            history_data.append({
                'round': r_num,
                'proposals': round_proposals # キー名は必ず 'proposals'
            })
        except:
            continue

    return dict(
        history           = history_data,
        lottery_text      = f"公共くじ：当たり {C.TOTAL_PRIZE}円／はずれ 0円",
        prize_total       = C.TOTAL_PRIZE,
        round_number      = player.round_number,
        num_rounds        = C.NUM_ROUNDS,
        PLAYERS_PER_GROUP = C.PLAYERS_PER_GROUP,
        final_price       = player.group.final_price,
        lottery_win       = player.group.field_maybe_none('lottery_win'),
        reached_agreement = player.group.reached_agreement,
        payoff            = player.payoff or 0
    )

class Propose(Page):
    form_model = 'player'
    form_fields = ['proposal']

    @staticmethod
    def is_displayed(player):
        if player.round_number == 1:
            return True
        # 前のラウンドの合意状況を確認
        prev_g = player.group.in_round(player.round_number - 1)
        return not prev_g.reached_agreement

    vars_for_template = vars_for_all_pages

class WaitAfterPropose(WaitPage):
    title_text = "判定中..."
    
    @staticmethod
    def after_all_players_arrive(group: Group):
        players = group.get_players()
        props = [p.proposal for p in players if p.proposal is not None]
        
        # 全員一致のロジック
        if len(set(props)) == 1:
            group.reached_agreement = True
            group.final_price = props[0]
        elif group.round_number == C.NUM_ROUNDS:
            group.reached_agreement = False
            group.final_price = int(statistics.median(props))

        # 計算
        if group.reached_agreement or group.round_number == C.NUM_ROUNDS:
            group.lottery_win = random.random() < C.WIN_PROB
            prize_each = C.PRIZE_PER_PERSON if group.lottery_win else 0
            for p in players:
                p.payoff = prize_each - group.final_price

class Results(Page):
    @staticmethod
    def is_displayed(player):
        return player.group.reached_agreement or player.round_number == C.NUM_ROUNDS

    vars_for_template = vars_for_all_pages

page_sequence = [Propose, WaitAfterPropose, Results]