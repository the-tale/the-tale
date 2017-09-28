
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tt_market',
        'USER': 'tt_market',
        'PASSWORD': 'tt_market',
        'HOST': '',
        'PORT': '',
    }
}

TIME_ZONE = 'UTC'

USE_I18N = True
USE_L10N = True

SECRET_KEY = 'd*awil6lu21jz5d)*2xo@spu!)%_886irkfln@ov!$x1$g+kz6'

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

INSTALLED_APPS = ['tt_market']
