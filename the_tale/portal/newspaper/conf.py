# coding: utf-8
import datetime

from dext.utils.app_settings import app_settings

newspaper_settings = app_settings('NEWSPAPER',
                                  FIRST_EDITION_DATE=datetime.datetime(2012, 10, 29)
    )
