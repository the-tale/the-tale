# coding: utf-8

from django.db import models

from common.utils.enum import create_enum

BATTLE_1X1_STATE = create_enum('BATTLE_1X1_STATE', (('WAITING', 1, u'в очереди'),
                                                    ('PREPAIRING', 2, u'подготовка'),
                                                    ('PROCESSING', 3, u'идёт бой'),

                                                    ('ENEMY_NOT_FOND', 4, u'противник не найден'),
                                                    ('PROCESSED', 5, u'бой обработан'),
                                                    ('LEAVE_QUEUE', 6, u'убрана из очереди игроком')) )

BATTLE_RESULT = create_enum('BATTLE_RESULT', (('UNKNOWN', 0, u'неизвестен'),
                                              ('VICTORY', 1, u'победа'),
                                              ('DEFEAT', 2, u'поражение'),
                                              ('DRAW', 3, u'ничья')) )


class Battle1x1(models.Model):

    account = models.ForeignKey('accounts.Account', null=False, related_name='+')

    enemy = models.ForeignKey('accounts.Account', null=True, related_name='+')

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    state = models.IntegerField(default=BATTLE_1X1_STATE.WAITING, choices=BATTLE_1X1_STATE._CHOICES, db_index=True)

    calculate_rating = models.BooleanField(default=False, db_index=True)

    result = models.IntegerField(default=BATTLE_RESULT.UNKNOWN, choices=BATTLE_RESULT._CHOICES, db_index=True)
