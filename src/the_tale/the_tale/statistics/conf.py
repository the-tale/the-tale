# coding: utf-8
import os
import datetime

from django.conf import settings as project_settings

from dext.common.utils.app_settings import app_settings


statistics_settings = app_settings('STATISTICS',
                                   START_DATE=datetime.datetime(year=2012, month=6, day=27),
                                   PAYMENTS_START_DATE=datetime.datetime(year=2013, month=8, day=1))
