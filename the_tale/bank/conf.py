# coding: utf-8

from dext.utils.app_settings import app_settings


bank_settings = app_settings('BANK',
                             BANK_PROCESSOR_SLEEP_TIME=60,
                             ENABLE_BANK=True,
                             INFINIT_MONEY_AMOUNT=999999999,
                             SETTINGS_ALLOWED_KEY='bank allowed',
                             GET_ACCOUNT_ID_BY_EMAIL='the_tale.accounts.logic.get_account_id_by_email')
