# coding: utf-8
import os
from meta_config import meta_config

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

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

#TODO: UTC
TIME_ZONE = 'UTC'

LANGUAGE_CODE = 'ru'

SITE_ID = 1

X_FRAME_OPTIONS = 'DENY'

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
    'dext.less.context_processors.less'
    )


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'dext.utils.exceptions.ExceptionMiddleware'
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

    'common.utils',

    'accounts',

    'portal',

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
    'game.textgen',
    'game.balance',

    'cms',
    'cms.news',

    'forum',

    'stress_testing',

    'south'
)

###############################
# AMQP
###############################

AMQP_BROKER_HOST = 'localhost'
AMQP_BROKER_USER = 'the-tale'
AMQP_BROKER_PASSWORD = 'the-tale'
AMQP_BROKER_VHOST = '/the-tale'

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

try:
    from settings_check import *
except:
    pass
