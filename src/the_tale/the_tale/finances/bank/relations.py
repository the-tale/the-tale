# coding: utf-8

from rels import Column
from rels.django import DjangoEnum


class INVOICE_STATE(DjangoEnum):

    records = ( ('REQUESTED', 0, u'запрошен'),
                ('FROZEN',    1, u'заморожен'),
                ('REJECTED',  2, u'отказано в заморозке'),
                ('CONFIRMED', 3, u'подтверждён'),
                ('CANCELED',  4, u'отменён'),
                ('RESETED',   5, u'сброшен'),
                ('FORCED',    6, u'запрошен принудительно'))


class ENTITY_TYPE(DjangoEnum):
    is_infinite = Column(unique=False)
    is_real = Column(unique=False)

    records = ( ('DENGI_ONLINE', 0, u'dengi online', True, True),
                ('GAME_ACCOUNT', 1, u'игровой аккаунт', False, False),
                ('GAME_MASTER',  2, u'гейммастер', True, False),
                ('GAME_LOGIC',   3, u'игровая логика', True, False),
                ('XSOLLA',       4, u'xsolla', True, True))


class CURRENCY_TYPE(DjangoEnum):
    records = ( ('PREMIUM', 0, u'премиум валюта'),
                ('NORMAL', 1, u'обычная валюта'),)
