# coding: utf-8

from dext.utils.app_settings import app_settings

from game.balance import constants as c

places_settings = app_settings('PLACES',
                               POWER_HISTORY_LENGTH=2*7*24*c.TURNS_IN_HOUR,
                               MAX_SIZE=10,
                               MAX_DESCRIPTION_LENGTH=1000,
                               SIZE_TO_PERSONS_NUMBER={0: 2,
                                                       1: 2,
                                                       2: 3,
                                                       3: 3,
                                                       4: 3,
                                                       5: 4,
                                                       6: 4,
                                                       7: 4,
                                                       8: 5,
                                                       9: 5,
                                                       10: 6} )
