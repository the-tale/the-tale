# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

class META_TERRAIN(DjangoEnum):
    records = ( ('WATER', 0, 'вода'),
                ('MOUNTAINS', 1, 'горы'),
                ('DESERT', 2, 'пустыня'),
                ('SWAMP', 3, 'болото'),
                ('NORMAL', 4, 'зелень'),
                ('JUNGLE', 5, 'джунгли') )

class META_HEIGHT(DjangoEnum):
    records = ( ('WATER', 0, 'вода'),
                ('PLAINS', 1, 'равнины'),
                ('HILLS', 2, 'холмы'),
                ('MOUNTAINS', 3, 'горы') )

class META_VEGETATION(DjangoEnum):
    records = ( ('NONE', 0, 'нет'),
                ('GRASS', 1, 'трава'),
                ('TREES', 2, 'деревья') )

class TERRAIN(DjangoEnum):
    meta_height = Column(unique=False, primary=False)
    meta_terrain = Column(unique=False, primary=False)
    meta_vegetation = Column(unique=False, primary=False)

    records = ( ('WATER_DEEP',            0, 'глубокая вода',                   META_HEIGHT.WATER, META_TERRAIN.WATER, META_VEGETATION.NONE),
                ('WATER_SHOAL',           1, 'мелкая вода',                     META_HEIGHT.WATER, META_TERRAIN.WATER, META_VEGETATION.NONE),
                ('MOUNTAINS_HIGH',        2, 'высокие горы',                    META_HEIGHT.MOUNTAINS, META_TERRAIN.MOUNTAINS, META_VEGETATION.NONE),
                ('MOUNTAINS_LOW',         3, 'низкие горы',                     META_HEIGHT.MOUNTAINS, META_TERRAIN.MOUNTAINS, META_VEGETATION.NONE),

                ('PLANE_SAND',            4, 'пустыня',                         META_HEIGHT.PLAINS, META_TERRAIN.DESERT, META_VEGETATION.NONE),
                ('PLANE_DRY_LAND',        5, 'высохшая растрескавшаяся земля',  META_HEIGHT.PLAINS, META_TERRAIN.DESERT, META_VEGETATION.NONE),
                ('PLANE_MUD',             6, 'грязь',                           META_HEIGHT.PLAINS, META_TERRAIN.SWAMP, META_VEGETATION.NONE),
                ('PLANE_DRY_GRASS',       7, 'сухие луга',                      META_HEIGHT.PLAINS, META_TERRAIN.NORMAL, META_VEGETATION.GRASS),
                ('PLANE_GRASS',           8, 'луга',                            META_HEIGHT.PLAINS, META_TERRAIN.NORMAL, META_VEGETATION.GRASS),
                ('PLANE_SWAMP_GRASS',     9, 'болото',                          META_HEIGHT.PLAINS, META_TERRAIN.SWAMP, META_VEGETATION.GRASS),
                ('PLANE_CONIFER_FOREST',  10, 'хвойный лес',                    META_HEIGHT.PLAINS, META_TERRAIN.NORMAL, META_VEGETATION.TREES),
                ('PLANE_GREENWOOD',       11, 'лиственный лес',                 META_HEIGHT.PLAINS, META_TERRAIN.NORMAL, META_VEGETATION.TREES),
                ('PLANE_SWAMP_FOREST',    12, 'заболоченный лес',               META_HEIGHT.PLAINS, META_TERRAIN.SWAMP, META_VEGETATION.TREES),
                ('PLANE_JUNGLE',          13, 'джунгли',                        META_HEIGHT.PLAINS, META_TERRAIN.JUNGLE, META_VEGETATION.TREES),
                ('PLANE_WITHERED_FOREST', 14, 'мёртвый лес',                    META_HEIGHT.PLAINS, META_TERRAIN.DESERT, META_VEGETATION.TREES),

                ('HILLS_SAND',            15, 'песчаные дюны',                  META_HEIGHT.HILLS, META_TERRAIN.DESERT, META_VEGETATION.NONE),
                ('HILLS_DRY_LAND',        16, 'высохшие растрескавшиеся холмы', META_HEIGHT.HILLS, META_TERRAIN.DESERT, META_VEGETATION.NONE),
                ('HILLS_MUD',             17, 'грязевые холмы',                 META_HEIGHT.HILLS, META_TERRAIN.SWAMP, META_VEGETATION.NONE),
                ('HILLS_DRY_GRASS',       18, 'холмы с высохшей травой',        META_HEIGHT.HILLS, META_TERRAIN.NORMAL, META_VEGETATION.GRASS),
                ('HILLS_GRASS',           19, 'зелёные холмы',                  META_HEIGHT.HILLS, META_TERRAIN.NORMAL, META_VEGETATION.GRASS),
                ('HILLS_SWAMP_GRASS',     20, 'заболоченные холмы',             META_HEIGHT.HILLS, META_TERRAIN.SWAMP, META_VEGETATION.GRASS),
                ('HILLS_CONIFER_FOREST',  21, 'хвойный лес на холмах',          META_HEIGHT.HILLS, META_TERRAIN.NORMAL, META_VEGETATION.TREES),
                ('HILLS_GREENWOOD',       22, 'лиственный лес на холмах',       META_HEIGHT.HILLS, META_TERRAIN.NORMAL, META_VEGETATION.TREES),
                ('HILLS_SWAMP_FOREST',    23, 'заболоченный лес на холмах',     META_HEIGHT.HILLS, META_TERRAIN.SWAMP, META_VEGETATION.TREES),
                ('HILLS_JUNGLE',          24, 'джунгли на холмах',              META_HEIGHT.HILLS, META_TERRAIN.JUNGLE, META_VEGETATION.TREES),
                ('HILLS_WITHERED_FOREST', 25, 'мёртвый лес на холмах',          META_HEIGHT.HILLS, META_TERRAIN.DESERT, META_VEGETATION.TREES)
              )
