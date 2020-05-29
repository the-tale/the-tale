
import smart_imports

smart_imports.all()


NAME_REGEX = r'^[\-\ а-яА-Я«»\'ёЁ]+$' if not django_settings.TESTS_RUNNING else r'^[\-\ а-яА-Я«»\'\,ёЁ]+$'


settings = utils_app_settings.app_settings('HEROES',
                                           USE_ABILITY_CHANCE=0.1,
                                           MESSAGES_LOG_LENGTH=10,
                                           DIARY_LOG_LENGTH=20,
                                           DIARY_LOG_LENGTH_PREMIUM=50,

                                           MIN_PVP_BATTLES=25,

                                           UI_CACHING_KEY='hero_ui_%d',

                                           # not cache livetime, but time period after setupped ui_caching_started_at
                                           # in which ui_caching is turned on
                                           UI_CACHING_TIME=10 * 60,

                                           # time before caching end, when we send next cache command
                                           UI_CACHING_CONTINUE_TIME=60,

                                           # cache livetime
                                           UI_CACHING_TIMEOUT=60,

                                           # should we dump cached heroes to database
                                           DUMP_CACHED_HEROES=False,

                                           START_ENERGY_BONUS=10,
                                           MAX_HELPS_IN_TURN=10,

                                           NAME_REGEX=NAME_REGEX,
                                           NAME_SYMBOLS_DESCRITION='пробел, -, а-я, А-Я, «», \' ',

                                           NAME_MIN_LENGHT=3,

                                           ABILITIES_RESET_TIMEOUT=datetime.timedelta(days=30),
                                           UNLOAD_TIMEOUT=c.TURN_DELTA * 3,
                                           RARE_OPERATIONS_INTERVAL=1000,
                                           INACTIVE_HERO_DELAY=int(10),  # для неактивных героев замедлять время в N раз
                                           POWER_PER_ACTIVE_BILL=1.5,
                                           ACTIVE_BILLS_MAXIMUM=4,

                                           TT_DIARY_ENTRY_POINT='http://localhost:10001/',

                                           MAX_HERO_DESCRIPTION_LENGTH=10000,

                                           REMOVE_HERO_DELAY=10*60)
