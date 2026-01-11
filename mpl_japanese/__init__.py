from otree.api import *

doc = """
マシュー・リンチ形式のMPL（選択課題）
"""

class C(BaseConstants):
    NAME_IN_URL = 'mpl_japanese'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    LOTTERY_HIGH = 1000
    LOTTERY_LOW = 0
    LOTTERY_PROBABILITY = 50
    # 選択肢のリスト
    AMOUNTS = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550]

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    # 通常の選択用フィールドを動的に定義できないため、個別に定義
    choice_50 = models.IntegerField(choices=[[1, 'くじ'], [2, '確実']], widget=widgets.RadioSelectHorizontal)
    choice_100 = models.IntegerField(choices=[[1, 'くじ'], [2, '確実']], widget=widgets.RadioSelectHorizontal)
    choice_150 = models.IntegerField(choices=[[1, 'くじ'], [2, '確実']], widget=widgets.RadioSelectHorizontal)
    choice_200 = models.IntegerField(choices=[[1, 'くじ'], [2, '確実']], widget=widgets.RadioSelectHorizontal)
    choice_250 = models.IntegerField(choices=[[1, 'くじ'], [2, '確実']], widget=widgets.RadioSelectHorizontal)
    choice_300 = models.IntegerField(choices=[[1, 'くじ'], [2, '確実']], widget=widgets.RadioSelectHorizontal)
    choice_350 = models.IntegerField(choices=[[1, 'くじ'], [2, '確実']], widget=widgets.RadioSelectHorizontal)
    choice_400 = models.IntegerField(choices=[[1, 'くじ'], [2, '確実']], widget=widgets.RadioSelectHorizontal)
    choice_450 = models.IntegerField(choices=[[1, 'くじ'], [2, '確実']], widget=widgets.RadioSelectHorizontal)
    choice_500 = models.IntegerField(choices=[[1, 'くじ'], [2, '確実']], widget=widgets.RadioSelectHorizontal)
    choice_550 = models.IntegerField(choices=[[1, 'くじ'], [2, '確実']], widget=widgets.RadioSelectHorizontal)

    # 曖昧さ（確率不明）用フィールド
    choice_ambig_50 = models.IntegerField(choices=[[1, 'くじ'], [2, '確実']], widget=widgets.RadioSelectHorizontal)
    choice_ambig_100 = models.IntegerField(choices=[[1, 'くじ'], [2, '確実']], widget=widgets.RadioSelectHorizontal)
    choice_ambig_150 = models.IntegerField(choices=[[1, 'くじ'], [2, '確実']], widget=widgets.RadioSelectHorizontal)
    choice_ambig_200 = models.IntegerField(choices=[[1, 'くじ'], [2, '確実']], widget=widgets.RadioSelectHorizontal)
    choice_ambig_250 = models.IntegerField(choices=[[1, 'くじ'], [2, '確実']], widget=widgets.RadioSelectHorizontal)
    choice_ambig_300 = models.IntegerField(choices=[[1, 'くじ'], [2, '確実']], widget=widgets.RadioSelectHorizontal)
    choice_ambig_350 = models.IntegerField(choices=[[1, 'くじ'], [2, '確実']], widget=widgets.RadioSelectHorizontal)
    choice_ambig_400 = models.IntegerField(choices=[[1, 'くじ'], [2, '確実']], widget=widgets.RadioSelectHorizontal)
    choice_ambig_450 = models.IntegerField(choices=[[1, 'くじ'], [2, '確実']], widget=widgets.RadioSelectHorizontal)
    choice_ambig_500 = models.IntegerField(choices=[[1, 'くじ'], [2, '確実']], widget=widgets.RadioSelectHorizontal)
    choice_ambig_550 = models.IntegerField(choices=[[1, 'くじ'], [2, '確実']], widget=widgets.RadioSelectHorizontal)

# 共通のテンプレート変数作成関数
def make_rows(prefix):
    return [{'field_name': f'{prefix}_{i}', 'label': f'{i}円'} for i in C.AMOUNTS]

class Decision(Page):
    form_model = 'player'
    def get_form_fields(player):
        return [f'choice_{i}' for i in C.AMOUNTS]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            is_ambiguity=False,
            lottery_text=f"{C.LOTTERY_PROBABILITY}%で{C.LOTTERY_HIGH}円、{100-C.LOTTERY_PROBABILITY}%で{C.LOTTERY_LOW}円",
            rows=make_rows('choice')
        )

class DecisionAmbiguity(Page):
    form_model = 'player'
    def get_form_fields(player):
        return [f'choice_ambig_{i}' for i in C.AMOUNTS]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            is_ambiguity=True,
            lottery_text=f"確率不明のくじ（{C.LOTTERY_HIGH}円 または {C.LOTTERY_LOW}円）",
            rows=make_rows('choice_ambig')
        )

class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        import random
        # 支払決定プロセスの再現
        choice_type = random.choice(['regular', 'ambiguity'])
        selected_amount = random.choice(C.AMOUNTS)
        
        if choice_type == 'regular':
            player_choice = getattr(player, f'choice_{selected_amount}')
            choice_type_text = "通常の選択（確率50%のくじ）"
        else:
            player_choice = getattr(player, f'choice_ambig_{selected_amount}')
            choice_type_text = "確率不明の選択"
        
        lottery_outcome = random.choice([C.LOTTERY_HIGH, C.LOTTERY_LOW])
        
        if player_choice == 1: # くじを選んだ場合
            player.payoff = lottery_outcome
            choice_text = "くじ"
        else: # 確実な金額を選んだ場合
            player.payoff = selected_amount
            choice_text = f"{selected_amount}円（確実）"
        
        return dict(
            selected_amount=selected_amount,
            choice_type_text=choice_type_text,
            choice_text=choice_text,
            lottery_outcome=lottery_outcome,
            payoff=player.payoff,
            was_lottery=(player_choice == 1)
        )

page_sequence = [Decision, DecisionAmbiguity, Results]