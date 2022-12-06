import os.path

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'op.sqlite')

DISABLE_AUTH = False

USERS = (
    (
        'loginname',
        'encrypted_key',
        'name',
        'email@domain.com'
    ),
    (
        'loginname',
        'encrypted_key',
        'Posthorn',
        'email@domain.com'
    ),
    (
        'loginname',
        'encrypted_key',
        'Signet',
        'email@domain.com'
    )
)
