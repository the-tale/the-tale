# coding: utf-8

from django.db import models

from common.utils.enum import create_enum

from game.balance.enums import RACE


TERRAIN = create_enum('TERRAIN', (('DESERT',    '_', u'пустыня'),
                                  ('FOREST',    'f', u'лес'),
                                  ('GRASS',     '.', u'луга'),
                                  ('SWAMP',     'w', u'болото'),
                                  ('MOUNTAINS', 'm', u'горы')) )

RACE_TO_TERRAIN = { RACE.HUMAN: TERRAIN.GRASS,
                    RACE.ELF: TERRAIN.FOREST,
                    RACE.ORC: TERRAIN.DESERT,
                    RACE.GOBLIN: TERRAIN.SWAMP,
                    RACE.DWARF: TERRAIN.MOUNTAINS }

TERRAIN_STR_2_ID = { 'desert': TERRAIN.DESERT,
                     'forest': TERRAIN.FOREST,
                     'grass': TERRAIN.GRASS,
                     'swamp': TERRAIN.SWAMP,
                     'mountains': TERRAIN.MOUNTAINS}


PLACE_TYPE = create_enum('PLACE_TYPE', (('CITY', 0, u'город'),))


class Place(models.Model):

    MAX_NAME_LENGTH = 150
    MAX_MODIFIER_ID_LENGTH = 32

    x = models.BigIntegerField(null=False)
    y = models.BigIntegerField(null=False)

    updated_at_turn = models.BigIntegerField(default=0)

    name = models.CharField(max_length=MAX_NAME_LENGTH, null=False, db_index=True)

    name_forms = models.TextField(null=False, default=u'')

    description = models.TextField(null=False, default=u'', blank=True)

    type = models.IntegerField(choices=PLACE_TYPE._CHOICES, null=False, default=PLACE_TYPE.CITY)

    size = models.IntegerField(null=False) # specify size of the place

    data = models.TextField(null=False, default=u'{}')

    heroes_number = models.IntegerField(default=0)

    modifier = models.CharField(max_length=MAX_MODIFIER_ID_LENGTH, null=True, default=None)

    class Meta:
        ordering = ('name', )

    def __unicode__(self):
        return self.name
