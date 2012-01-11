# coding: utf-8

from django_next.utils.app_settings import app_settings

settings = app_settings('HEROES', 
                        USE_ABILITY_CHANCE=0.1,
                        MESSAGES_LOG_LENGTH=10)

