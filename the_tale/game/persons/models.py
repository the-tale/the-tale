# coding: utf-8

from django.db import models

from rels.django import RelationIntegerField

from dext.common.utils import s11n

from the_tale.game.relations import GENDER, RACE
from the_tale.game.persons import relations


class Person(models.Model):
    MAX_NAME_LENGTH = 100

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    created_at_turn = models.IntegerField(null=False, default=0)

    updated_at_turn = models.BigIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    place = models.ForeignKey('places.Place', related_name='persons', on_delete=models.PROTECT)

    gender = RelationIntegerField(relation=GENDER, relation_column='value')
    race = RelationIntegerField(relation=RACE, relation_column='value')

    type = RelationIntegerField(relation=relations.PERSON_TYPE, relation_column='value')

    data = models.TextField(null=False, default=u'{}')

    def __unicode__(self): return u'%s from %s' % (s11n.from_json(self.data)['name']['forms'][0], self.place)



class SocialConnection(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    created_at_turn = models.BigIntegerField()

    out_game_at = models.DateTimeField(null=True, default=None)
    out_game_at_turn = models.BigIntegerField(null=True, default=None)

    person_1 = models.ForeignKey(Person, related_name='+', on_delete=models.CASCADE)
    person_2 = models.ForeignKey(Person, related_name='+', on_delete=models.CASCADE)

    connection = RelationIntegerField(relation=relations.SOCIAL_CONNECTION_TYPE)

    state = RelationIntegerField(relation=relations.SOCIAL_CONNECTION_STATE)
