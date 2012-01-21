# coding: utf-8

from django.db import models

from game.angels.models import Angel

from game.game_info import RACE, RACE_CHOICES

class Hero(models.Model):

    angel = models.ForeignKey(Angel, related_name='heroes', default=None, null=True, blank=True)

    alive = models.BooleanField(default=True)

    #base
    name = models.CharField(max_length=150, null=False)

    race = models.IntegerField(choices=RACE_CHOICES, default=RACE.HUMAN)

    level = models.IntegerField(null=False, default=1)
    experience = models.BigIntegerField(null=False, default=0)
    destiny_points = models.IntegerField(null=False, default=1)
    destiny_points_spend = models.IntegerField(null=False, default=0) # for random.seed
    
    health = models.FloatField(null=False, default=0.0)

    money = models.BigIntegerField(null=False, default=0)

    equipment = models.TextField(null=False, default='{}')
    bag = models.TextField(null=False, default='{}')

    abilities = models.TextField(null=False, default='{}')

    context = models.TextField(null=False, default='{}')

    messages = models.TextField(null=False, default='[]')

    #position
    pos_place = models.ForeignKey('places.Place', related_name='+', null=True, default=None, blank=True)
    pos_road = models.ForeignKey('roads.Road', related_name='+', null=True, default=None, blank=True)
    pos_percents = models.FloatField(null=True, default=None, blank=True)
    pos_invert_direction = models.NullBooleanField(default=False, null=True, blank=True)
    pos_from_x = models.IntegerField(null=True, blank=True, default=None)
    pos_from_y = models.IntegerField(null=True, blank=True, default=None)
    pos_to_x = models.IntegerField(null=True, blank=True, default=None)
    pos_to_y = models.IntegerField(null=True, blank=True, default=None)

    @classmethod
    def get_related_query(cls):
        return cls.objects.select_related('pos_place', 'pos_road')

    def __unicode__(self):
        return u'hero[%d] - %s' % (self.id, self.name)


class CHOOSE_ABILITY_STATE:
    WAITING = 0
    PROCESSED = 1
    UNPROCESSED = 2
    RESET = 3
    ERROR = 4

CHOOSE_ABILITY_STATE_CHOICES = [(CHOOSE_ABILITY_STATE.WAITING, u'в очереди'),
                                (CHOOSE_ABILITY_STATE.PROCESSED, u'обработана'),
                                (CHOOSE_ABILITY_STATE.UNPROCESSED, u'нельзя выбрать'),
                                (CHOOSE_ABILITY_STATE.RESET, u'сброшена'),
                                (CHOOSE_ABILITY_STATE.ERROR, u'ошибка')]

class ChooseAbilityTask(models.Model):

    state = models.IntegerField(default=CHOOSE_ABILITY_STATE.WAITING, choices=CHOOSE_ABILITY_STATE_CHOICES)

    hero = models.ForeignKey(Hero,  related_name='+')

    ability_id = models.CharField(max_length=64)
    ability_level = models.IntegerField(null=False)

    comment = models.CharField(max_length=256, blank=True, null=False, default=True)
