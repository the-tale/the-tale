# coding: utf-8

from dext.utils.app_settings import app_settings

from game.balance import constants as c

places_settings = app_settings('PLACES',
                               POWER_HISTORY_LENGTH=2*7*24*c.TURNS_IN_HOUR,
                               MAX_SIZE=10,
                               SIZE_TO_PERSONS_NUMBER={0: 1,
                                                       1: 1,
                                                       2: 2,
                                                       3: 2,
                                                       4: 2,
                                                       5: 3,
                                                       6: 3,
                                                       7: 3,
                                                       8: 4,
                                                       9: 4,
                                                       10: 5} )
