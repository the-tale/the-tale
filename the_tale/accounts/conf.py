# coding: utf-8
import os
import datetime

from dext.common.utils.app_settings import app_settings


APP_DIR = os.path.abspath(os.path.dirname(__file__))


accounts_settings = app_settings('ACCOUNTS',
                                 SESSION_REGISTRATION_TASK_ID_KEY='accounts_registration_task_id',
                                 SESSION_REGISTRATION_REFERER_KEY='accounts_registration_referer_key',
                                 SESSION_REGISTRATION_REFERRAL_KEY='accounts_registration_referral_key',
                                 SESSION_REGISTRATION_ACTION_KEY='accounts_registration_action_key',

                                 SESSION_FIRST_TIME_VISIT_VISITED_KEY = 'first_time_visite_visited',
                                 SESSION_FIRST_TIME_VISIT_KEY = 'first_time_visite',

                                 SESSION_REMEMBER_TIME=365*24*60*60,

                                 REFERRAL_URL_ARGUMENT='referral',
                                 ACTION_URL_ARGUMENT='action',

                                 FORUM_COMPLAINT_THEME='/forum/threads/1177',


                                 FAST_REGISTRATION_USER_PASSWORD='password-FOR_fast-USERS',
                                 FAST_ACCOUNT_EXPIRED_TIME=3*24*60*60,
                                 REGISTRATION_TIMEOUT=1*60,
                                 RESET_PASSWORD_LENGTH=8,
                                 RESET_PASSWORD_TASK_LIVE_TIME=60*60,
                                 CHANGE_EMAIL_TIMEOUT=2*24*60*60,
                                 ACTIVE_STATE_TIMEOUT = 3*24*60*60,
                                 ACTIVE_STATE_REFRESH_PERIOD=3*60*60,
                                 SYSTEM_USER_NICK=u'Смотритель',
                                 DEVELOPERS_IDS=[1, 1022],

                                 ACCOUNTS_ON_PAGE=25,

                                 PREMIUM_EXPIRED_NOTIFICATION_IN=datetime.timedelta(days=3),
                                 PREMIUM_INFINIT_TIMEOUT=datetime.timedelta(days=100*365),

                                 RANDOM_PREMIUM_CREATED_AT_BARRIER=datetime.timedelta(days=7),

                                 SETTINGS_PREV_PREIMIUM_EXPIRED_NOTIFICATION_RUN_TIME_KEY = 'pref premium expired notification',
                                 PREMIUM_EXPIRED_NOTIFICATION_RUN_TIME=3, # UTC time

                                 CREATE_DEBUG_BANK_ACCOUNTS=False,

                                 INFORMER_SHOW=True,
                                 INFORMER_LINK=u'http://informer.the-tale.org/?id=%(account_id)d&type=4',
                                 INFORMER_CREATOR_ID=2557,
                                 INFORMER_CREATOR_NAME=u'Yashko',
                                 INFORMER_WIDTH=400,
                                 INFORMER_HEIGHT=50,
                                 INFORMER_FORUM_THREAD=515,

                                 NICK_REGEX=ur'^[a-zA-Z0-9\-\ _а-яА-Я]+$',
                                 NICK_MIN_LENGTH=3,
                                 NICK_MAX_LENGTH=30,

                                 RESET_NICK_PREFIX=u'имя игрока сброшено',

                                 BOT_EMAIL_TEMPLATE='bot_%d@the-tale.org',
                                 BOT_PASSWORD='password-Bots',
                                 BOT_NICK_TEMPLATE=u'Существо №%d',
                                 BOT_HERO_NAME_FORMS=[u'Существо', u'Существа', u'Существу', u'Существо', u'Существом', u'Существе',
                                                      u'Существа', u'Существ', u'Существам', u'Существ', u'Существами', u'Существах'],
                                 BOT_HERO_NAME_PROPERTIES=(u'ср', ),

                                 MAX_ACCOUNT_DESCRIPTION_LENGTH=10000)
