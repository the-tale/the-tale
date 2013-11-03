# coding: utf-8

from the_tale.common.utils.enum import create_enum

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

MAP_STATISTICS = create_enum('MAP_STATISTICS', ( ('LOWLANDS', 0, u'низины'),
                                                 ('PLAINS', 1, u'равнины'),
                                                 ('UPLANDS', 2, u'возвышенности'),
                                                 ('DESERTS', 3, u'пустыни'),
                                                 ('GRASS', 4, u'луга'),
                                                 ('FORESTS', 5, u'леса'),) )
