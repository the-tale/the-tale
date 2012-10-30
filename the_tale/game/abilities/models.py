# coding: utf-8

from django.db import models

from common.utils.enum import create_enum


class AbilitiesData(models.Model):

    hero = models.ForeignKey('heroes.Hero', null=False)

    help_available_at = models.BigIntegerField(null=False, default=0)


ABILITY_TASK_STATE = create_enum('ABILITY_TASK_STATE', (('WAITING', 0, u'в очереди'),
                                                        ('PROCESSED', 1, u'обработана'),
                                                        ('UNPROCESSED', 2, u'нельзя применить'),
                                                        ('RESET', 3, u'сброшена'),
                                                        ('ERROR', 4, u'ошибка'), ))

class AbilityTask(models.Model):

    state = models.IntegerField(default=ABILITY_TASK_STATE.WAITING, choices=ABILITY_TASK_STATE.CHOICES)

    hero = models.ForeignKey('heroes.Hero',  related_name='abilities_in_use')

    type = models.CharField(max_length=64)

    activated_at = models.IntegerField()
    available_at = models.IntegerField()

    comment = models.TextField(default='')

    data = models.TextField(default='{}')
