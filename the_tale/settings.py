# coding: utf-8
import os
import sys

from dext.common.utils.meta_config import MetaConfig

TESTS_RUNNING = 'test' in sys.argv or 'testserver' in sys.argv

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
HOME_DIR = os.getenv("HOME")

PROJECT_MODULE = os.path.basename(PROJECT_DIR)

META_CONFIG_FILE = os.path.join(PROJECT_DIR, 'meta_config.json')
META_CONFIG = MetaConfig(config_path=META_CONFIG_FILE)

DEBUG = False

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

CSRF_COOKIE_HTTPONLY = True
CSRF_FAILURE_VIEW = 'the_tale.urls.handlerCSRF'
SESSION_COOKIE_HTTPONLY = True

SITE_ID = 1
SITE_URL = None # MUST be defined in settings_local

SOCIAL_VK_GROUP_URL = 'http://vk.com/zpgtale'
SOCIAL_TWITTER_GROUP_URL = 'https://twitter.com/zpg_tale'
SOCIAL_FACEBOOK_GROUP_URL = 'https://www.facebook.com/groups/zpgtale/'

YOUTUBE_TUTORIAL = 'https://www.youtube.com/watch?v=P6oSC3zhcUQ'

X_FRAME_OPTIONS = 'DENY'

ALLOWED_HOSTS = ['the-tale.org',
                 '.the-tale.org',
                 'the-tale.com',
                 '.the-tale.com']

AUTH_USER_MODEL = 'accounts.Account'

OWNER = u'ИП Елецкий А.Н. УНП 291200954, юридический адрес: Беларусь Брестская обл. г. Барановичи ул. Кутузова д.4'
OWNER_SHORT = u'Елецкий Алексей (Tiendil)'
OWNER_COUNTRY = u'Республика Беларусь'

NEWRELIC_ENABLED = True
NEWRELIC_CONF_PATH = '/home/the-tale/conf/newrelic.ini'

API_CLIENT = 'the_tale-%s' % META_CONFIG.version

##############################
# I18N
##############################

USE_I18N = True
USE_L10N = True


SECRET_KEY = 'i@oi33(3f0vlezy$aj3_3q%q=#fb1ehovw0k&==w3ycs+#5f)y'

GA_CODE = 'UA-10915391-4'
ADDTHIS = True
MAIL_RU = True

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# TODO: switch to JSONSerializer (all current sessions will be lost if not converted to JSON)
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'


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
    'the_tale.portal.context_processors.section',
    'the_tale.portal.context_processors.cdn_paths',
    'the_tale.portal.context_processors.currencies',
    'the_tale.game.balance.context_processors.balance',
    'the_tale.game.bills.context_processors.bills_context',
    'the_tale.linguistics.context_processors.linguistics_context'
    )


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'dext.settings.middleware.SettingsMiddleware',
    'the_tale.accounts.middleware.RegistrationMiddleware',
    'the_tale.accounts.third_party.middleware.ThirdPartyMiddleware',
    'the_tale.accounts.middleware.FirstTimeVisitMiddleware'
)

ROOT_URLCONF = 'the_tale.urls'

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
    'dext.forms',
    'dext.common.utils',
    'dext.common.amqp_queues',

    'the_tale.common.utils',
    'the_tale.common.postponed_tasks',

    'the_tale.post_service',

    'the_tale.accounts',
    'the_tale.accounts.clans',
    'the_tale.accounts.personal_messages',
    'the_tale.accounts.friends',
    'the_tale.accounts.payments',
    'the_tale.accounts.achievements',
    'the_tale.accounts.third_party',

    'the_tale.guide',

    'the_tale.portal',
    'the_tale.portal.developers_info',

    'the_tale.game',
    'the_tale.game.angels',
    'the_tale.game.abilities',
    'the_tale.game.heroes',
    'the_tale.game.actions',
    'the_tale.game.quests',
    'the_tale.game.map',
    'the_tale.game.map.roads',
    'the_tale.game.map.places',
    'the_tale.game.artifacts',
    'the_tale.game.mobs',
    'the_tale.game.companions',
    'the_tale.game.persons',
    'the_tale.game.balance',
    'the_tale.game.bills',
    'the_tale.game.ratings',
    'the_tale.game.pvp',
    'the_tale.game.phrase_candidates',
    'the_tale.game.chronicle',
    'the_tale.game.cards',

    'the_tale.cms',
    'the_tale.cms.news',

    'the_tale.forum',
    'the_tale.blogs',
    'the_tale.collections',
    'the_tale.linguistics',

    'the_tale.bank',
    'the_tale.bank.xsolla',

    'the_tale.statistics',

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
        'OPTIONS': {'tcp_nodelay': True}
    }
}
CACHE_MIDDLEWARE_SECONDS = 24*60*60
CACHE_MIDDLEWARE_KEY_PREFIX = ''

