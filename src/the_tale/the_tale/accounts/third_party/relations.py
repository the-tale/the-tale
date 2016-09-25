# coding: utf-8

from rels.django import DjangoEnum


class ACCESS_TOKEN_STATE(DjangoEnum):
    records = ( ('UNPROCESSED', 0, u'неизвестен'),
                ('ACCEPTED', 1, u'разрешено') )


class AUTHORISATION_STATE(DjangoEnum):
    records = ( ('NOT_REQUESTED', 0, u'авторизация не запрашивалась'),
                ('UNPROCESSED', 1, u'пользователь ещё не принял решение'),
                ('ACCEPTED', 2, u'авторизация прошла успешно'),
                ('REJECTED', 3, u'в авторизации отказано') )
