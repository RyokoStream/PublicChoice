from otree.api import *
from .models import C
import random
import statistics

# --- 補助関数 (合意判定用) ---
def _stop_round(session):
    return session.vars.get("stop_round", 0)

# --- PAGES ---

class Propose(Page):
    form_model = "player"
    form_fields = ["proposal"]

    def is_displayed(self):
        # 合意が成立したら、以降のラウンドは表示しない
        return _stop_round(self.session) == 0

    def vars_for_template(self):
        # HTMLの {% if history %} で使うためのデータを作成
        history = []
        for r in range(1, self.round_number):
            g = self.group.in_round(r)
            history.append(dict(
                round=r,
                proposals=[dict(id=p.id_in_group, value=p.proposal) for p in g.get_players()],
            ))
        
        # HTMLに渡す変数をすべて定義
        return dict(
            round_number=self.round_number,
            num_rounds=C.NUM_ROUNDS,
            lottery_text=f"公共くじ：当たり {C.PRIZE_TOTAL}円／はずれ 0円（当たり確率 1/2）",
            history=history, # ←これで 'history' エラーが消えます
        )

class Pages2(Page):
    # Pages2.html を表示するためのクラス
    def is_displayed(self):
        return _stop_round(self.session) == 0

    def vars_for_template(self):
        return dict(
            summary="あなたの提案を送信しました。次の画面で結果を確認します。"
        )

class Results(Page):
    def is_displayed(self):
        # 最終結果を表示する条件（合意したラウンド、または最終ラウンド）
        stop = _stop_round(self.session)
        return (stop != 0 and self.round_number == stop) or (stop == 0 and self.round_number == C.NUM_ROUNDS)

    def vars_for_template(self):
        players = self.group.get_players()
        group_size = len(players)
        final_price = self.group.final_price
        reached_agreement = self.group.reached_agreement

        # 抽選（1回のみ実行）
        if not self.session.vars.get("lottery_drawn", False):
            self.session.vars["lottery_win"] = (random.random() < C.WIN_PROB)
            self.session.vars["lottery_drawn"] = True

        lottery_win = self.session.vars["lottery_win"]
        per_capita_prize = C.PRIZE_TOTAL // group_size
        payoff = (per_capita_prize - final_price) if lottery_win else (0 - final_price)

        return dict(
            proposals=sorted([p.proposal for p in players]),
            final_price=final_price,
            reached_agreement=reached_agreement,
            group_size=group_size,
            lottery_win=lottery_win,
            payoff=payoff,
        )

# --- ページ順序 ---
# あなたの手元にある「Propose」「Pages2」を軸にした構成です
page_sequence = [Propose, Pages2, Results]