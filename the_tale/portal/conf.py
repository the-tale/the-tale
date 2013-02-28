# coding: utf-8
import re

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
                               NEWS_ON_INDEX=3)
