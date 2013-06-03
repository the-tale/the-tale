# coding: utf-8

from django.conf import settings as project_settings

from dext.utils.app_settings import app_settings

payments_settings = app_settings('PAYMENTS',
                                 PREMIUM_CURRENCY_FOR_DOLLAR=100,
                                 ENABLE_DENGIONLINE=False if not project_settings.TESTS_RUNNING else True,
                                 ALWAYS_ALLOWED_ACCOUNTS=[])
