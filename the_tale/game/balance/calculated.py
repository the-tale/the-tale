# coding: utf-8

from game.balance import formulas as f

##########################
# Характер

# предпочтения

CHARACTER_PREFERENCES_MOB_LEVEL_REQUIRED = 2 # на втором уровне
CHARACTER_PREFERENCES_PLACE_LEVEL_REQUIRED = f.lvl_after_time(24*7) # через неделю
CHARACTER_PREFERENCES_COMRADE_LEVEL_REQUIRED = f.lvl_after_time(24*14) # через две недели
CHARACTER_PREFERENCES_ENEMY_LEVEL_REQUIRED = f.lvl_after_time(24*30) # через месяц
