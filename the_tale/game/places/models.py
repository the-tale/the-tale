# coding: utf-8

from django.db import models

from rels.django import RelationIntegerField

from dext.common.utils import s11n

from the_tale.game.relations import RACE

from the_tale.game.places import relations
from the_tale.game.places import modifiers


class Place(models.Model):

    x = models.BigIntegerField(null=False)
    y = models.BigIntegerField(null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    created_at_turn = models.BigIntegerField(default=0)

    updated_at_turn = models.BigIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    is_frontier = models.BooleanField(default=False)

    description = models.TextField(null=False, default=u'', blank=True)

    data = models.TextField(null=False, default=u'{}')

    habit_honor_positive = models.FloatField(default=0)
    habit_honor_negative = models.FloatField(default=0)
    habit_peacefulness_positive = models.FloatField(default=0)
    habit_peacefulness_negative = models.FloatField(default=0)

    habit_honor = models.FloatField(default=0)
    habit_peacefulness = models.FloatField(default=0)

    modifier = RelationIntegerField(relation=modifiers.CITY_MODIFIERS, null=False, default=modifiers.CITY_MODIFIERS.NONE.value)
    race = RelationIntegerField(relation=RACE)

    persons_changed_at_turn = models.BigIntegerField(default=0)

    def __unicode__(self): return s11n.from_json(self.data)['name']['forms'][0]


class Building(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    created_at_turn = models.BigIntegerField(default=0)

    x = models.BigIntegerField(null=False)
    y = models.BigIntegerField(null=False)

    state = RelationIntegerField(relation=relations.BUILDING_STATE, relation_column='value', db_index=True)
    type = RelationIntegerField(relation=relations.BUILDING_TYPE, relation_column='value')

    integrity = models.FloatField(default=1.0, null=False)

    place = models.ForeignKey(Place, null=False, on_delete=models.CASCADE)

    person = models.OneToOneField('persons.Person', null=False, on_delete=models.CASCADE)

    data = models.TextField(null=False, default=u'{}')


class ResourceExchange(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)

    place_1 = models.ForeignKey(Place, related_name='+', null=True, on_delete=models.CASCADE)
    place_2 = models.ForeignKey(Place, related_name='+', null=True, on_delete=models.CASCADE)

    resource_1 = RelationIntegerField(relation=relations.RESOURCE_EXCHANGE_TYPE, relation_column='value')
    resource_2 = RelationIntegerField(relation=relations.RESOURCE_EXCHANGE_TYPE, relation_column='value')

    bill = models.ForeignKey('bills.Bill', blank=True, null=True, related_name='+', on_delete=models.SET_NULL)