try:
    from the_tale.settings_local import * # pylint: disable=W0403,W0401,W0614
except Exception: # pylint: disable=W0702,W0703
    pass

if 'TEMPLATE_DEBUG' not in globals():
    TEMPLATE_DEBUG = DEBUG


AMQP_CONNECTION_URL = 'amqp://%s:%s@%s/%s' % (AMQP_BROKER_USER,
                                              AMQP_BROKER_PASSWORD,
                                              AMQP_BROKER_HOST,
                                              AMQP_BROKER_VHOST)


DEXT_PID_DIRECTORY = os.path.join(HOME_DIR, '.the-tale')

##############################
# static content settings
##############################

STATIC_URL = '//%s/static/%s/' % (SITE_URL, META_CONFIG.static_data_version)

if 'STATIC_DIR' not in globals():
    STATIC_DIR = os.path.join(PROJECT_DIR, 'static')
STATIC_CDN = '//static.the-tale.org/static/%s/' % META_CONFIG.static_data_version
STATIC_DEBUG_URL = '/static/%s/' % META_CONFIG.static_data_version

ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
ADMIN_DEBUG_MEDIA_PREFIX = STATIC_DEBUG_URL + 'admin/'

DCONT_URL = '//%s/dcont/' % SITE_URL
if 'DCONT_DIR' not in globals():
    DCONT_DIR = os.path.join(PROJECT_DIR, 'dcont')
DCONT_CDN = '//static.the-tale.org%s' % DCONT_URL
DCONT_DEBUG_URL = '/dcont/'

LESS_FILES_DIR = os.path.join(PROJECT_DIR, 'less')
LESS_DEST_DIR = os.path.join(PROJECT_DIR, 'static', 'css')

if 'CDNS_ENABLED' not in globals():
    CDNS_ENABLED = False

CDNS = ( ('STATIC_JQUERY_JS',
          '%splugins/jquery/jquery-1.7.2.min.js' % STATIC_URL, '//yandex.st/jquery/1.7.2/jquery.min.js',
          'http://yandex.st/jquery/1.7.2/jquery.min.js'),
         ('STATIC_JQUERY_UI_JS',
          '%splugins/jquery/jquery-ui-1.8.9/js/jquery-ui-1.8.9.custom.min.js' % STATIC_URL, '//yandex.st/jquery-ui/1.8.9/jquery-ui.min.js',
          'http://yandex.st/jquery-ui/1.8.9/jquery-ui.min.js'),
         ('STATIC_TWITTER_BOOTSTRAP',
          '%sbootstrap/' % STATIC_URL, '%sbootstrap/' % STATIC_CDN,
          'http:%sbootstrap/css/bootstrap.min.css' % STATIC_CDN),

          # bootstrapcdn returns css not equal to our (media instructions missed)
          # '//netdna.bootstrapcdn.com/twitter-bootstrap/2.0.4/',
          # 'http://netdna.bootstrapcdn.com/twitter-bootstrap/2.0.4/css/bootstrap-combined.min.css'),

         ('STATIC_CONTENT',
          STATIC_URL, STATIC_CDN,
          'http:%simages/rss.png' % STATIC_CDN),

         ('DCONT_CONTENT',
          DCONT_URL, None,
          None)
    )



