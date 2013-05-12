# coding: utf-8

from dext.utils.app_settings import app_settings

heroes_settings = app_settings('HEROES',
                               USE_ABILITY_CHANCE=0.1,
                               MESSAGES_LOG_LENGTH=10,
                               DIARY_LOG_LENGTH=10,
                               UI_CACHING_KEY='heroe_ui_%d',
                               # not cache livetime, but time period after setupped ui_caching_started_at in which ui_caching is turned on
                               UI_CACHING_TIME=10*60,
                               # and this is cache live time (it must be greate then c.TURN_DELTA)
                               UI_CACHING_TIMEOUT=60,
                               PLACE_HELP_HISTORY_SIZE=200)
