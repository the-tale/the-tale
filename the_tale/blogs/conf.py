# coding: utf-8

from dext.utils.app_settings import app_settings

blogs_settings = app_settings('BLOGS',
                              FORUM_CATEGORY_SLUG='blogs',
                              POSTS_ON_PAGE=10)
