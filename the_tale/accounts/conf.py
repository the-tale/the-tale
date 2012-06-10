# coding: utf-8
import os

from dext.utils.app_settings import app_settings


APP_DIR = os.path.abspath(os.path.dirname(__file__))


accounts_settings = app_settings('ACCOUNTS',
                                 SESSION_REGISTRATION_TASK_ID_KEY='registration_task_id',
                                 SESSION_REGISTRATION_TASK_STATE_KEY='registration_task_state',
                                 FAST_REGISTRATION_USER_PASSWORD='password-FOR_fast-USERS',
                                 FAST_ACCOUNT_EXPIRED_TIME=3*24*60*60,
                                 REGISTRATION_TIMEOUT=1*60,
                                 CHANGE_EMAIL_TIMEOUT=2*24*60*60)
