# coding: utf-8

import rels
from rels.django import DjangoEnum


class MOB_RECORD_STATE(DjangoEnum):
   records = ( ('ENABLED', 0, u'в игре'),
               ('DISABLED', 1, u'вне игры'),)


class INDEX_ORDER_TYPE(DjangoEnum):
   records =( ('BY_LEVEL', 'by_level', u'по уровню'),
              ('BY_NAME', 'by_name', u'по имени'),)
