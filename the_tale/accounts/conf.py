# coding: utf-8
import os
import datetime

from dext.utils.app_settings import app_settings


APP_DIR = os.path.abspath(os.path.dirname(__file__))


accounts_settings = app_settings('ACCOUNTS',
                                 SESSION_REGISTRATION_TASK_ID_KEY='accounts_registration_task_id',
                                 SESSION_REGISTRATION_REFERER_KEY='accounts_registration_referer_key',
                                 SESSION_REGISTRATION_REFERRAL_KEY='accounts_registration_referral_key',

                                 REFERRAL_URL_ARGUMENT='referral',

                                 FAST_REGISTRATION_USER_PASSWORD='password-FOR_fast-USERS',
                                 FAST_ACCOUNT_EXPIRED_TIME=3*24*60*60,
                                 REGISTRATION_TIMEOUT=1*60,
                                 RESET_PASSWORD_LENGTH=8,
                                 RESET_PASSWORD_TASK_LIVE_TIME=60*60,
                                 CHANGE_EMAIL_TIMEOUT=2*24*60*60,
                                 ACTIVE_STATE_TIMEOUT = 3*24*60*60,
                                 ACTIVE_STATE_REFRESH_PERIOD=3*60*60,
                                 SYSTEM_USER_NICK=u'Смотритель',

                                 ACCOUNTS_ON_PAGE=25,

                                 PREMIUM_EXPIRED_NOTIFICATION_IN=datetime.timedelta(days=3),

                                 SETTINGS_PREV_PREIMIUM_EXPIRED_NOTIFICATION_RUN_TIME_KEY = 'pref premium expired notification',
                                 PREMIUM_EXPIRED_NOTIFICATION_RUN_TIME=3, # UTC time

                                 CREATE_DEBUG_BANK_ACCOUNTS=False,

                                 INFORMER_SHOW=True,
                                 INFORMER_LINK=u'http://pubstomp.zz.mu/thetale/?id=%(account_id)d&type=4',
                                 INFORMER_CREATOR_ID=2557,
                                 INFORMER_CREATOR_NAME=u'Yashko',
                                 INFORMER_WIDTH=400,
                                 INFORMER_HEIGHT=50,
                                 INFORMER_FORUM_THREAD=515,

                                 NICK_REGEX=ur'[a-zA-Z0-9\-\ _а-яА-Я]+',
                                 NICK_MIN_LENGTH=3,
                                 NICK_MAX_LENGTH=30)
