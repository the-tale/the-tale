# coding: utf-8

from rels.django import DjangoEnum


class BATTLE_1X1_RESULT(DjangoEnum):
    records = (('UNKNOWN', 0, 'неизвестен'),
                ('VICTORY', 1, 'победа'),
                ('DEFEAT', 2, 'поражение'),
                ('DRAW', 3, 'ничья'))


class BATTLE_1X1_STATE(DjangoEnum):
    records = ( ('WAITING', 1, 'в очереди'),
                ('PREPAIRING', 2, 'подготовка'),
                ('PROCESSING', 3, 'идёт бой') )
