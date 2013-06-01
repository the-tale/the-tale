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
                 ('FAILED_ON_CONFIRM', 3, u'ошибка при подтверждении'),
                 ('DISCARDED', 4, u'отклонён по таймауту'))


class CHECK_USER_RESULT(DjangoEnum):
    answer = Column(unique=False, primary=False)
    _records = ( ('USER_EXISTS', 0, u'пользователь найден', u'YES'),
                 ('WRONG_KEY', 1, u'неверный хэш', u'NO'),
                 ('USER_NOT_EXISTS', 2, u'пользователь не найден', u'NO') )

class CONFIRM_PAYMENT_RESULT(DjangoEnum):
    answer = Column(unique=False, primary=False)
    _records = ( ('INVOICE_NOT_FOUND', 0, u'платёж не найден', u'NO'),
                 ('WRONG_USER_ID', 1, u'неверный идентификатор пользователя', u'NO'),
                 ('WRONG_ORDER_ID', 2, u'неверный идентификатор заказа', u'NO'),
                 ('WRONG_HASH_KEY', 3, u'неверный хэш', u'NO'),
                 ('ALREADY_CONFIRMED', 4, u'уже подтверждено', u'YES'),
                 ('ALREADY_CONFIRMED_WRONG_ARGUMENTS', 5, u'уже подтверждено, но новые аргументы отличаются от переданных ранее', u'NO'),
                 ('ALREADY_PROCESSED', 6, u'уже обработано', u'YES'),
                 ('ALREADY_PROCESSED_WRONG_ARGUMENTS', 7, u'уже обработано, но новые аргументы отличаются от переданных ранее', u'NO'),
                 ('CONFIRMED', 8, u'подтверждено успешно', u'YES'),
                 ('FAILED_ON_CONFIRM', 9, u'ошибка при обработке запроса', u'NO'),
                 ('ALREADY_FAILED_ON_CONFIRM', 10, u'ранее возникла ошибка при обработке запроса', u'NO'),
                 ('DISCARDED', 11, u'счёт отменён, превышено время ожидания ответа системы', u'NO'))
