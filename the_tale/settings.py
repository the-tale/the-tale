# coding: utf-8
import os
import sys

from dext.utils.meta_config import MetaConfig

TESTS_RUNNING = 'test' in sys.argv or 'testserver' in sys.argv

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
HOME_DIR = os.getenv("HOME")

META_CONFIG_FILE = os.path.join(PROJECT_DIR, 'meta_config.json')
meta_config = MetaConfig(config_path=META_CONFIG_FILE)

DEBUG = False

DEBUG_DATABASE_USAGE = False
DEBUG_DATABASE_USAGE_OUTPUT_DIR = '/tmp/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'the-tale',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

TIME_ZONE = 'UTC'

LANGUAGE_CODE = 'ru'

SITE_ID = 1
SITE_URL = None # MUST be defined in settings_local

X_FRAME_OPTIONS = 'DENY'

ALLOWED_HOSTS = ['.the-tale.org',
                 '.the-tale.com',
                 '164.138.29.80'] # ip to access the-tale.com

AUTH_USER_MODEL = 'accounts.Account'

##############################
# I18N
##############################

USE_I18N = True
USE_L10N = True

##############################
# static content settings
##############################

# MEDIA_ROOT = ''
# MEDIA_URL = ''

STATIC_URL = '/static/%s/' % meta_config.static_data_version
STATIC_DIR = os.path.join(PROJECT_DIR, 'static')

ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

DCONT_URL = '/dcont/'
DCONT_DIR = os.path.join(PROJECT_DIR, 'dcont')

LESS_CSS_URL = STATIC_URL + 'less/'
LESS_FILES_DIR = os.path.join(PROJECT_DIR, 'less')
LESS_DEST_DIR = os.path.join(PROJECT_DIR, 'static', 'css')

SECRET_KEY = 'i@oi33(3f0vlezy$aj3_3q%q=#fb1ehovw0k&==w3ycs+#5f)y'

GA_CODE = 'UA-10915391-4'
ADDTHIS = True

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

################################
# Mail settings
################################

SERVER_EMAIL = u'«Сказка»: системное сообщение <no-reply@the-tale.org>'
ADMINS = (('Tiendil', 'admin@the-tale.org'), )

EMAIL_NOREPLY = u'«Сказка» <no-reply@the-tale.org>'
EMAIL_SUPPORT = u'«Сказка» <support@the-tale.org>'
EMAIL_SUPPORT_SHORT = u'support@the-tale.org'

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

################################
# Other settings
################################

APPEND_SLASH = True
#PREPEND_WWW = True

AUTH_PROFILE_MODULE = 'accounts.Account'

#TODO: jinja
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    'dext.less.context_processors.less',
    'portal.context_processors.section',
    'game.balance.context_processors.balance',
    'game.bills.context_processors.bills_context'
    )


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'dext.settings.middleware.SettingsMiddleware',
    'accounts.middleware.RegistrationMiddleware'
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',

    'dext.less',
    'dext.settings',

    'common.utils',
    'common.postponed_tasks',

    'post_service',

    'accounts',
    'accounts.personal_messages',
    'accounts.friends',
    'accounts.payments',

    'guide',

    'portal',
    'portal.developers_info',

    'game',
    'game.angels',
    'game.abilities',
    'game.heroes',
    'game.actions',
    'game.quests',
    'game.map',
    'game.map.roads',
    'game.map.places',
    'game.artifacts',
    'game.mobs',
    'game.persons',
    'game.balance',
    'game.bills',
    'game.ratings',
    'game.pvp',
    'game.phrase_candidates',
    'game.chronicle',

    'cms',
    'cms.news',

    'forum',
    'blogs',

    'bank',
    'bank.dengionline',

    'south'
)

###############################
# AMQP
###############################

AMQP_BROKER_HOST = 'localhost'
AMQP_BROKER_USER = 'the-tale'
AMQP_BROKER_PASSWORD = 'the-tale'
AMQP_BROKER_VHOST = '/the-tale'

##############################
# code coverage tests
##############################

# TEST_RUNNER = 'django_coverage.coverage_runner.CoverageRunner'


