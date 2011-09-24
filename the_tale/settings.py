# coding: utf-8
import os

import djcelery

PROJECT_DIR = os.path.dirname(__file__)

DEBUG = False
DEBUG_DB = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'the_tale',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

#TODO: UTC
TIME_ZONE = 'America/Chicago'

LANGUAGE_CODE = 'en'

SITE_ID = 1

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

#STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')
STATIC_URL = '/static/'
STATICFILES_DIRS = ( os.path.join(PROJECT_DIR, 'static'), )

ADMIN_MEDIA_PREFIX = '/static/admin/'


LESS_CSS_URL = '/less/'
LESS_FILES_DIR = os.path.join(PROJECT_DIR, 'less')
LESS_DEST_DIR = os.path.join(PROJECT_DIR, 'static', 'css')


STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

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
    'django_next.less.context_processors.less'
    )


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
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
    'django.contrib.staticfiles', # TODO: remove if not in DEBUG mode

    'accounts',

    'game',
    'game.angels',
    'game.cards',
    'game.heroes',
    'game.turns',
    'game.actions',
    'game.journal_messages',
    'game.quests',
    'game.map',
    'game.map.roads',
    'game.map.places',
    'game.artifacts',

    'stress_testing',

    'south',
    'djcelery'
)

###############################
# Celery
###############################

BROKER_HOST = 'localhost'
BROKER_USER = 'the_tale'
BROKER_PASSWORD = 'the_tale'
BROKER_VHOST = '/the_tale_host'

CELERY_CREATE_MISSING_QUEUES = True

CELERY_ROUTES = [ { 'supervisor.cmd': {'queue': 'supervisor', 'routing_key': 'supervisor.cmd'}},
                  { 'game.cmd': {'queue': 'game', 'routing_key': 'game.cmd'}} ]

CELERY_QUEUES = {
    'supervisor': {
        'exchange': 'supervisor',
        'exchange_type': 'direct',
        'binding_key': 'supervisor.cmd'},
    'game': {
        'exchange': 'game',
        'exchange_type': 'direct',
        'binding_key': 'game.cmd'},
    'default': {
        'exchange': 'default',
        'exchange_type': 'direct',
        'routing_key': 'default',
        'binding_key': 'default'}
}

CELERY_DEFAULT_QUEUE = 'default'

try:
    from settings_local import *
except:
    pass

TEMPLATE_DEBUG = DEBUG


djcelery.setup_loader()
