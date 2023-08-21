import os.path

DB_USER = 'op'
DB_PWD = 'op'
DB_DATABASE = 'drachdb2'
DB_HOST ='127.0.0.1'

DISABLE_AUTH = False
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'op.sqlite')

USERS = (
    (
        'admin',
        'pbkdf2:sha256:50000$qb7HDOK3$dea256b639a772db6440f447833fcc3cd1951bce1abd2d7216d2153a06ace3b4',
        'Joel Uckelman',
        'uckelman@nomic.net'
    ),
    (
        'posthorn',
        'pbkdf2:sha256:50000$rKxWJQRz$0cd783cdfa8494ba610c4974c31c3747b8ebeaab78e174217118f3011f93ba9a',
        'Posthorn',
        'posthorn@drachenwald.sca.org'
    ),
    (
        'signet',
        'pbkdf2:sha256:50000$RrV4YAQp$afa434495723c87755da12634f9b264ad0646980cceb5e7d93056a00fd6513dc',
        'Signet',
        'signet@drachenwald.sca.org'
    )
)
ARMORIAL_PATH="./arms"
GOOGLE_KEY_ID = ""
GOOGLE_KEY_SECRET = ""
