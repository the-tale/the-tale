# coding: utf-8

import rels
from rels.django import DjangoEnum


class MOB_RECORD_STATE(DjangoEnum):
   records = ( ('ENABLED', 0, u'в игре'),
                ('DISABLED', 1, u'вне игры'),)



class MOB_TYPE(DjangoEnum):
    is_mercenary = rels.Column(unique=False)

    records = ( ('PLANT', 0, u'растение', False),
                 ('ANIMAL', 1, u'животное', False),
                 ('SUPERNATURAL', 2, u'сверхъестественное', False),
                 ('MECHANICAL', 3, u'механизм', False),
                 ('BARBARIAN', 4, u'дикарь', False),
                 ('CIVILIZED', 5, u'цивилизованный гуманоид', True))
