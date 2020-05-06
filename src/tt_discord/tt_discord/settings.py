
import getpass

SERVICE_USER = getpass.getuser()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': SERVICE_USER,
        'USER': SERVICE_USER,
        'PASSWORD': SERVICE_USER,
        'HOST': '',
        'PORT': '',
    }
}

TIME_ZONE = 'UTC'

USE_I18N = True
USE_L10N = True

SECRET_KEY = 'd*awil6lu21jz5d)*2xo@spu!)%_886irkfln@ov!$x1$g+kz6'

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

INSTALLED_APPS = ['tt_discord']
