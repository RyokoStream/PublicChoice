from otree.api import *
import json

def make_rows():
    amounts = list(range(50, 551, 50))  # 50, 100, ..., 550（11通り）
    return [
        {"label": f"{a} 円", "field_name": f"row_{i+1}"}
        for i, a in enumerate(amounts)
    ]



class RiskMPL(Page):
    # ★ 同じテンプレを使い回す
    template_name = 'mpl_japanese/Intro.html'

    # ★ vars_for_template は self 形式（あなたの環境で確実）
    def vars_for_template(self):
        return dict(
            is_ambiguity=False,
            lottery_text="くじ：状態1（確率1/2）→1000円、状態2（確率1/2）→0円",
            rows=make_rows(),
        )

    # ★ live_method は static（player を直接受け取る）
    @staticmethod
    def live_method(player, data):
        if data.get("type") == "submit":
            player.mpl_risk_json = json.dumps(
                data.get("choices", {}),
                ensure_ascii=False
            )
            return {player.id_in_group: dict(type="finished")}

class AmbiguityMPL(Page):
    # ★ 同じテンプレ
    template_name = 'mpl_japanese/Intro.html'

    def vars_for_template(self):
        return dict(
            is_ambiguity=True,
            lottery_text="くじ：状態1なら1000円、状態2なら0円（各状態が出る確率は不明）",
            rows=make_rows(),
        )

    @staticmethod
    def live_method(player, data):
        if data.get("type") == "submit":
            player.mpl_amb_json = json.dumps(
                data.get("choices", {}),
                ensure_ascii=False
            )
            return {player.id_in_group: dict(type="finished")}


# ★ ここに入れる（AmbiguityMPLの外、page_sequenceの前）
class WaitForExperimenter(Page):
    template_name = 'mpl_japanese/WaitForExperimenter.html'


# ★ ページ順（ここに「名前だけ」入れる）
page_sequence = [
    RiskMPL,              # 1ページ目：確率明示
    AmbiguityMPL,         # 2ページ目：確率不明
    WaitForExperimenter,  # 最後：待機ページ
]
