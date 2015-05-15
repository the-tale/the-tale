# coding: utf-8

from django.conf import settings as project_settings

from dext.common.utils.app_settings import app_settings

bills_settings = app_settings('BILLS',
                              RATIONALE_MIN_LENGTH=100,
                              CHRONICLE_MIN_LENGTH=100 if not project_settings.TESTS_RUNNING else 5,
                              CHRONICLE_MAX_LENGTH=500,
                              MIN_VOTES_PERCENT=0.6,
                              BILL_LIVE_TIME=4*24*60*60,
                              BILL_ACTUAL_LIVE_TIME=30*24*60*60,
                              MINIMUM_BILL_OWNER_AGE=2, # IN DAYS
                              FORUM_CATEGORY_UID='bills',
                              BILLS_ON_PAGE=10,
                              BILLS_PROCESS_INTERVAL=60,
                              PLACES__TO_ACCESS_VOTING=10)
