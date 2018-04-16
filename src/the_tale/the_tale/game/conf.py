
import os

from dext.common.utils.app_settings import app_settings

from the_tale.game.balance import constants as c


APP_DIR = os.path.abspath(os.path.dirname(__file__))

game_settings = app_settings('GAME',

                             TURN_DELAY=c.TURN_DELTA,

                             ENABLE_WORKER_HIGHLEVEL=True,
                             ENABLE_WORKER_TURNS_LOOP=True,
                             ENABLE_WORKER_LONG_COMMANDS=True,
                             ENABLE_PVP=True,

                             ENABLE_DATA_REFRESH=True,

                             PROCESS_TURN_WAIT_LOGIC_TIMEOUT=5*60,
                             PROCESS_TURN_WAIT_HIGHLEVEL_TIMEOUT=10*60,

                             STOP_WAIT_TIMEOUT=20 * 60,

                             SAVED_UNCACHED_HEROES_FRACTION=0.00025,

                             JS_CONSTNATS_FILE_LOCATION=os.path.join(APP_DIR, '../static/game/data/constants.js'),

                             COLLECT_GARBAGE=True,
                             COLLECT_GARBAGE_PERIOD=20, # in turns
                             UNLOAD_OBJECTS=False,

                             GAME_STATE_KEY='game state',

                             INFO_API_VERSION='1.9',
                             DIARY_API_VERSION='1.0',
                             NAMES_API_VERSION='1.0',
                             HERO_HISTORY_API_VERSION='1.0',

                             SAVE_ON_EXCEPTION_TIMEOUT=60*60, # seconds

                             ENERGY_TRANSACTION_LIFETIME=24*60*60,
                             TT_ENERGY_BALANCE='http://localhost:10005/accounts/balance',
                             TT_ENERGY_START_TRANSACTION='http://localhost:10005/transactions/start',
                             TT_ENERGY_COMMIT_TRANSACTION='http://localhost:10005/transactions/commit',
                             TT_ENERGY_ROLLBACK_TRANSACTION='http://localhost:10005/transactions/rollback',
                             TT_ENERGY_DEBUG_CLEAR_SERVICE_URL='http://localhost:10005/debug-clear-service')
