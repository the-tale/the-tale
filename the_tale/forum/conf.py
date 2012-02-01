# coding: utf-8

from django_next.utils.app_settings import app_settings

forum_settings = app_settings('FORUM', 
                              POSTS_ON_PAGE=15
                              )

