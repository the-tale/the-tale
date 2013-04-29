# coding: utf-8

from dext.utils.app_settings import app_settings


bank_settings = app_settings('BANK',
                             BANK_DELAY=60,
                             ENABLE_BANK=True,
                             INFINIT_MONEY_AMOUNT=999999999,
                             SETTINGS_ALLOWED_KEY='bank allowed')
