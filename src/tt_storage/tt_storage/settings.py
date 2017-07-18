
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tt_storage',
        'USER': 'tt_storage',
        'PASSWORD': 'tt_storage',
        'HOST': '',
        'PORT': '',
    }
}

TIME_ZONE = 'UTC'

USE_I18N = True
USE_L10N = True

SECRET_KEY = 'crr8fzog*np(9olw0hc!lp^wm9zg%v!s#m1u0qjd)2$qyi=j+l'

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

INSTALLED_APPS = ['tt_storage']
