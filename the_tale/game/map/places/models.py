# coding: utf-8

from django.db import models

from rels.django import RelationIntegerField

from the_tale.game.relations import RACE

from the_tale.game.map.places.relations import BUILDING_TYPE, BUILDING_STATE, RESOURCE_EXCHANGE_TYPE, CITY_MODIFIERS

from the_tale.game.balance import constants as c


class Place(models.Model):

    MAX_NAME_LENGTH = 150

    x = models.BigIntegerField(null=False)
    y = models.BigIntegerField(null=False)

    updated_at_turn = models.BigIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    name = models.CharField(max_length=MAX_NAME_LENGTH, null=False, db_index=True)

    name_forms = models.TextField(null=False, default=u'')

    description = models.TextField(null=False, default=u'', blank=True)

    size = models.IntegerField(null=False)
    expected_size = models.IntegerField(default=0)

    goods = models.IntegerField(default=0)

    production = models.IntegerField(default=c.PLACE_GOODS_BONUS)
    safety = models.FloatField(default=1.0-c.BATTLES_PER_TURN)
    freedom = models.FloatField(default=1.0)
    transport = models.FloatField(default=1.0)

    data = models.TextField(null=False, default=u'{}')

    heroes_number = models.IntegerField(default=0)

    modifier = RelationIntegerField(relation=CITY_MODIFIERS, null=True, default=None, blank=True)
    race = RelationIntegerField(relation=RACE)

    class Meta:
        ordering = ('name', )

    def __unicode__(self):
        return self.name


class Building(models.Model):

    name_forms = models.TextField(null=False, default=u'')

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    created_at_turn = models.BigIntegerField(default=0)

    x = models.BigIntegerField(null=False)
    y = models.BigIntegerField(null=False)

    state = RelationIntegerField(relation=BUILDING_STATE, relation_column='value', db_index=True)
    type = RelationIntegerField(relation=BUILDING_TYPE, relation_column='value')

    integrity = models.FloatField(default=1.0, null=False)

    place = models.ForeignKey(Place, null=False, on_delete=models.CASCADE)

    person = models.ForeignKey('persons.Person', null=False, unique=True, on_delete=models.CASCADE)


class ResourceExchange(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)

    place_1 = models.ForeignKey(Place, related_name='+', on_delete=models.CASCADE)
    place_2 = models.ForeignKey(Place, related_name='+', on_delete=models.CASCADE)

    resource_1 = RelationIntegerField(relation=RESOURCE_EXCHANGE_TYPE, relation_column='value')
    resource_2 = RelationIntegerField(relation=RESOURCE_EXCHANGE_TYPE, relation_column='value')

    bill = models.ForeignKey('bills.Bill', blank=True, null=True, related_name='+', on_delete=models.SET_NULL)
