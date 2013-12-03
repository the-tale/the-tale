# coding: utf-8

import rels
from rels.django import DjangoEnum


class MOB_RECORD_STATE(DjangoEnum):
   records = ( ('ENABLED', 0, u'в игре'),
                ('DISABLED', 1, u'вне игры'),)


class MOB_TYPE(DjangoEnum):
    is_mercenary = rels.Column(unique=False)

    records = ( ('PLANT', 0, u'растения', False),
                ('ANIMAL', 1, u'животные', False),
                ('SUPERNATURAL', 2, u'стихийные существа', False),
                ('MECHANICAL', 3, u'конструкты', False),
                ('BARBARIAN', 4, u'дикари', False),
                ('CIVILIZED', 5, u'цивилизованные существа', True),
                ('COLDBLOODED', 6, u'хладнокровные гады', False),
                ('INSECT', 7, u'насекомые', False),
                ('DEMON', 8, u'демоны', False),
                ('UNDEAD', 9, u'нежить', False),
                ('MONSTER', 10, u'чудовища', False))


class INDEX_ORDER_TYPE(DjangoEnum):
   records =( ('BY_LEVEL', 'by_level', u'по уровню'),
              ('BY_NAME', 'by_name', u'по имени'),)
