# coding: utf-8

from rels.django_staff import DjangoEnum


class BATTLE_1X1_RESULT(DjangoEnum):
    _records = (('UNKNOWN', 0, u'неизвестен'),
                ('VICTORY', 1, u'победа'),
                ('DEFEAT', 2, u'поражение'),
                ('DRAW', 3, u'ничья'))


class BATTLE_1X1_STATE(DjangoEnum):
    _records = ( ('WAITING', 1, u'в очереди'),
                 ('PREPAIRING', 2, u'подготовка'),
                 ('PROCESSING', 3, u'идёт бой') )
