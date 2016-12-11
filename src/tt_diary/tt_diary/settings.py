
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tt_diary',
        'USER': 'tt_diary',
        'PASSWORD': 'tt_diary',
        'HOST': '',
        'PORT': '',
    }
}

TIME_ZONE = 'UTC'

USE_I18N = True
USE_L10N = True

SECRET_KEY = 'asdjkadajklsdilasjfqwepdfqjdqpdjpsjda'

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

INSTALLED_APPS = ['tt_diary']
