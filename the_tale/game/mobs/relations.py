# coding: utf-8

import rels
from rels.django import DjangoEnum


class MOB_RECORD_STATE(DjangoEnum):
   records = ( ('ENABLED', 0, u'в игре'),
                ('DISABLED', 1, u'вне игры'),)


class MOB_TYPE(DjangoEnum):
    is_mercenary = rels.Column(unique=False)
    is_eatable = rels.Column(unique=False)

    records = ( ('PLANT', 0, u'растения', False, True),
                ('ANIMAL', 1, u'животные', False, True),
                ('SUPERNATURAL', 2, u'стихийные существа', False, False),
                ('MECHANICAL', 3, u'конструкты', False, False),
                ('BARBARIAN', 4, u'дикари', False, True),
                ('CIVILIZED', 5, u'цивилизованные существа', True, True),
                ('COLDBLOODED', 6, u'хладнокровные гады', False, True),
                ('INSECT', 7, u'насекомые', False, True),
                ('DEMON', 8, u'демоны', False, False),
                ('UNDEAD', 9, u'нежить', False, False),
                ('MONSTER', 10, u'чудовища', False, True))


class INDEX_ORDER_TYPE(DjangoEnum):
   records =( ('BY_LEVEL', 'by_level', u'по уровню'),
              ('BY_NAME', 'by_name', u'по имени'),)
