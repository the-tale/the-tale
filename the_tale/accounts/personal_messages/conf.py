# coding: utf-8

import datetime

from dext.common.utils.app_settings import app_settings


settings = app_settings('PERSONAL_MESSAGES',
                        MESSAGES_ON_PAGE=10,
                        SYSTEM_MESSAGES_LEAVE_TIME=datetime.timedelta(seconds=2*7*24*60*60))
