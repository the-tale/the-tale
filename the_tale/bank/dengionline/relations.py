# coding: utf-8

from rels import Column
from rels.django_staff import DjangoEnum


class CURRENCY_TYPE(DjangoEnum):
    url_code = Column()

    _records = ( ('USD', 0, u'доллар США', u'USD'),
                 ('RUB', 1, u'рубль РФ', u'RUB'),
                 ('BYR', 2, u'рубль РБ', u'BYR'),
                 ('UZS', 3, u'узбекский сум', u'UZS'),
                 ('EUR', 4, u'евро', u'EUR'),
                 ('UAH', 5, u'гривна', u'UAH') )


class INVOICE_STATE(DjangoEnum):
    _records = ( ('REQUESTED', 0, u'запрошен'),
                 ('CONFIRMED', 1, u'подтверждён'),
                 ('PROCESSED', 2, u'средства зачислены'),
                 ('FAILED_ON_CONFIRM', 3, u'ошибка при подтверждении') )


class CHECK_USER_RESULT(DjangoEnum):
    answer = Column(unique=False, primary=False)
    _records = ( ('USER_EXISTS', 0, u'пользователь найден', u'YES'),
                 ('WRONG_KEY', 1, u'неверный хэш', u'NO'),
                 ('USER_NOT_EXISTS', 2, u'пользователь не найден', u'NO') )
