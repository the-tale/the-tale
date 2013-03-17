# coding: utf-8

from django.db import models

from rels.django_staff import TableIntegerField

from game.balance.enums import CITY_MODIFIERS, RACE

from game.map.places.relations import BUILDING_TYPE, BUILDING_STATE


class Place(models.Model):

    MAX_NAME_LENGTH = 150

    x = models.BigIntegerField(null=False)
    y = models.BigIntegerField(null=False)

    updated_at_turn = models.BigIntegerField(default=0)

    name = models.CharField(max_length=MAX_NAME_LENGTH, null=False, db_index=True)

    name_forms = models.TextField(null=False, default=u'')

    description = models.TextField(null=False, default=u'', blank=True)

    size = models.IntegerField(null=False) # specify size of the place

    data = models.TextField(null=False, default=u'{}')

    heroes_number = models.IntegerField(default=0)

    modifier = models.IntegerField(null=True, default=None, choices=CITY_MODIFIERS._CHOICES, blank=True)

    race = models.IntegerField(null=False, default=RACE.HUMAN, choices=RACE._CHOICES)

    class Meta:
        ordering = ('name', )

    def __unicode__(self):
        return self.name


class Building(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, null=False)

    x = models.BigIntegerField(null=False)
    y = models.BigIntegerField(null=False)

    state = TableIntegerField(relation=BUILDING_STATE, relation_column='value', default=BUILDING_STATE.WORKING, db_index=True)
    type = TableIntegerField(relation=BUILDING_TYPE, relation_column='value')

    integrity = models.FloatField(default=1.0, null=False)

    place = models.ForeignKey(Place, null=False)

    person = models.ForeignKey('persons.Person', null=False, unique=True)
