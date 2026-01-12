from os import environ

# Security Settings
SECRET_KEY = '5238389471112'
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD') or 'Ryoko0903'

# Session Configurations
SESSION_CONFIGS = [
    # 1. 本番用：リスク計測、公共くじ、そして最終結果を連続で行う
    dict(
        name='combined_experiment',
        display_name="【本番用】リスク計測と公共くじ実験（一連の流れ）",
        num_demo_participants=3,
        app_sequence=['mpl_japanese', 'publiclottery', 'final_results']
    ),
    # 2. 個別テスト用：MPLのみ
    dict(
        name='mpl_japanese_session',
        display_name="MPL 日本語版（単体テスト）",
        num_demo_participants=1,
        app_sequence=['mpl_japanese']
    ),
    # 3. 個別テスト用：公共くじのみ
    dict(
        name='publiclottery_session',
        display_name="Public Lottery（単体テスト）",
        num_demo_participants=3,
        app_sequence=['publiclottery']
    ),
]

# Default Settings
SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=0.00,
    doc=""
)

# 参加者やセッションごとの変数を保存する場所
PARTICIPANT_FIELDS = ['mpl_payoff',
'public_lottery_payoff',]
SESSION_FIELDS = []

# Localization (日本語設定)
LANGUAGE_CODE = 'ja'
REAL_WORLD_CURRENCY_CODE = 'JPY'
USE_POINTS = True

# Rooms
ROOMS = [
    dict(
        name='econ101',
        display_name='Econ 101 class',
    ),
    dict(name='live_demo', display_name='Room for live demo'),
]

# インストールされているアプリのリスト（新しく作ったアプリも忘れずに追加）
INSTALLED_APPS = [
    'otree', 
    'mpl_japanese', 
    'publiclottery', 
    'final_results'
]

DEMO_PAGE_INTRO_HTML = """
実験プログラムの管理画面です。
"""