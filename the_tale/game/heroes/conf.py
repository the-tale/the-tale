# coding: utf-8

from dext.utils.app_settings import app_settings

heroes_settings = app_settings('HEROES', 
                               USE_ABILITY_CHANCE=0.1,
                               MESSAGES_LOG_LENGTH=10)

