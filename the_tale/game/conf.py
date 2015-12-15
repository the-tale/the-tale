# coding: utf-8
import os
import math

from dext.common.utils.app_settings import app_settings

from the_tale.game.balance import constants as c


APP_DIR = os.path.abspath(os.path.dirname(__file__))

POWER_HISTORY_WEEKS = 8
POWER_RECALCULATE_STEPS = float(POWER_HISTORY_WEEKS*7*24*c.TURNS_IN_HOUR) / c.MAP_SYNC_TIME
POWER_REDUCE_FRACTION = float(math.pow(0.01, 1.0 / POWER_RECALCULATE_STEPS))

game_settings = app_settings('GAME',

                             TURN_DELAY=c.TURN_DELTA,

                             ENABLE_WORKER_HIGHLEVEL=True,
                             ENABLE_WORKER_TURNS_LOOP=True,
                             ENABLE_WORKER_LONG_COMMANDS=True,
                             ENABLE_PVP=True,

                             POWER_HISTORY_WEEKS=POWER_HISTORY_WEEKS,
                             POWER_REDUCE_FRACTION=POWER_REDUCE_FRACTION,

                             ENABLE_DATA_REFRESH=True,

                             PROCESS_TURN_WAIT_LOGIC_TIMEOUT = 5*60,
                             PROCESS_TURN_WAIT_HIGHLEVEL_TIMEOUT = 10*60,

                             STOP_WAIT_TIMEOUT = 20 * 60,

                             SAVED_UNCACHED_HEROES_FRACTION=0.00025,

                             JS_CONSTNATS_FILE_LOCATION='./the_tale/static/game/data/constants.js',

                             COLLECT_GARBAGE=True,
                             COLLECT_GARBAGE_PERIOD=20, # in turns
                             UNLOAD_OBJECTS=False,

                             GAME_STATE_KEY='game state',

                             INFO_API_VERSION='1.4',

                             SAVE_ON_EXCEPTION_TIMEOUT=60*60, # seconds

                             TEXTGEN_SOURCES_DIR=os.path.join(APP_DIR, 'fixtures', 'textgen', 'texts_src'),
                             TEXTGEN_VOCABULARY=os.path.join(APP_DIR, 'fixtures', 'textgen', 'vocabulary.json'),
                             TEXTGEN_STORAGE_VOCABULARY=os.path.join(APP_DIR, 'fixtures', 'textgen', 'storage', 'vocabulary.json'),
                             TEXTGEN_STORAGE_DICTIONARY=os.path.join(APP_DIR, 'fixtures', 'textgen', 'storage', 'dictionary.json'),
                             TEXTGEN_STORAGE_PHRASES_TYPES=os.path.join(APP_DIR, 'fixtures', 'textgen', 'storage', 'phrases_types.json')    )
