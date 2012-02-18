# coding: utf-8
import os

from dext.utils.app_settings import app_settings

APP_DIR = os.path.abspath(os.path.dirname(__file__))

mobs_settings = app_settings('MOBS', 
                             DEFS_DIRECTORY=os.path.join(APP_DIR, 'defs'))

