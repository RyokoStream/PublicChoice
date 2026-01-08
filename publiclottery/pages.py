from otree.api import *
from .models import C
import random
import statistics


def _stop_round(session):
    # 合意が成立したラウンド番号。未確定なら 0
    return session.vars.get("stop_round", 0)


class Propose(Page):
    form_model = "player"
    form_fields = ["proposal"]

    def is_displayed(self):
        # stop_round が確定したら、以降のラウンドでは提案ページ自体を出さない
        return _stop_round(self.session) == 0

    def vars_for_template(self):
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
            lottery_text=f"公共くじ：当たり {C.PRIZE_TOTAL}円／はずれ 0円（当たり確率 1/2）",
            history=history,
        )


class WaitAll(WaitPage):
    body_text = "他の参加者の入力を待っています…"

    def is_displayed(self):
        return _stop_round(self.session) == 0

    def after_all_players_arrive(self):
        # このラウンドの入力が揃った瞬間に、合意判定→必要なら終了ラウンドを確定
        players = self.group.get_players()
        proposals = [p.proposal for p in players]

        all_same = len(set(proposals)) == 1
        if all_same:
            self.group.final_price = proposals[0]
            self.group.reached_agreement = True
            # ★ここで終了ラウンドを確定（以降ラウンドをスキップ）
            self.session.vars["stop_round"] = self.round_number

        # 合意がなく、最終ラウンドに到達したらそこで終了（中央値で決定）
        if (not all_same) and (self.round_number == C.NUM_ROUNDS):
            self.group.final_price = int(statistics.median(proposals))
            self.group.reached_agreement = False
            self.session.vars["stop_round"] = self.round_number


class Reveal(Page):
    def is_displayed(self):
        # stop_round が確定したラウンドだけ表示（未確定の間は通常どおり表示）
        stop = _stop_round(self.session)
        return (stop == 0) or (self.round_number == stop)

    def vars_for_template(self):
        proposals = [p.proposal for p in self.group.get_players()]
        return dict(
            round_number=self.round_number,
            num_rounds=C.NUM_ROUNDS,
            proposals=sorted(proposals),
        )


class Results(Page):
    def is_displayed(self):
        stop = _stop_round(self.session)
        # 合意成立ラウンド or 最終ラウンドで結果表示
        return (stop != 0 and self.round_number == stop) or (stop == 0 and self.round_number == C.NUM_ROUNDS)

    def vars_for_template(self):
        players = self.group.get_players()
        proposals = [p.proposal for p in players]
        group_size = len(players)

        final_price = self.group.final_price
        reached_agreement = self.group.reached_agreement

        # ★抽選は1回だけ固定（session.varsに保存）
        if not self.session.vars.get("lottery_drawn", False):
            self.session.vars["lottery_win"] = (random.random() < C.WIN_PROB)
            self.session.vars["lottery_drawn"] = True

        lottery_win = self.session.vars["lottery_win"]

        per_capita_prize = C.PRIZE_TOTAL // group_size
        payoff = (per_capita_prize - final_price) if lottery_win else (0 - final_price)
        group_investment = final_price * group_size

        return dict(
            proposals=sorted(proposals),
            final_price=final_price,
            reached_agreement=reached_agreement,
            group_size=group_size,
            group_investment=group_investment,
            prize_total=C.PRIZE_TOTAL,
            per_capita_prize=per_capita_prize,
            lottery_win=lottery_win,
            payoff=payoff,
        )


class WaitForExperimenter(Page):
    template_name = "publiclottery/WaitForExperimenter.html"

    def is_displayed(self):
        stop = _stop_round(self.session)
        return (stop != 0 and self.round_number == stop) or (stop == 0 and self.round_number == C.NUM_ROUNDS)


page_sequence = [Propose, WaitAll, Reveal, Results, WaitForExperimenter]
