# coding: utf-8
import md5
import time
import datetime

from bank import logic as bank_logic

from bank.xsolla.conf import xsolla_settings
from bank.xsolla.relations import CHECK_USER_RESULT, PAY_RESULT
from bank.xsolla.prototypes import InvoicePrototype


def check_user_md5(command, v1):
    md5_hash = md5.new()
    md5_hash.update(command.value)
    md5_hash.update(v1)
    md5_hash.update(xsolla_settings.SECRET_KEY)
    return md5_hash.hexdigest()


def check_user(command, external_md5, v1, v2, v3):

    if v1 is None:
        return CHECK_USER_RESULT.NOT_SPECIFIED_V1

    if not external_md5 or check_user_md5(command, v1).lower() != external_md5.lower():
        return CHECK_USER_RESULT.WRONG_MD5

    if bank_logic.get_account_id(email=v1) is None:
        return CHECK_USER_RESULT.USER_NOT_EXISTS

    return CHECK_USER_RESULT.USER_EXISTS


def pay_md5(command, v1, id):
    md5_hash = md5.new()
    md5_hash.update(command.value)
    md5_hash.update(v1)
    md5_hash.update(id)
    md5_hash.update(xsolla_settings.SECRET_KEY)
    return md5_hash.hexdigest()


def pay(command, external_md5, v1, v2, v3, id, sum, test, date, request_url):

    if v1 is None:
        return PAY_RESULT.NOT_SPECIFIED_V1, None

    if id is None:
        return PAY_RESULT.NOT_SPECIFIED_ID, None

    if sum is None:
        return PAY_RESULT.NOT_SPECIFIED_SUM, None

    if not external_md5 or pay_md5(command, v1, id).lower() != external_md5.lower():
        return PAY_RESULT.WRONG_MD5, None

    invoice = InvoicePrototype.pay(v1=v1, v2=v2, v3=v3, xsolla_id=id, payment_sum=sum, test=test, date=date, request_url=request_url)

    return invoice.pay_result, invoice.id


def cancel_md5(command, id):
    md5_hash = md5.new()
    md5_hash.update(command.value)
    md5_hash.update(id)
    md5_hash.update(xsolla_settings.SECRET_KEY)
    return md5_hash.hexdigest()
