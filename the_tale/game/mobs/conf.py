# coding: utf-8
import os

from dext.utils.app_settings import app_settings

APP_DIR = os.path.abspath(os.path.dirname(__file__))

mobs_settings = app_settings('MOBS',
                             MOBS_STORAGE=os.path.join(APP_DIR, 'fixtures', 'mobs.xls'),
                             TEST_STORAGE=os.path.join(APP_DIR, 'fixtures', 'test.xls'))
