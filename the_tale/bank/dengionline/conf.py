# coding: utf-8

from datetime import timedelta

from dext.utils.app_settings import app_settings

dengionline_settings = app_settings('DENGIONLINE',
                                    PROJECT_ID='TEST-PROJECT-ID',
                                    SECRET_KEY='TEST-SECRET-KEY',
                                    RECEIVED_CURRENCY_TYPE='RUB',
                                    SIMPLE_PAYMENT_URL='https://paymentgateway.ru/',
                                    CREATION_TIME_LIMIT=timedelta(minutes=5),
                                    CREATION_NUMBER_LIMIT=5,
                                    DISCARD_TIMEOUT=timedelta(days=7))
