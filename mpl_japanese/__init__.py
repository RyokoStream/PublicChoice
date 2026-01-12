from otree.api import *
import random

class C(BaseConstants):
    NAME_IN_URL = 'mpl_japanese'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    LOTTERY_HIGH = 1000
    LOTTERY_LOW = 0
    LOTTERY_PROBABILITY = 50
    AMOUNTS = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550]

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    # --- フィールド定義 ---
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

def make_rows(prefix):
    return [{'field_name': f'{prefix}_{i}', 'label': f'{i}円'} for i in C.AMOUNTS]

# --- PAGES ---

class Decision(Page):
    form_model = 'player'
    def get_form_fields(player):
        return [f'choice_{i}' for i in C.AMOUNTS]
    @staticmethod
    def vars_for_template(player: Player):
        return dict(is_ambiguity=False, lottery_text=f"{C.LOTTERY_PROBABILITY}%で{C.LOTTERY_HIGH}円", rows=make_rows('choice'))

class DecisionAmbiguity(Page):
    form_model = 'player'
    def get_form_fields(player):
        return [f'choice_ambig_{i}' for i in C.AMOUNTS]
    @staticmethod
    def vars_for_template(player: Player):
        return dict(is_ambiguity=True, lottery_text="確率不明のくじ", rows=make_rows('choice_ambig'))

class Results(Page):
    @staticmethod
    def is_displayed(player):
        return True

    @staticmethod
    def get_timeout_seconds(player):
        if player.session.config['name'] == 'combined_experiment':
            return 0
        return None

    @staticmethod
    def vars_for_template(player: Player):
        # 確実に変数を初期化する
        choice_type_text = ""
        selected_amount = random.choice(C.AMOUNTS)
        choice_text = ""
        was_lottery = False
        payoff = 0

        choice_type = random.choice(['regular', 'ambiguity'])
        
        if choice_type == 'regular':
            field_name = f'choice_{selected_amount}'
            choice_type_text = "リスク計測（通常のくじ）"
        else:
            field_name = f'choice_ambig_{selected_amount}'
            choice_type_text = "曖昧さ計測（確率不明のくじ）"
        
        # 値の取得とエラーハンドリング
        player_choice_val = getattr(player, field_name, None)
        
        # 獲得額の計算
        lottery_outcome = random.choice([C.LOTTERY_HIGH, C.LOTTERY_LOW])
        
        if player_choice_val == 1:
            choice_text = "くじ"
            was_lottery = True
            payoff = lottery_outcome
        else:
            choice_text = "確実"
            was_lottery = False
            payoff = selected_amount
        
        # データの記録
        player.payoff = payoff
        player.participant.mpl_payoff = payoff
        
        return {
            'choice_type_text': choice_type_text,
            'selected_amount': selected_amount,
            'choice_text': choice_text,
            'was_lottery': was_lottery,
            'payoff': payoff,
        }

page_sequence = [Decision, DecisionAmbiguity, Results]