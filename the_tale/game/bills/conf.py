# coding: utf-8

from dext.utils.app_settings import app_settings

bills_settings = app_settings('BILLS',
                              RATIONALE_MIN_LENGTH=100,
                              MIN_VOTES_PERCENT=0.6,
                              BILL_LIVE_TIME = 4*24*60*60,
                              FORUM_CATEGORY_UID='bills',
                              BILLS_ON_PAGE=10,
                              BILLS_PROCESS_INTERVAL=60,
                              PLACES__TO_ACCESS_VOTING=10)
