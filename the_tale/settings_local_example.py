# coding: utf-8
import sys
import os
import getpass

# Всё что указано в settings.py как NotImplemented должно быть определено в settings_local.py

TESTS_RUNNING = 'test' in sys.argv or 'testserver' in sys.argv

DEBUG = 'runserver' in sys.argv

GAME_ENABLE_WORKER_HIGHLEVEL = True # включить фонового рабочего, отвечающего за расчёт карты и влияния
GAME_ENABLE_PVP = True # включить фонового рабочего, отвечающего за PvP

GAME_ENABLE_WORKER_TURNS_LOOP = False # включить фонового рабочего, отвечающего за инициацию расчёта ходов
GAME_ENABLE_DATA_REFRESH = False # разрешить странице игры автоматически ходить за новым ходом (полезно отключать, если идёт отладка её скриптов)

POST_SERVICE_ENABLE_MESSAGE_SENDER = False # включить фоновый сервис отправки электронных писем
PORTAL_ENABLE_WORKER_LONG_COMMANDS = False # включить фоновый сервис, выполняющий длительные сервисныекоманды

PAYMENTS_ENABLE_REAL_PAYMENTS = False

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/emails'

CURRENT_USER = getpass.getuser()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('THE_TALE_DB', 'the_tale'),
        'USER': os.environ.get('THE_TALE_DB_USER', CURRENT_USER),
        'PASSWORD': os.environ.get('THE_TALE_DB_PASSWORD', CURRENT_USER),
        'HOST': 'localhost',
        'PORT': '',
        'CONN_MAX_AGE': 0
    }
}

AMQP_BROKER_HOST = 'localhost'
AMQP_BROKER_USER = os.environ.get('THE_TALE_AMQP_USER', CURRENT_USER)
AMQP_BROKER_PASSWORD = os.environ.get('THE_TALE_AMQP_PASSWORD', CURRENT_USER)
AMQP_BROKER_VHOST = os.environ.get('THE_TALE_AMQP_VHOST', '/the_tale')

SITE_URL = 'localhost:8000'

NEWRELIC_ENABLED = False
CDNS_ENABLED = False
CDN_DOMAIN = None # установить, если используется CDN

# см. ALLOWED_HOSTS в конфигурации Django, необходимо переопределить со своими доменами и/или ip адресами
ALLOWED_HOSTS = ['the-tale.org',
                 '.the-tale.org']

OWNER = u'' # строка с ревизитами владельца сайта для пользовательского соглашения и футера сайта

PAGE_TITLE = u'' # базовоый заголовок для страниц

SECRET_KEY = u'!@#1231' # ваш УНИКАЛЬНЫЙ секретный ключ для некоторых частей фунциональности Django

GA_CODE = None # идентификатор в google analytics
ADDTHIS = None # идентификатор в addthis
MAIL_RU = None # номер счётчика mail.ru

SERVER_EMAIL = u'' # почта сервера
ADMINS = () # перечень администраторов сайта (см. описание в конфигах Django)

EMAIL_NOREPLY = u'no-reply@example.com'  # почта, которая будет писаться в письмах, на которые игроки не должны отвечать
EMAIL_SUPPORT = u'' # почта службы подержки
EMAIL_SUPPORT_SHORT = u'' # короткий адрес службы поддержки (только сама почта, без вставки имени и прочего)


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
