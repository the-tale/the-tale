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
                  (re.compile(r'^/accounts/payments.*$'), 'shop'),
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

                               SETTINGS_PREV_CLEANING_RUN_TIME_KEY='prev cleaning run time',
                               CLEANING_RUN_TIME=2, # UTC time

                               SETTINGS_PREV_RATINGS_SYNC_TIME_KEY='prev ratings sync run time',
                               RATINGS_SYNC_DELAY=4*60*60,

                               SETTINGS_PREV_MIGHT_SYNC_TIME_KEY='prev might sync run time',
                               MIGHT_SYNC_DELAY=24*60*60,

                               SETTINGS_PREV_CDN_SYNC_TIME_KEY='prev cdn sync run time',
                               CDN_SYNC_DELAY=5*60,

                               SETTINGS_PREV_CURRENCIES_SYNC_TIME_KEY='prev currencies sync run time',
                               CURRENCIES_SYNC_DELAY=24*60*60,

                               PREMIUM_DAYS_FOR_HERO_OF_THE_DAY=30,

                               SETTINGS_PREV_REAL_DAY_STARTED_TIME_KEY='prev real day started',
                               REAL_DAY_STARTED_TIME=8, # UTC hourse

                               ENABLE_WORKER_LONG_COMMANDS=True,

                               SETTINGS_CDN_INFO_KEY='cdn info',
                               SETTINGS_CURRENCIES_INFO_KEY='currencies info',

                               AWS_ACCESS_KEY='amazon access key',
                               AWS_SECRET_KEY='amazon secret key',
                               AWS_S3_BACKUP_BUCKET='tale-backups',

                               LAST_BACKUP_PATH='/tmp/last_backup.gztar')
