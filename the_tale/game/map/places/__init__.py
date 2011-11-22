# coding: utf-8

from django_next.utils.app_settings import app_settings

settings = app_settings('PLACES', 
                        POWER_HISTORY_LENGTH=14,
                        MAX_SIZE=10,
                        PERSON_ON_SIZE_1=2)

