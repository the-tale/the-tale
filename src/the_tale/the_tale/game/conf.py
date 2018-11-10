
import smart_imports

smart_imports.all()


APP_DIR = os.path.abspath(os.path.dirname(__file__))


settings = dext_app_settings.app_settings('GAME',

                                          TURN_DELAY=c.TURN_DELTA,

                                          ENABLE_WORKER_HIGHLEVEL=True,
                                          ENABLE_WORKER_TURNS_LOOP=True,
                                          ENABLE_WORKER_LONG_COMMANDS=True,
                                          ENABLE_PVP=True,

                                          ENABLE_DATA_REFRESH=True,

                                          PROCESS_TURN_WAIT_LOGIC_TIMEOUT=5 * 60,
                                          PROCESS_TURN_WAIT_HIGHLEVEL_TIMEOUT=10 * 60,

                                          STOP_WAIT_TIMEOUT=20 * 60,

                                          SAVED_UNCACHED_HEROES_FRACTION=0.00025,

                                          JS_CONSTNATS_FILE_LOCATION=os.path.join(APP_DIR, '../static/game/data/constants.js'),

                                          COLLECT_GARBAGE=True,
                                          COLLECT_GARBAGE_PERIOD=20,
                                          UNLOAD_OBJECTS=False,

                                          GAME_STATE_KEY='game state',

                                          INFO_API_VERSION='1.9',
                                          DIARY_API_VERSION='1.0',
                                          NAMES_API_VERSION='1.0',
                                          HERO_HISTORY_API_VERSION='1.0',

                                          SAVE_ON_EXCEPTION_TIMEOUT=60 * 60,

                                          ENERGY_TRANSACTION_LIFETIME=24 * 60 * 60,

                                          TT_ENERGY_ENTRY_POINT='http://localhost:10005/',

                                          TT_IMPACTS_PERSONAL_ENTRY_POINT='http://localhost:10007/',
                                          TT_IMPACTS_CROWD_ENTRY_POINT='http://localhost:10008/',
                                          TT_IMPACTS_JOB_ENTRY_POINT='http://localhost:10009/',
                                          TT_IMPACTS_FAME_ENTRY_POINT='http://localhost:10010/')
