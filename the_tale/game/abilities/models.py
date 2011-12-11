# coding: utf-8

from django.db import models

class ABILITY_STATE:
    WAITING = 0
    PROCESSED = 1
    UNPROCESSED = 2
    RESET = 3
    ERROR = 4

ABILITY_STATE_CHOICES = [(ABILITY_STATE.WAITING, u'в очереди'),
                         (ABILITY_STATE.PROCESSED, u'обработана'),
                         (ABILITY_STATE.UNPROCESSED, u'нельзя применить'),
                         (ABILITY_STATE.RESET, u'сброшена'),
                         (ABILITY_STATE.ERROR, u'ошибка')]

class AbilityTask(models.Model):

    state = models.IntegerField(default=ABILITY_STATE.WAITING, choices=ABILITY_STATE_CHOICES)

    angel = models.ForeignKey('angels.Angel', related_name='abilities_in_use')
    hero = models.ForeignKey('heroes.Hero',  related_name='abilities_in_use')

    type = models.CharField(max_length=64)

    activated_at = models.IntegerField()
    available_at = models.IntegerField()

    data = models.TextField(default='{}')
