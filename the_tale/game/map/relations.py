# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from the_tale.game.map.conf import map_settings


class TERRAIN(DjangoEnum):
    records = ( ('WATER_DEEP',            0, u'глубокая вода'),
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
                )


class MAP_STATISTICS(DjangoEnum):
    records = ( ('LOWLANDS', 0, u'низины'),
                ('PLAINS', 1, u'равнины'),
                ('UPLANDS', 2, u'возвышенности'),
                ('DESERTS', 3, u'пустыни'),
                ('GRASS', 4, u'луга'),
                ('FORESTS', 5, u'леса'),)


_SPRITE_ID = -1
def sprite(name, x=0, y=0, base=None):
    global _SPRITE_ID
    _SPRITE_ID += 1

    if base is None:
        base = name

    return (name, _SPRITE_ID, name, x * map_settings.CELL_SIZE, y * map_settings.CELL_SIZE, base)

class SPRITES(DjangoEnum):
    x = Column(unique=False, primary=False)
    y = Column(unique=False, primary=False)
    base = Column(unique=False, primary=False, single_type=False)

    records = (
        # Heroes (neutral gender equal to male)
        sprite('HERO_HUMAN_MASCULINE',  x=0, y=8),
        sprite('HERO_HUMAN_FEMININE',   x=1, y=8),
        sprite('HERO_DWARF_MASCULINE',  x=2, y=8),
        sprite('HERO_DWARF_FEMININE',   x=3, y=8),
        sprite('HERO_ELF_MASCULINE',    x=4, y=8),
        sprite('HERO_ELF_FEMININE',     x=5, y=8),
        sprite('HERO_GOBLIN_MASCULINE', x=6, y=8),
        sprite('HERO_GOBLIN_FEMININE',  x=7, y=8),
        sprite('HERO_ORC_MASCULINE',    x=8, y=8),
        sprite('HERO_ORC_FEMININE',     x=9, y=8),

        sprite('HERO_HUMAN_NEUTER',     x=0, y=8),
        sprite('HERO_DWARF_NEUTER',     x=2, y=8),
        sprite('HERO_ELF_NEUTER',       x=4, y=8),
        sprite('HERO_GOBLIN_NEUTER',    x=6, y=8),
        sprite('HERO_ORC_NEUTER',       x=8, y=8),

        # Terrain
        sprite('WATER_DEEP',            y=2, x=4),
        sprite('WATER_SHOAL',           y=2, x=3),
        sprite('MOUNTAINS_HIGH',        y=2, x=1, base='MOUNTAINS_BACKGROUND'),
        sprite('MOUNTAINS_LOW',         y=2, x=0, base='MOUNTAINS_BACKGROUND'),
        sprite('PLANE_SAND',            y=0, x=1),
        sprite('PLANE_DRY_LAND',        y=0, x=3),
        sprite('PLANE_MUD',             y=0, x=4),
        sprite('PLANE_DRY_GRASS',       y=0, x=5),
        sprite('PLANE_GRASS',           y=0, x=0),
        sprite('PLANE_SWAMP_GRASS',     y=0, x=2),
        sprite('PLANE_CONIFER_FOREST',  y=1, x=0, base='PLANE_CONIFER_GRASS'),
        sprite('PLANE_GREENWOOD',       y=1, x=1, base='PLANE_GRASS'),
        sprite('PLANE_SWAMP_FOREST',    y=1, x=2, base='PLANE_SWAMP_GRASS'),
        sprite('PLANE_JUNGLE',          y=1, x=3, base='JUNGLE_BACKGROUD'),
        sprite('PLANE_WITHERED_FOREST', y=2, x=5, base='PLANE_DRY_GRASS'),
        sprite('HILLS_SAND',            y=0, x=7, base='PLANE_SAND'),
        sprite('HILLS_DRY_LAND',        y=0, x=11, base='PLANE_DRY_LAND'),
        sprite('HILLS_MUD',             y=0, x=10, base='PLANE_MUD'),
        sprite('HILLS_DRY_GRASS',       y=0, x=9, base='PLANE_DRY_GRASS'),
        sprite('HILLS_GRASS',           y=0, x=6, base='PLANE_GRASS'),
        sprite('HILLS_SWAMP_GRASS',     y=0, x=8, base='PLANE_SWAMP_GRASS'),
        sprite('HILLS_CONIFER_FOREST',  y=1, x=6, base='PLANE_CONIFER_GRASS'),
        sprite('HILLS_GREENWOOD',       y=1, x=7, base='PLANE_GRASS'),
        sprite('HILLS_SWAMP_FOREST',    y=1, x=8, base='PLANE_SWAMP_GRASS'),
        sprite('HILLS_JUNGLE',          y=1, x=9, base='JUNGLE_BACKGROUD'),
        sprite('HILLS_WITHERED_FOREST', y=2, x=6, base='PLANE_DRY_GRASS'),
        sprite('PLANE_CONIFER_GRASS',   y=2, x=7),

        sprite('MOUNTAINS_BACKGROUND',  y=2, x=2),
        sprite('JUNGLE_BACKGROUD',      y=1, x=11),

        # Cities
        sprite('CITY_HUMAN_SMALL',     y=6, x=0),
        sprite('CITY_HUMAN_MEDIUM',    y=6, x=1),
        sprite('CITY_HUMAN_LARGE',     y=6, x=2),
        sprite('CITY_HUMAN_CAPITAL',   y=6, x=3),

        sprite('CITY_DWARF_SMALL',     y=6, x=4),
        sprite('CITY_DWARF_MEDIUM',    y=6, x=5),
        sprite('CITY_DWARF_LARGE',     y=6, x=6),
        sprite('CITY_DWARF_CAPITAL',   y=6, x=7),

        sprite('CITY_ELF_SMALL',     y=6, x=8),
        sprite('CITY_ELF_MEDIUM',    y=6, x=9),
        sprite('CITY_ELF_LARGE',     y=6, x=10),
        sprite('CITY_ELF_CAPITAL',   y=6, x=11),

        sprite('CITY_GOBLIN_SMALL',     y=7, x=0),
        sprite('CITY_GOBLIN_MEDIUM',    y=7, x=1),
        sprite('CITY_GOBLIN_LARGE',     y=7, x=2),
        sprite('CITY_GOBLIN_CAPITAL',   y=7, x=3),

        sprite('CITY_ORC_SMALL',     y=7, x=4),
        sprite('CITY_ORC_MEDIUM',    y=7, x=5),
        sprite('CITY_ORC_LARGE',     y=7, x=6),
        sprite('CITY_ORC_CAPITAL',   y=7, x=7),

        # Roads
        sprite('R4',        x=3, y=3),
        sprite('R3',        x=1, y=3),
        sprite('R_VERT',    x=5, y=3),
        sprite('R_HORIZ',   x=2, y=3),
        sprite('R_ANGLE',   x=4, y=3),
        sprite('R1',        x=0, y=3),

        # cursors
        sprite('SELECT_LAND',         x=0, y=9),
        sprite('CELL_HIGHLIGHTING',   x=1, y=9),

        # buildings
        sprite('BUILDING_SAWMILL',        y=4, x=0),
        sprite('BUILDING_WATCHTOWER',     y=4, x=1),
        sprite('BUILDING_MAGE_TOWER',     y=4, x=2),
        sprite('BUILDING_SCAFFOLD',       y=4, x=3),
        sprite('BUILDING_RANCH',          y=4, x=4),
        sprite('BUILDING_SMITHY',         y=4, x=5),
        sprite('BUILDING_HUNTER_HOUSE',   y=4, x=6),
        sprite('BUILDING_FISHING_LODGE',  y=4, x=7),
        sprite('BUILDING_TRADING_POST',   y=4, x=8),
        sprite('BUILDING_INN',            y=4, x=9),
        sprite('BUILDING_FARM',           y=4, x=10),
        sprite('BUILDING_MINE',           y=4, x=11),
        sprite('BUILDING_TEMPLE',         y=5, x=0),
        sprite('BUILDING_LABORATORY',     y=5, x=1),
        sprite('BUILDING_HOSPITAL',       y=5, x=2),
        sprite('BUILDING_MANOR',          y=5, x=3),
        sprite('BUILDING_DEN_OF_THIEVE',  y=5, x=4),
        sprite('BUILDING_GUILDHALL',      y=5, x=5),
        sprite('BUILDING_MEWS',           y=5, x=6),
        sprite('BUILDING_SCENE',          y=5, x=7),
        sprite('BUILDING_TAILOR_SHOP',    y=5, x=8),
        sprite('BUILDING_BUREAU',         y=5, x=9) )
