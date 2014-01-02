# coding: utf-8

import datetime

from django.db import models

from rels.django import RelationIntegerField

from the_tale.common.utils.enum import create_enum

from the_tale.game.relations import GENDER, RACE
from the_tale.game.persons.relations import PERSON_TYPE


PERSON_STATE = create_enum('PERSON_STATE', ( ('IN_GAME', 0,  u'в игре'),
                                             ('OUT_GAME', 1, u'вне игры'),
                                             ('REMOVED', 2, u'удален')))


class Person(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, null=False, default=datetime.datetime(2000, 1, 1))
    created_at_turn = models.IntegerField(null=False, default=0)

    out_game_at = models.DateTimeField(null=False, default=datetime.datetime(2000, 1, 1))

    place = models.ForeignKey('places.Place', related_name='persons', on_delete=models.PROTECT)

    state = models.IntegerField(default=PERSON_STATE.IN_GAME, choices=PERSON_STATE._CHOICES)

    name = models.CharField(max_length=256)

    gender = RelationIntegerField(relation=GENDER, relation_column='value')
    race = RelationIntegerField(relation=RACE, relation_column='value')

    type = RelationIntegerField(relation=PERSON_TYPE, relation_column='value')

    friends_number = models.IntegerField(default=0)

    enemies_number = models.IntegerField(default=0)

    data = models.TextField(null=False, default=u'{}')

    def __unicode__(self): return u'%s from %s' % (self.name, self.place)
