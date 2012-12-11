# coding: utf-8
import os
import re

from django.conf import settings as project_settings

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
                  (re.compile(r'^/game/ratings.*$'), 'community'),
                  (re.compile(r'^/game.*$'), 'game'),
                  (re.compile(r'^/guide.*$'), 'guide') )

portal_settings = app_settings('PORTAL',
                               DUMP_EMAIL='admin@the-tale.org',
                               META_CONFIG=os.path.join(project_settings.PROJECT_DIR, 'meta_config.json'),
                               FAQ_URL='http://the-tale.org/forum/threads/126',
                               BILLS_ON_INDEX=8,
                               FORUM_THREADS_ON_INDEX=5,
                               NEWS_ON_INDEX=3)
