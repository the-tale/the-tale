# coding: utf-8
import os

from dext.utils.app_settings import app_settings

from game.balance import constants as c


APP_DIR = os.path.abspath(os.path.dirname(__file__))


game_settings = app_settings('GAME',

                             TURN_DELAY=c.TURN_DELTA,

                             ENABLE_WORKER_HIGHLEVEL=True,
                             ENABLE_WORKER_TURNS_LOOP=True,
                             ENABLE_WORKER_LONG_COMMANDS=True,
                             ENABLE_PVP=True,

                             ENABLE_DATA_REFRECH=True,

                             PROCESS_TURN_WAIT_LOGIC_TIMEOUT = 5*60,
                             PROCESS_TURN_WAIT_HIGHLEVEL_TIMEOUT = 10*60,

                             SAVED_UNCACHED_HEROES_FRACTION=0.01,

                             JS_CONSTNATS_FILE_LOCATION='./static/game/data/constants.js',

                             TEXTGEN_SOURCES_DIR=os.path.join(APP_DIR, 'fixtures', 'textgen', 'texts_src'),
                             TEXTGEN_VOCABULARY=os.path.join(APP_DIR, 'fixtures', 'textgen', 'vocabulary.json'),
                             TEXTGEN_STORAGE_VOCABULARY=os.path.join(APP_DIR, 'fixtures', 'textgen', 'storage', 'vocabulary.json'),
                             TEXTGEN_STORAGE_DICTIONARY=os.path.join(APP_DIR, 'fixtures', 'textgen', 'storage', 'dictionary.json'),
                             TEXTGEN_STORAGE_PHRASES_TYPES=os.path.join(APP_DIR, 'fixtures', 'textgen', 'storage', 'phrases_types.json')    )
