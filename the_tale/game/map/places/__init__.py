# coding: utf-8

from dext.utils.app_settings import app_settings

settings = app_settings('PLACES', 
                        POWER_HISTORY_LENGTH=14,
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

