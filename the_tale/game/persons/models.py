# coding: utf-8

import datetime

from django.db import models

from rels.django import RelationIntegerField

from the_tale.game.relations import GENDER, RACE
from the_tale.game.persons import relations


class Person(models.Model):
    MAX_NAME_LENGTH = 100

    created_at = models.DateTimeField(auto_now_add=True, null=False, default=datetime.datetime(2000, 1, 1))
    created_at_turn = models.IntegerField(null=False, default=0)

    out_game_at = models.DateTimeField(null=False, default=datetime.datetime(2000, 1, 1))

    place = models.ForeignKey('places.Place', related_name='persons', on_delete=models.PROTECT)

    state = RelationIntegerField(relation=relations.PERSON_STATE)

    gender = RelationIntegerField(relation=GENDER, relation_column='value')
    race = RelationIntegerField(relation=RACE, relation_column='value')

    type = RelationIntegerField(relation=relations.PERSON_TYPE, relation_column='value')

    friends_number = models.IntegerField(default=0)

    enemies_number = models.IntegerField(default=0)

    name = models.CharField(max_length=MAX_NAME_LENGTH, null=False, db_index=True)

    data = models.TextField(null=False, default=u'{}')

    def __unicode__(self): return u'%s from %s' % (self.name, self.place)



class SocialConnection(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    created_at_turn = models.BigIntegerField()

    out_game_at = models.DateTimeField(null=True, default=None)
    out_game_at_turn = models.BigIntegerField(null=True, default=None)

    person_1 = models.ForeignKey(Person, related_name='+', on_delete=models.CASCADE)
    person_2 = models.ForeignKey(Person, related_name='+', on_delete=models.CASCADE)

    connection = RelationIntegerField(relation=relations.SOCIAL_CONNECTION_TYPE)

    state = RelationIntegerField(relation=relations.SOCIAL_CONNECTION_STATE)
