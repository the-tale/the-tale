# coding: utf-8
import re
import datetime

from django.core.urlresolvers import reverse_lazy

from dext.utils.app_settings import app_settings

SITE_SECTIONS = ( (re.compile(r'^/$'), 'index'),
                  (re.compile(r'^/news.*$'), 'news'),
                  (re.compile(r'^/forum.*$'), 'forum'),
                  (re.compile(r'^/accounts/auth.*$'), 'auth'),
                  (re.compile(r'^/accounts/profile.*$'), 'profile'),
                  (re.compile(r'^/accounts/messages.*$'), 'personal_messages'),
                  (re.compile(r'^/accounts/.*$'), 'community'),
                  (re.compile(r'^/game/heroes.*$'), 'hero'),
                  (re.compile(r'^/game/bills.*$'), 'world'),
                  (re.compile(r'^/game/phrase-candidates.*$'), 'world'),
                  (re.compile(r'^/game/chronicle.*$'), 'world'),
                  (re.compile(r'^/game/ratings.*$'), 'community'),
                  (re.compile(r'^/game/pvp/calls.*$'), 'community'),
                  (re.compile(r'^/game/map/'), 'map'),
                  (re.compile(r'^/game/map.*$'), None),
                  (re.compile(r'^/game.*$'), 'game'),
                  (re.compile(r'^/guide.*$'), 'guide') )

portal_settings = app_settings('PORTAL',
                               DUMP_EMAIL='admin@the-tale.org',
                               FAQ_URL=reverse_lazy('forum:threads:show', args=[126]),
                               ERRORS_URL=reverse_lazy('forum:subcategory', args=['erros']),
                               BILLS_ON_INDEX=4,
                               CHRONICLE_RECORDS_ON_INDEX=5,
                               FORUM_THREADS_ON_INDEX=5,
                               BLOG_POSTS_ON_INDEX=3,
                               SETTINGS_ACCOUNT_OF_THE_DAY_KEY='account of the day',
                               FIRST_EDITION_DATE=datetime.datetime(2012, 10, 29),
                               NEWS_ON_INDEX=3,

                               SETTINGS_PREV_CLEANING_RUN_TIME_KEY = 'prev cleaning run time',
                               CLEANING_RUN_TIME=2, # UTC time

                               SETTINGS_PREV_PREIMIUM_EXPIRED_NOTIFICATION_RUN_TIME_KEY = 'pref premium expired notification',
                               PREMIUM_EXPIRED_NOTIFICATION_RUN_TIME=3, # UTC time

                               SETTINGS_PREV_RATINGS_SYNC_TIME_KEY = 'prev ratings sync run time',
                               RATINGS_SYNC_DELAY=4*60*60, # UTC time

                               ENABLE_WORKER_LONG_COMMANDS=True
    )
