# coding: utf-8
import sys

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
CDN_DOMAIN = 'установить, если используется CDN'

# см. ALLOWED_HOSTS в конфигурации Django, необходимо переопределить со своими доменами и/или ip адресами
ALLOWED_HOSTS = ['the-tale.org',
                 '.the-tale.org']

OWNER = u'строка с ревизитами владельца сайта для пользовательского соглашения и футера сайта'

PAGE_TITLE = u'базовоый заголовок для страниц'

SECRET_KEY = 'ваш секретный ключ для некоторых частей фунциональности Django'

GA_CODE = 'идентификатор в google analytics'
ADDTHIS = 'идентификатор в addthis'
MAIL_RU = 'номер счётчика mail.ru'

SERVER_EMAIL = u'почта сервера'
ADMINS = () # перечень администраторов сайта (см. описание в конфигах Django)

EMAIL_NOREPLY = u'почта, которая будет писаться в письмах, на которые игроки не должны отвечать'
EMAIL_SUPPORT = u'почта службы подержки'
EMAIL_SUPPORT_SHORT = u'короткий адрес службы поддержки (только сама почта, без вставки имени и прочего)'


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
