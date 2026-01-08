from otree.api import *


class C(BaseConstants):
    NAME_IN_URL = "publiclottery"
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 3

    # ★デモ用：当たったときの総額（3人なら 3000円）
    PRIZE_TOTAL = 3000

    # ★当たり確率（今は明示 1/2）
    WIN_PROB = 0.5


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    # 最終的に採用した一人あたり購入額（中央値 or 一致額）
    final_price = models.IntegerField(initial=0)

    # 合意したかどうか
    reached_agreement = models.BooleanField(initial=False)

    # ★当たり外れ（抽選結果）
    lottery_win = models.BooleanField(initial=False)

    # ★抽選を1回だけに固定するためのフラグ（これが無いと pages.py が落ちる）
    lottery_drawn = models.BooleanField(initial=False)


class Player(BasePlayer):
    # 各ラウンドの提案（自己負担）額（円）
    proposal = models.IntegerField(min=0, max=1000)
