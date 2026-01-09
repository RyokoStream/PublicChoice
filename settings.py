from os import environ

# Security Settings
SECRET_KEY = '5238389471112'
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD') or 'Ryoko0903'

# Session Configurations
SESSION_CONFIGS = [
    dict(
        name='mpl_japanese_session',
        display_name="MPL 日本語版",
        num_demo_participants=1,
        app_sequence=['mpl_japanese']
    ),
    dict(
        name='publiclottery_session',
        display_name="Public Lottery (dev)",
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

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

# Localization
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

INSTALLED_APPS = ['otree', 'mpl_japanese', 'publiclottery']

DEMO_PAGE_INTRO_HTML = """
Here are some oTree games."""