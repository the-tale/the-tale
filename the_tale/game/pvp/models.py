# coding: utf-8

from django.db import models

from common.utils.enum import create_enum

BATTLE_1X1_STATE = create_enum('BATTLE_1X1_STATE', (('WAITING', 1, u'в очереди'),
                                                    ('PREPAIRING', 2, u'подготовка'),
                                                    ('PROCESSING', 3, u'идёт бой'),

                                                    ('ENEMY_NOT_FOND', 4, u'противник не найден'),
                                                    ('PROCESSED', 5, u'бой обработан'),
                                                    ('LEAVE_QUEUE', 6, u'убрана из очереди игроком')) )


class Battle1x1(models.Model):

    account = models.ForeignKey('accounts.Account', null=False, related_name='+')

    enemy = models.ForeignKey('accounts.Account', null=True, related_name='+')

    created_at = models.DateTimeField(auto_now_add=True, null=False)

    state = models.IntegerField(default=BATTLE_1X1_STATE.WAITING, choices=BATTLE_1X1_STATE.CHOICES)
