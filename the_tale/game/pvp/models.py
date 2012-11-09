# coding: utf-8

from django.db import models

from common.utils.enum import create_enum

BATTLE_1X1_STATE = create_enum('BATTLE_1X1_STATE', (('WAITING', 1, u'в очереди'),
                                                    ('PREPAIRING', 2, u'подготовка'),
                                                    ('PROCESSING', 3, u'идёт бой') ) )


class Battle1x1(models.Model):

    account = models.ForeignKey('accounts.Account', null=False, related_name='+', unique=True)

    enemy = models.ForeignKey('accounts.Account', null=True, related_name='+', unique=True)

    created_at = models.DateTimeField(auto_now_add=True, null=False)

    state = models.IntegerField(default=BATTLE_1X1_STATE.WAITING, choices=BATTLE_1X1_STATE.CHOICES)
