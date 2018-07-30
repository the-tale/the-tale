
import smart_imports

smart_imports.all()


class INVOICE_STATE(rels_django.DjangoEnum):

    records = (('REQUESTED', 0, 'запрошен'),
               ('FROZEN', 1, 'заморожен'),
               ('REJECTED', 2, 'отказано в заморозке'),
               ('CONFIRMED', 3, 'подтверждён'),
               ('CANCELED', 4, 'отменён'),
               ('RESETED', 5, 'сброшен'),
               ('FORCED', 6, 'запрошен принудительно'))


class ENTITY_TYPE(rels_django.DjangoEnum):
    is_infinite = rels.Column(unique=False)
    is_real = rels.Column(unique=False)

    records = (('DENGI_ONLINE', 0, 'dengi online', True, True),
               ('GAME_ACCOUNT', 1, 'игровой аккаунт', False, False),
               ('GAME_MASTER', 2, 'гейммастер', True, False),
               ('GAME_LOGIC', 3, 'игровая логика', True, False),
               ('XSOLLA', 4, 'xsolla', True, True))


class CURRENCY_TYPE(rels_django.DjangoEnum):
    records = (('PREMIUM', 0, 'премиум валюта'),
               ('NORMAL', 1, 'обычная валюта'),)
