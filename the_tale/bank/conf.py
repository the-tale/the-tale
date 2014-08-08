# coding: utf-8
import datetime

from dext.common.utils.app_settings import app_settings


bank_settings = app_settings('BANK',
                             BANK_PROCESSOR_SLEEP_TIME=60,
                             ENABLE_BANK=True,
                             INFINIT_MONEY_AMOUNT=999999999,
                             FROZEN_INVOICE_EXPIRED_TIME=datetime.timedelta(minutes=60),
                             FROZEN_INVOICE_EXPIRED_CHECK_TIMEOUT=60,
                             SETTINGS_ALLOWED_KEY='bank allowed',
                             SETTINGS_LAST_FROZEN_EXPIRED_CHECK_KEY='bank last frozen expired check',
                             GET_ACCOUNT_ID_BY_EMAIL='the_tale.accounts.logic.get_account_id_by_email')
