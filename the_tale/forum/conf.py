# coding: utf-8

from dext.utils.app_settings import app_settings

forum_settings = app_settings('FORUM',
                              POSTS_ON_PAGE=15,
                              THREADS_ON_PAGE=15,
                              MODERATOR_GROUP_NAME='forum moderators group',
                              FEED_ITEMS_NUMBER=10,
                              FEED_ITEMS_DELAY=2*60*60,
                              THREAD_DELAY=5*60,
                              POST_DELAY=20,
                              FIRST_POST_DELAY=3*60,
                              UNREAD_STATE_EXPIRE_TIME=3*24*60*60)
