# coding: utf-8

from rels.django import DjangoEnum


class MESSAGE_STATE(DjangoEnum):
    records = ( ('WAITING', 1, u'ожидает обработки'),
                ('PROCESSED', 2, u'обработано'),
                ('ERROR', 3, u'ошибка при обработке'),
                ('SKIPPED', 4, u'сервис не отправляет этот тип сообщений'))
