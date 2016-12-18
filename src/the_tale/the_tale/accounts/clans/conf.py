# coding: utf-8

from dext.common.utils.app_settings import app_settings

clans_settings = app_settings('CLANS',
                              CLANS_ON_PAGE=25,
                              OWNER_MIGHT_REQUIRED=300,
                              FORUM_CATEGORY_SLUG='clans',)
