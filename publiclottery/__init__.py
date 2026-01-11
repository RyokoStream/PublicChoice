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

class Player(BasePlayer):
    proposal = models.IntegerField(
        label="購入額（0〜1000円）",
        min=0, max=1000
    )

# --- PAGES ---

class Propose(Page):
    form_model = 'player'
    form_fields = ['proposal']

    def is_displayed(self):
        if self.round_number == 1:
            return True
        return not self.group.in_round(self.round_number - 1).reached_agreement

    def vars_for_template(self):
        group_size = len(self.group.get_players())
        current_prize_total = group_size * C.PRIZE_PER_PERSON
        
        history = []
        for r in range(1, self.round_number):
            g = self.group.in_round(r)
            history.append(dict(
                round=r,
                proposals=[dict(id=p.id_in_group, value=p.proposal) for p in g.get_players()],
            ))
        
        return dict(
            round_number=self.round_number,
            num_rounds=C.NUM_ROUNDS,
            lottery_text=f"公共くじ：当たり {current_prize_total}円／はずれ 0円",
            history=history,
            group_investment=0
        )

# WaitPageはHTMLファイルを作らなくて大丈夫です
class WaitAfterPropose(WaitPage):
    title_text = "待機中"
    body_text = "他の参加者が入力するのを待っています。全員の入力が終わると自動的に進みます。"

    def after_all_players_arrive(self):
        proposals = [p.proposal for p in self.group.get_players()]
        all_same = len(set(proposals)) == 1
        
        if all_same:
            self.group.reached_agreement = True
            self.group.final_price = proposals[0]
        elif self.round_number == C.NUM_ROUNDS:
            self.group.reached_agreement = False
            self.group.final_price = int(statistics.median(proposals))

        # 抽選と利得計算
        if self.group.reached_agreement or self.round_number == C.NUM_ROUNDS:
            lottery_win = random.random() < C.WIN_PROB
            self.session.vars[f'win_group_{self.group.id}'] = lottery_win
            
            for p in self.group.get_players():
                if lottery_win:
                    p.payoff = C.PRIZE_PER_PERSON - self.group.final_price
                else:
                    p.payoff = 0 - self.group.final_price

class Results(Page):
    def is_displayed(self):
        if self.group.reached_agreement:
            return True
        return self.round_number == C.NUM_ROUNDS

    def vars_for_template(self):
        lottery_win = self.session.vars.get(f'win_group_{self.group.id}', False)
        players = self.group.get_players()
        proposals_list = [p.proposal for p in players]
        
        return dict(
            proposals=proposals_list,
            group_investment=sum(proposals_list),
            prize_total=len(players) * C.PRIZE_PER_PERSON,
            final_price=self.group.final_price,
            lottery_win=lottery_win,
            payoff=self.payoff, 
            per_capita_prize=C.PRIZE_PER_PERSON,
            group_size=len(players),
            reached_agreement=self.group.reached_agreement,
        )

page_sequence = [Propose, WaitAfterPropose, Results]