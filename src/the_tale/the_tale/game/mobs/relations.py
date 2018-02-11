
from rels.django import DjangoEnum


class MOB_RECORD_STATE(DjangoEnum):
    records = (('ENABLED', 0, 'в игре'),
               ('DISABLED', 1, 'вне игры'))


class INDEX_ORDER_TYPE(DjangoEnum):
    records = (('BY_LEVEL', 'by_level', 'по уровню'),
               ('BY_NAME', 'by_name', 'по имени'))
