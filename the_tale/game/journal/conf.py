# coding: utf-8
import os

from dext.utils.app_settings import app_settings

APP_DIR = os.path.abspath(os.path.dirname(__file__))

journal_settings = app_settings('JOURNAL', 
                                TEXTS_DIRECTORY=os.path.join(APP_DIR, 'texts'),
                                PYMORPHY_DICTS_DIRECTORY=os.path.join(APP_DIR, 'dicts', 'ru_sqlite'))

