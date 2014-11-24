# coding: utf-8

from rels.django import DjangoEnum


class COMPANION_RECORD_STATE(DjangoEnum):
   records = ( ('ENABLED', 0, u'в игре'),
               ('DISABLED', 1, u'вне игры'),)