CURRENCIES_BASE = 'BYR'
CURRENCIES_LIST = ['BYR', 'RUB', 'UAH', 'USD']

############################
# LOGGING
############################


def get_worker_log_file_handler(name):
    return {'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(HOME_DIR, 'logs', '%s.log' % name),
            'when': 'D',
            'interval': 2,
            'backupCount': 2,
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
        'file_game_supervisor': get_worker_log_file_handler('game_supervisor'),
        'file_game_logic': get_worker_log_file_handler('game_logic'),
        'file_game_highlevel': get_worker_log_file_handler('game_highlevel'),
        'file_game_turns_loop': get_worker_log_file_handler('game_turns_loop'),
        'file_game_long_commands': get_worker_log_file_handler('game_long_commands'),
        'file_portal_long_commands': get_worker_log_file_handler('portal_long_commands'),
        'file_linguistics_manager': get_worker_log_file_handler('linguistics_manager'),
        'file_game_pvp_balancer': get_worker_log_file_handler('game_pvp_balancer'),
        'file_game_quests': get_worker_log_file_handler('game_quests'),
        'file_linguistics': get_worker_log_file_handler('linguistics'),
        'file_accounts_registration': get_worker_log_file_handler('accounts_registration'),
        'file_accounts_accounts_manager': get_worker_log_file_handler('accounts_accounts_manager'),
        'file_achievements_achievements_manager': get_worker_log_file_handler('achievements_achievements_manager'),
        'file_collections_items_manager': get_worker_log_file_handler('collections_items_manager'),
        'file_post_service_message_sender': get_worker_log_file_handler('post_service_message_sender'),
        'file_bank_bank_processor': get_worker_log_file_handler('bank_bank_processor'),
        'file_bank_xsolla_banker': get_worker_log_file_handler('bank_xsolla_banker'),
        'file_bank_xsolla_requests': get_worker_log_file_handler('bank_xsolla_requests'),
        'file_postponed_tasks_refrigerator': get_worker_log_file_handler('postponed_tasks_refrigerator')
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'the-tale': {
            'handlers': ['mail_admins', 'console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False
        },
        'the-tale.workers.game_supervisor': get_worker_logger('game_supervisor'),
        'the-tale.workers.game_logic': get_worker_logger('game_logic'),
        'the-tale.workers.game_highlevel': get_worker_logger('game_highlevel'),
        'the-tale.workers.game_turns_loop': get_worker_logger('game_turns_loop'),
        'the-tale.workers.game_long_commands': get_worker_logger('game_long_commands'),
        'the-tale.workers.portal_long_commands': get_worker_logger('portal_long_commands'),
        'the-tale.workers.linguistics_manager': get_worker_logger('linguistics_manager'),
        'the-tale.workers.game_pvp_balancer': get_worker_logger('game_pvp_balancer'),
        'the-tale.workers.accounts_registration': get_worker_logger('accounts_registration'),
        'the-tale.workers.accounts_accounts_manager': get_worker_logger('accounts_accounts_manager'),
        'the-tale.workers.achievements_achievements_manager': get_worker_logger('achievements_achievements_manager'),
        'the-tale.workers.collections_items_manager': get_worker_logger('collections_items_manager'),
        'the-tale.workers.post_service_message_sender': get_worker_logger('post_service_message_sender'),
        'the-tale.workers.bank_bank_processor': get_worker_logger('bank_bank_processor'),
        'the-tale.workers.bank_xsolla_banker': get_worker_logger('bank_xsolla_banker'),
        'the-tale.bank_xsolla_requests': get_worker_logger('bank_xsolla_requests'),
        'the-tale.workers.postponed_tasks_refrigerator': get_worker_logger('postponed_tasks_refrigerator'),
        'the-tale.game.quests': get_worker_logger('game_quests'),
        'the-tale.linguistics': get_worker_logger('linguistics')
    } if not TESTS_RUNNING else {}
}
