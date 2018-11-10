
import smart_imports

smart_imports.all()


# NotImplemented settings MUST be defined in settings_local

TESTS_RUNNING = 'test' in sys.argv or 'testserver' in sys.argv

RUNSERVER_RUNNING = 'runserver' in sys.argv

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
HOME_DIR = os.getenv("HOME")

PROJECT_MODULE = os.path.basename(PROJECT_DIR)

META_CONFIG_FILE = os.path.join(PROJECT_DIR, 'meta_config.json')
META_CONFIG = dext_meta_config.MetaConfig(config_path=META_CONFIG_FILE)

DEBUG = False

SENTRY_RAVEN_CONFIG = None

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'the_tale',
        'USER': 'the_tale',
        'PASSWORD': 'the_tale',
        'HOST': '',
        'PORT': '',
        'CONN_MAX_AGE': 60 * 60  # close connection after an hour
    }
}

TIME_ZONE = 'UTC'

LANGUAGE_CODE = 'ru'

CSRF_FAILURE_VIEW = 'the_tale.urls.handlerCSRF'

CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True

SITE_ID = 1
SITE_URL = 'local.the-tale'

SOCIAL_VK_GROUP_URL = None
SOCIAL_TWITTER_GROUP_URL = None
SOCIAL_FACEBOOK_GROUP_URL = None

COMMUNITY_PROJECTS = []
SOCIAL_GITHUB_URL = 'https://github.com/the-tale'
SOCIAL_DOCUMENTATION = 'https://docs.the-tale.org'

CARDS_TUTORIAL = None
YOUTUBE_TUTORIAL = None

X_FRAME_OPTIONS = 'DENY'

ALLOWED_HOSTS = ['localhost',
                 'the-tale.org',
                 '.the-tale.org',
                 'local.the-tale',
                 '.local.the-tale']

AUTH_USER_MODEL = 'accounts.Account'

OWNER = 'Информация о владельце сайта'

PAGE_TITLE = 'Сказка'

API_CLIENT = 'the_tale-%s' % META_CONFIG.version

##############################
# I18N
##############################

USE_I18N = True
USE_L10N = True

SECRET_KEY = 'test secret key, must be replaced'

TT_SECRET = 'test.secret'

GA_CODE = None
ADDTHIS = None
MAIL_RU = None

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'


################################
# Mail settings
################################

SERVER_EMAIL = '«Сказка»: системное сообщение <no-reply@example.com>'
ADMINS = ()

EMAIL_NOREPLY = '«Сказка» <no-reply@example.com>'
EMAIL_SUPPORT = '«Сказка» <support@example.com>'
EMAIL_SUPPORT_SHORT = 'support@example.com'

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/emails'

################################
# Other settings
################################

APPEND_SLASH = True

TEMPLATES = [{'BACKEND': 'dext.common.utils.jinja2.Engine',
              'OPTIONS': {
                  'context_processors': ('django.contrib.auth.context_processors.auth',
                                         'django.template.context_processors.debug',
                                         'django.template.context_processors.i18n',
                                         'django.template.context_processors.media',
                                         'django.template.context_processors.static',
                                         'django.contrib.messages.context_processors.messages',
                                         'the_tale.portal.context_processors.section',
                                         'the_tale.portal.context_processors.cdn_paths',
                                         'the_tale.game.balance.context_processors.balance',
                                         'the_tale.game.bills.context_processors.bills_context',
                                         'the_tale.linguistics.context_processors.linguistics_context',
                                         'the_tale.guide.context_processors.guide_context',
                                         'the_tale.blogs.context_processors.blogs_context'
                                         ),
                  'directories': (os.path.join(PROJECT_DIR, 'templates'),),
                  'auto_reload': False,
                  'undefined': jinja2.StrictUndefined,
                  'autoescape': True,
                  'trim_blocks': True,
                  'extensions': ['jinja2.ext.loopcontrols']
              }},
             {'BACKEND': 'django.template.backends.django.DjangoTemplates',
              'APP_DIRS': True,
              'OPTIONS': {
                  'context_processors': ('django.contrib.auth.context_processors.auth',
                                         'django.template.context_processors.debug',
                                         'django.template.context_processors.i18n',
                                         'django.template.context_processors.media',
                                         'django.template.context_processors.static',
                                         'django.contrib.messages.context_processors.messages',
                                         'the_tale.portal.context_processors.section',
                                         'the_tale.portal.context_processors.cdn_paths',
                                         'the_tale.game.balance.context_processors.balance',
                                         'the_tale.game.bills.context_processors.bills_context',
                                         'the_tale.linguistics.context_processors.linguistics_context'
                                         ),
                  'debug': False
              }}
             ]


MIDDLEWARE = ('django.middleware.common.CommonMiddleware',
              'django.contrib.sessions.middleware.SessionMiddleware',
              'django.middleware.csrf.CsrfViewMiddleware',
              'django.contrib.auth.middleware.AuthenticationMiddleware',
              'django.contrib.messages.middleware.MessageMiddleware',
              'django.middleware.clickjacking.XFrameOptionsMiddleware',
              'dext.settings.middleware.SettingsMiddleware',
              'the_tale.accounts.middleware.RegistrationMiddleware',
              'the_tale.accounts.third_party.middleware.ThirdPartyMiddleware',
              'the_tale.accounts.middleware.FirstTimeVisitMiddleware')

