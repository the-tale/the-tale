# coding: utf-8

import datetime

from django.db import models

from common.utils.enum import create_enum

from game.game_info import GENDER
from game.balance.enums import RACE, PERSON_TYPE


PERSON_STATE = create_enum('PERSON_STATE', ( ('IN_GAME', 0,  u'в игре'),
                                             ('OUT_GAME', 1, u'вне игры') ))


class Person(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, null=False, default=datetime.datetime(2000, 1, 1))
    created_at_turn = models.IntegerField(null=False, default=0)

    place = models.ForeignKey('places.Place', related_name='persons')

    state = models.IntegerField(default=PERSON_STATE.IN_GAME, choices=PERSON_STATE._CHOICES)

    name = models.CharField(max_length=256)

    gender = models.IntegerField(null=False, default=GENDER.MASCULINE, choices=GENDER._CHOICES)

    race = models.IntegerField(choices=RACE._CHOICES, default=RACE.HUMAN)

    type = models.IntegerField(choices=PERSON_TYPE._CHOICES)

    friends_number = models.IntegerField(default=0)

    enemies_number = models.IntegerField(default=0)

    data = models.TextField(null=False, default=u'{}')
