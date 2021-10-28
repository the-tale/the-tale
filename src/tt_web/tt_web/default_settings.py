
import os

from tt_web import utils


tt_config = utils.load_config(os.environ['TT_CONFIG'])


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': tt_config['database']['name'],
        'USER': tt_config['database']['user'],
        'PASSWORD': tt_config['database']['password'],
        'HOST': tt_config['database']['host'],
        'PORT': tt_config['database']['port'],
    }
}

TIME_ZONE = 'UTC'

USE_I18N = True
USE_L10N = True

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

SECRET_KEY = tt_config['django']['secret_key']