ROOT_URLCONF = 'the_tale.urls'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',

    'dext.less',
    'dext.settings',
    'dext.forms',
    'dext.common.utils',
    'dext.common.amqp_queues',

    'the_tale.common.utils',
    'the_tale.common.postponed_tasks',
    'the_tale.common.meta_relations',

    'the_tale.post_service',

    'the_tale.accounts.third_party',  # MUST be before 'the_tale.accounts', since strange bug in Django 1.8, when model AccessToken placed in accounts application instead third_party
    'the_tale.accounts',
    'the_tale.accounts.personal_messages',
    'the_tale.accounts.friends',
    'the_tale.accounts.achievements',

    'the_tale.clans',

    'the_tale.guide',

    'the_tale.portal',
    'the_tale.portal.developers_info',

    'the_tale.game.chronicle',  # MUST be before game, since the same bug like with the_tale.accounts.third_party
    'the_tale.game',
    'the_tale.game.jobs',
    'the_tale.game.abilities',
    'the_tale.game.heroes',
    'the_tale.game.actions',
    'the_tale.game.quests',
    'the_tale.game.map',
    'the_tale.game.roads',
    'the_tale.game.places',
    'the_tale.game.artifacts',
    'the_tale.game.mobs',
    'the_tale.game.companions',
    'the_tale.game.persons',
    'the_tale.game.balance',
    'the_tale.game.bills',
    'the_tale.game.ratings',
    'the_tale.game.pvp',
    'the_tale.game.cards',
    'the_tale.game.politic_power',

    'the_tale.news',

    'the_tale.forum',
    'the_tale.blogs',
    'the_tale.collections',
    'the_tale.linguistics',

    'the_tale.finances.shop',
    'the_tale.finances.bank',
    'the_tale.finances.xsolla',

    'the_tale.statistics']


if TESTS_RUNNING:
    # argon password hasher print warnings on time of tests running, so replace it with more fast and more stable hasher
    PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
else:
    PASSWORD_HASHERS = ['django.contrib.auth.hashers.Argon2PasswordHasher',
                        'django.contrib.auth.hashers.PBKDF2PasswordHasher']

###############################
# AMQP
###############################

AMQP_BROKER_HOST = 'localhost'
AMQP_BROKER_USER = 'the_tale'
AMQP_BROKER_PASSWORD = 'the_tale'
AMQP_BROKER_VHOST = '/the_tale'

##############################
# tests
##############################

if TESTS_RUNNING:
    INSTALLED_APPS.append('test_without_migrations')

    # commented, to allow parallel testing
    # TEST_RUNNER = 'django_slowtests.DiscoverSlowestTestsRunner'
    # NUM_SLOW_TESTS = 10

################
# CACHING
################

CACHES = {'default': {'BACKEND': 'django_redis.cache.RedisCache',
                      'LOCATION': 'unix:///var/run/redis/redis.sock',
                      'OPTIONS': {
                          'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                          'SERIALIZER': 'django_redis.serializers.json.JSONSerializer'}}}


CACHE_MIDDLEWARE_SECONDS = 24 * 60 * 60
CACHE_MIDDLEWARE_KEY_PREFIX = ''

try:
    from the_tale.settings_local import *  # pylint: disable=W0403,W0401,W0614
except Exception:  # pylint: disable=W0702,W0703
    pass


if SENTRY_RAVEN_CONFIG:
    INSTALLED_APPS.append('raven.contrib.django.raven_compat')
    RAVEN_CONFIG = SENTRY_RAVEN_CONFIG


if RUNSERVER_RUNNING:
    INSTALLED_APPS.remove('django.contrib.staticfiles')


if TESTS_RUNNING:
    GAME_ENABLE_WORKER_HIGHLEVEL = True
    PVP_BALANCING_WITHOUT_LEVELS = False


if DEBUG:
    for template in TEMPLATES:
        if 'OPTIONS' in template:
            if 'auto_reload' in template['OPTIONS']:
                template['OPTIONS']['auto_reload'] = True
            if 'debug' in template['OPTIONS']:
                template['OPTIONS']['debug'] = True


AMQP_CONNECTION_URL = 'amqp://%s:%s@%s/%s' % (AMQP_BROKER_USER,
                                              AMQP_BROKER_PASSWORD,
                                              AMQP_BROKER_HOST,
                                              AMQP_BROKER_VHOST)


##############################
# static content settings
##############################

STATICFILES_DIRS = [os.path.join(PROJECT_DIR, 'static')]

STATIC_URL = '/static/%s/' % META_CONFIG.static_data_version

STATIC_ROOT = '/var/www/the_tale/static/%s/' % META_CONFIG.static_data_version

CDN_DOMAIN = globals().get('CDN_DOMAIN', 'static.the-tale.org')

STATIC_CDN = '//%s/static/%s/' % (CDN_DOMAIN, META_CONFIG.static_data_version)

ADMIN_MEDIA_PREFIX = '%sadmin/' % STATIC_URL

LESS_FILES_DIR = os.path.join(PROJECT_DIR, 'less')
LESS_DEST_DIR = os.path.join(PROJECT_DIR, 'static', 'css')

CDNS_ENABLED = globals().get('CDNS_ENABLED', False)

CDNS = (('STATIC_TWITTER_BOOTSTRAP',
         '%sbootstrap/' % STATIC_URL, '%sbootstrap/' % STATIC_CDN,
         'https:%sbootstrap/css/bootstrap.min.css' % STATIC_CDN),

        ('STATIC_CONTENT',
         STATIC_URL, STATIC_CDN,
         lambda: 'https:%simages/rss.png?_=%f' % (STATIC_CDN, time.time())),  # prevent url from caching for cases, when portal closed to 503
        )


############################
# LOGGING
############################

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
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose'
        },
        'sentry': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'formatter': 'verbose'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'django.server': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
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
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        }
    } if not TESTS_RUNNING else {}
}
