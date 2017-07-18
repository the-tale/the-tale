
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tt_personal_messages',
        'USER': 'tt_personal_messages',
        'PASSWORD': 'tt_personal_messages',
        'HOST': '',
        'PORT': '',
    }
}

TIME_ZONE = 'UTC'

USE_I18N = True
USE_L10N = True

SECRET_KEY = '2aosfz)qnym7x0367)@ow=w-c&#vq%yuascum21ml*p@cy4b6&'

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

INSTALLED_APPS = ['tt_personal_messages']
