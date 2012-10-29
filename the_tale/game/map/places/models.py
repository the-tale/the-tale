# coding: utf-8

from django.db import models

from ...game_info import RACE

class TERRAIN:
    DESERT = '_'
    FOREST = 'f'
    GRASS = '.'
    SWAMP = 'w'

TERRAIN_CHOICES = ( (TERRAIN.DESERT, 'пустыня' ),
                    (TERRAIN.FOREST, 'лес'),
                    (TERRAIN.GRASS, 'луга'),
                    (TERRAIN.SWAMP, 'болото') )

RACE_TO_TERRAIN = { RACE.HUMAN: TERRAIN.GRASS,
                    RACE.ELF: TERRAIN.FOREST,
                    RACE.ORC: TERRAIN.DESERT,
                    RACE.GOBLIN: TERRAIN.SWAMP,
                    RACE.DWARF: TERRAIN.GRASS }

TERRAIN_STR_2_ID = { 'desert': TERRAIN.DESERT,
                     'forest': TERRAIN.FOREST,
                     'grass': TERRAIN.GRASS,
                     'swamp': TERRAIN.SWAMP }

class PLACE_TYPE:
    CITY = 'city'

PLACE_CHOICES = ( (PLACE_TYPE.CITY, 'city'), )

class Place(models.Model):

    MAX_NAME_LENGTH = 150

    x = models.BigIntegerField(null=False)
    y = models.BigIntegerField(null=False)

    updated_at_turn = models.BigIntegerField(default=0)

    name = models.CharField(max_length=MAX_NAME_LENGTH, null=False, db_index=True)

    name_forms = models.TextField(null=False, default=u'')

    description = models.TextField(null=False, default=u'', blank=True)

    terrain = models.CharField(max_length=1,
                               default=TERRAIN.GRASS,
                               choices=TERRAIN_CHOICES,
                               null=False)

    type = models.CharField(max_length=50,
                            choices=PLACE_CHOICES,
                            null=False)

    subtype = models.CharField(max_length=50,
                               choices=( ('UNDEFINED', 'undefined'), ),
                               null=False) # orc city, goblin dungeon (specify how to display)

    size = models.IntegerField(null=False) # specify size of the place

    data = models.TextField(null=False, default={})

    heroes_number = models.IntegerField(default=0)

    class Meta:
        ordering = ('name', )

    def __unicode__(self):
        return self.name
