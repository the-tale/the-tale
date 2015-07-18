# coding: utf-8
import sys

TESTS_RUNNING = 'test' in sys.argv or 'testserver' in sys.argv

DEBUG = 'runserver' in sys.argv

GAME_ENABLE_WORKER_HIGHLEVEL = True
GAME_ENABLE_PVP = True

GAME_ENABLE_WORKER_TURNS_LOOP = False
GAME_ENABLE_DATA_REFRESH = False

POST_SERVICE_ENABLE_MESSAGE_SENDER = False
PORTAL_ENABLE_WORKER_LONG_COMMANDS = False

PAYMENTS_ENABLE_REAL_PAYMENTS = False

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/emails'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'the-tale',
        'USER': '<USERNAME>',
        'PASSWORD': '<USERNAME>',
        'HOST': 'localhost',
        'PORT': '',
        'CONN_MAX_AGE': 0
    }
}

AMQP_BROKER_HOST = 'localhost'
AMQP_BROKER_USER = '<USERNAME>'
AMQP_BROKER_PASSWORD = '<USERNAME>'
AMQP_BROKER_VHOST = '/the-tale'

SITE_URL = 'localhost:8000'

GA_CODE = None
ADDTHIS = None
MAIL_RU = None

NEWRELIC_ENABLED = False
CDNS_ENABLED = False


if TESTS_RUNNING:
    PAYMENTS_ENABLE_REAL_PAYMENTS = True
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3'
            }
        }

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
            }
        }

    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.MD5PasswordHasher',
    )
