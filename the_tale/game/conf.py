# coding: utf-8
import os

from dext.utils.app_settings import app_settings


APP_DIR = os.path.abspath(os.path.dirname(__file__))


game_settings = app_settings('GAME',
                             TURN_DELAY=10,

                             ENABLE_WORKER_HIGHLEVEL=True,
                             ENABLE_WORKER_TURNS_LOOP=True,

                             TEXTGEN_SOURCES_DIR=os.path.join(APP_DIR, 'fixtures', 'textgen', 'texts_src'),
                             TEXTGEN_VOCABULARY=os.path.join(APP_DIR, 'fixtures', 'textgen', 'vocabulary.json'),
                             TEXTGEN_STORAGE_VOCABULARY=os.path.join(APP_DIR, 'fixtures', 'textgen', 'storage', 'vocabulary.json'),
                             TEXTGEN_STORAGE_DICTIONARY=os.path.join(APP_DIR, 'fixtures', 'textgen', 'storage', 'dictionary.json') )
