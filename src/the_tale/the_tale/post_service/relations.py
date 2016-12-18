# coding: utf-8

from rels.django import DjangoEnum


class MESSAGE_STATE(DjangoEnum):
    records = ( ('WAITING', 1, 'ожидает обработки'),
                ('PROCESSED', 2, 'обработано'),
                ('ERROR', 3, 'ошибка при обработке'),
                ('SKIPPED', 4, 'сервис не отправляет этот тип сообщений'))