################
# CACHING
################

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
CACHE_MIDDLEWARE_SECONDS = 24*60*60
CACHE_MIDDLEWARE_KEY_PREFIX = ''

try:
    from settings_local import *
except:
    pass

if 'TEMPLATE_DEBUG' not in globals():
    TEMPLATE_DEBUG = DEBUG

if not DEBUG:
    LESS_CSS_URL = STATIC_URL + 'css/'


AMQP_CONNECTION_URL = 'amqp://%s:%s@%s/%s' % (AMQP_BROKER_USER,
                                              AMQP_BROKER_PASSWORD,
                                              AMQP_BROKER_HOST,
                                              AMQP_BROKER_VHOST)


DEXT_PID_DIRECTORY = os.path.join(HOME_DIR, '.the-tale')

############################
# LOGGING
############################


def get_worker_log_file_handler(name):
    return {'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(HOME_DIR, 'logs', '%s.log' % name),
            'when': 'D',
            'interval': 7,
            'backupCount': 2*4,
            'encoding': 'utf-8',
            'formatter': 'verbose',
            'utc': True }

def get_worker_logger(name):
    return {'handlers': ['file_%s' % name],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': True }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '[%(levelname)s %(asctime)s %(module)s %(process)d] %(message)s'
        },
        'simple': {
            'format': '[%(levelname)s] %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
            },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
            },
        'file_quests': get_worker_log_file_handler('quests'),
        'file_game_supervisor': get_worker_log_file_handler('game_supervisor'),
        'file_game_logic': get_worker_log_file_handler('game_logic'),
        'file_game_highlevel': get_worker_log_file_handler('game_highlevel'),
        'file_game_turns_loop': get_worker_log_file_handler('game_turns_loop'),
        'file_game_might_calculator': get_worker_log_file_handler('game_might_calculator'),
        'file_portal_long_commands': get_worker_log_file_handler('portal_long_commands'),
        'file_game_pvp_balancer': get_worker_log_file_handler('game_pvp_balancer'),
        'file_accounts_registration': get_worker_log_file_handler('accounts_registration'),
        'file_accounts_accounts_manager': get_worker_log_file_handler('accounts_accounts_manager'),
        'file_post_service_message_sender': get_worker_log_file_handler('post_service_message_sender'),
        'file_bank_bank_processor': get_worker_log_file_handler('bank_bank_processor'),
        'file_bank_dengionline_banker': get_worker_log_file_handler('bank_dengionline_banker'),
        'file_postponed_tasks_refrigerator': get_worker_log_file_handler('postponed_tasks_refrigerator')
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'the-tale.workers': {
            'handlers': ['mail_admins', 'console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False
        },
        'the-tale.quests': get_worker_logger('quests'),
        'the-tale.workers.game_supervisor': get_worker_logger('game_supervisor'),
        'the-tale.workers.game_logic': get_worker_logger('game_logic'),
        'the-tale.workers.game_highlevel': get_worker_logger('game_highlevel'),
        'the-tale.workers.game_turns_loop': get_worker_logger('game_turns_loop'),
        'the-tale.workers.game_might_calculator': get_worker_logger('game_might_calculator'),
        'the-tale.workers.portal_long_commands': get_worker_logger('portal_long_commands'),
        'the-tale.workers.game_pvp_balancer': get_worker_logger('game_pvp_balancer'),
        'the-tale.workers.accounts_registration': get_worker_logger('accounts_registration'),
        'the-tale.workers.accounts_accounts_manager': get_worker_logger('accounts_accounts_manager'),
        'the-tale.workers.post_service_message_sender': get_worker_logger('post_service_message_sender'),
        'the-tale.workers.bank_bank_processor': get_worker_logger('bank_bank_processor'),
        'the-tale.workers.bank_dengionline_banker': get_worker_logger('bank_dengionline_banker'),
        'the-tale.workers.postponed_tasks_refrigerator': get_worker_logger('postponed_tasks_refrigerator')
    } if not TESTS_RUNNING else {}
}

try:
    from settings_check import *
except:
    pass
