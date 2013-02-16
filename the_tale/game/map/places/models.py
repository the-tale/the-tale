# coding: utf-8

from django.db import models

from common.utils.enum import create_enum

from game.balance.enums import CITY_MODIFIERS


TERRAIN = create_enum('TERRAIN', ( ('WATER_DEEP',            0, u'глубокая вода'),
                                   ('WATER_SHOAL',           1, u'мелкая вода'),
                                   ('MOUNTAINS_HIGH',        2, u'высокие горы'),
                                   ('MOUNTAINS_LOW',         3, u'низкие горы'),

                                   ('PLANE_SAND',            4, u'пустыня'),
                                   ('PLANE_DRY_LAND',        5, u'высохшая растрескавшаяся земля'),
                                   ('PLANE_MUD',             6, u'грязь'),
                                   ('PLANE_DRY_GRASS',       7, u'сухие луга'),
                                   ('PLANE_GRASS',           8, u'луга'),
                                   ('PLANE_SWAMP_GRASS',     9, u'болото'),
                                   ('PLANE_CONIFER_FOREST',  10, u'хвойный лес'),
                                   ('PLANE_GREENWOOD',       11, u'лиственный лес'),
                                   ('PLANE_SWAMP_FOREST',    12, u'заболоченный лес'),
                                   ('PLANE_JUNGLE',          13, u'джунгли'),
                                   ('PLANE_WITHERED_FOREST', 14, u'мёртвый лес'),

                                   ('HILLS_SAND',            15, u'песчаные дюны'),
                                   ('HILLS_DRY_LAND',        16, u'высохшие растрескавшиеся холмы'),
                                   ('HILLS_MUD',             17, u'грязевые холмы'),
                                   ('HILLS_DRY_GRASS',       18, u'холмы с высохшей травой'),
                                   ('HILLS_GRASS',           19, u'зелёные холмы'),
                                   ('HILLS_SWAMP_GRASS',     20, u'заболоченные холмы'),
                                   ('HILLS_CONIFER_FOREST',  21, u'хвойный лес на холмах'),
                                   ('HILLS_GREENWOOD',       22, u'лиственный лес на холмах'),
                                   ('HILLS_SWAMP_FOREST',    23, u'заболоченный лес на холмах'),
                                   ('HILLS_JUNGLE',          24, u'джунгли на холмах'),
                                   ('HILLS_WITHERED_FOREST', 25, u'мёртвый лес на холмах')

                                   ) )

PLACE_TYPE = create_enum('PLACE_TYPE', (('CITY', 0, u'город'),))


class Place(models.Model):

    MAX_NAME_LENGTH = 150

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

    modifier = models.IntegerField(null=True, default=None, choices=CITY_MODIFIERS._CHOICES)

    class Meta:
        ordering = ('name', )

    def __unicode__(self):
        return self.name
