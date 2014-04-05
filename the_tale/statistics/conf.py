# coding: utf-8
import os
import datetime

from django.conf import settings as project_settings

from dext.utils.app_settings import app_settings


GEN_DATA_DIR = os.path.join(project_settings.DCONT_DIR, './statistics/')

statistics_settings = app_settings('STATISTICS',
                                   START_DATE=datetime.datetime(year=2012, month=6, day=27),
                                   PAYMENTS_START_DATE=datetime.datetime(year=2013, month=8, day=1),
                                   JS_DATA_FILE_LOCATION=os.path.join(GEN_DATA_DIR, './data-%s.js'),
                                   JS_DATA_FILE_URL='/dcont/statistics/data-%s.js',
                                   JS_DATA_FILE_VERSION_KEY='statistic version')
