# coding: utf-8

from dext.utils.app_settings import app_settings

game_settings = app_settings('GAME',
                             TURN_DELAY=10,

                             ENABLE_WORKER_HIGHLEVEL=True,
                             ENABLE_WORKER_TURNS_LOOP=True)
