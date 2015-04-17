# coding: utf-8
import datetime

from django.conf import settings as projects_settings

from dext.common.utils.app_settings import app_settings

from the_tale.game.balance import constants as c

heroes_settings = app_settings('HEROES',
                               USE_ABILITY_CHANCE=0.1,
                               MESSAGES_LOG_LENGTH=10,
                               DIARY_LOG_LENGTH=20,

                               MIN_PVP_BATTLES=25,

                               UI_CACHING_KEY='hero_ui_%d',
                               UI_CACHING_TIME=10*60, # not cache livetime, but time period after setupped ui_caching_started_at in which ui_caching is turned on
                               UI_CACHING_CONTINUE_TIME=60, # time before caching end, when we send next cache command
                               UI_CACHING_TIMEOUT=60, # cache livetime

                               DUMP_CACHED_HEROES=False, # should we dump cached heroes to database

                               START_ENERGY_BONUS=10,
                               MAX_HELPS_IN_TURN=10,

                               NAME_REGEX=ur'^[\-\ а-яА-Я«»\']+$' if not projects_settings.TESTS_RUNNING else ur'^[\-\ а-яА-Я«»\'\,]+$',
                               NAME_SYMBOLS_DESCRITION=u'пробел, -, а-я, А-Я, «», \' ',

                               NAME_MIN_LENGHT=3,

                               ABILITIES_RESET_TIMEOUT=datetime.timedelta(days=30),
                               PLACE_HELP_HISTORY_SIZE=200,
                               UNLOAD_TIMEOUT=c.TURN_DELTA * 3,
                               RARE_OPERATIONS_INTERVAL=1000,
                               INACTIVE_HERO_DELAY=int(10)  # для неактивных героев замедлять время в N раз
    )
