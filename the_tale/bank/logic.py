# coding: utf-8

from the_tale.common.utils import discovering

from the_tale.bank.conf import bank_settings


_GET_ACCOUNT_ID_BY_EMAIL_FUNCTION = discovering.get_function(bank_settings.GET_ACCOUNT_ID_BY_EMAIL)


def get_account_id(email):
    return _GET_ACCOUNT_ID_BY_EMAIL_FUNCTION(email)
