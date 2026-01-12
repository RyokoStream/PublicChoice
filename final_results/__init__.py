from otree.api import *

class C(BaseConstants):
    NAME_IN_URL = 'final_results'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    pass

# --- PAGES ---

class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        # 第1部の結果を取得
        mpl_amt = getattr(player.participant, 'mpl_payoff', 0)
        
        # 全体の利得から第1部を引いて、第2部（公共くじ）分を出す
        total_amt = player.participant.payoff
        pub_amt = total_amt - mpl_amt
        
        return dict(
            mpl_amt = mpl_amt,
            pub_amt = pub_amt,
            total_payoff = total_amt
        )

page_sequence = [Results]