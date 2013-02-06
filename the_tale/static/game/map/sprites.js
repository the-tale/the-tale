

pgf.tilesets = {

    main: {

        TILE_SIZE: 32,
        W: 32,
        H: 32,
        SRC: "/game/images/map.png",

        sprites: {

            hero_human_masculine:  { x: 0 * 32, y: 8 * 32 },
            hero_human_feminine:   { x: 1 * 32, y: 8 * 32 },
            hero_dwarf_masculine:  { x: 2 * 32, y: 8 * 32 },
            hero_dwarf_feminine:   { x: 3 * 32, y: 8 * 32 },
            hero_elf_masculine:    { x: 4 * 32, y: 8 * 32 },
            hero_elf_feminine:     { x: 5 * 32, y: 8 * 32 },
            hero_goblin_masculine: { x: 6 * 32, y: 8 * 32 },
            hero_goblin_feminine:  { x: 7 * 32, y: 8 * 32 },
            hero_orc_masculine:    { x: 8 * 32, y: 8 * 32 },
            hero_orc_feminine:     { x: 9 * 32, y: 8 * 32 },

            // neutral gender eual to male
            hero_human_neuter:  { x: 0 * 32, y: 8 * 32 },
            hero_dwarf_neuter:  { x: 2 * 32, y: 8 * 32 },
            hero_elf_neuter:    { x: 4 * 32, y: 8 * 32 },
            hero_goblin_neuter: { x: 6 * 32, y: 8 * 32 },
            hero_orc_neuter:    { x: 8 * 32, y: 8 * 32 },

            WATER_DEEP:            { y: 2 * 32, x: 4 * 32 },
            WATER_SHOAL:           { y: 2 * 32, x: 3 * 32 },
            MOUNTAINS_HIGH:        { y: 2 * 32, x: 1 * 32 },
            MOUNTAINS_LOW:         { y: 2 * 32, x: 0 * 32 },
            PLANE_SAND:            { y: 0 * 32, x: 1 * 32 },
            PLANE_DRY_LAND:        { y: 0 * 32, x: 3 * 32 },
            PLANE_MUD:             { y: 0 * 32, x: 4 * 32 },
            PLANE_DRY_GRASS:       { y: 0 * 32, x: 5 * 32 },
            PLANE_GRASS:           { y: 0 * 32, x: 0 * 32 },
            PLANE_SWAMP_GRASS:     { y: 0 * 32, x: 2 * 32 },
            PLANE_CONIFER_FOREST:  { y: 1 * 32, x: 0 * 32 },
            PLANE_GREENWOOD:       { y: 1 * 32, x: 1 * 32 },
            PLANE_SWAMP_FOREST:    { y: 1 * 32, x: 2 * 32 },
            PLANE_JUNGLE:          { y: 1 * 32, x: 3 * 32 },
            PLANE_WITHERED_FOREST: { y: 1 * 32, x: 5 * 32 },
            HILLS_SAND:            { y: 0 * 32, x: 7 * 32 },
            HILLS_DRY_LAND:        { y: 0 * 32, x: 11 * 32 },
            HILLS_MUD:             { y: 0 * 32, x: 10 * 32 },
            HILLS_DRY_GRASS:       { y: 0 * 32, x: 9 * 32 },
            HILLS_GRASS:           { y: 0 * 32, x: 6 * 32 },
            HILLS_SWAMP_GRASS:     { y: 0 * 32, x: 8 * 32 },
            HILLS_CONIFER_FOREST:  { y: 1 * 32, x: 6 * 32 },
            HILLS_GREENWOOD:       { y: 1 * 32, x: 7 * 32 },
            HILLS_SWAMP_FOREST:    { y: 1 * 32, x: 8 * 32 },
            HILLS_JUNGLE:          { y: 1 * 32, x: 9 * 32 },
            HILLS_WITHERED_FOREST: { y: 1 * 32, x: 10 * 32 },

            MOUNTAINS_BACKGROUND:  { y: 2 * 32, x: 2 * 32},
            JUNGLE_BACKGROUD:      { y: 1 * 32, x: 11 * 32},

            ROAD_WATER_DEEP:            'WATER_DEEP',
            ROAD_WATER_SHOAL:           'WATER_SHOAL',
            ROAD_MOUNTAINS_HIGH:        'MOUNTAINS_BACKGROUND',
            ROAD_MOUNTAINS_LOW:         'MOUNTAINS_BACKGROUND',
            ROAD_PLANE_SAND:            'PLANE_SAND',
            ROAD_PLANE_DRY_LAND:        'PLANE_DRY_LAND',
            ROAD_PLANE_MUD:             'PLANE_MUD',
            ROAD_PLANE_DRY_GRASS:       'PLANE_DRY_GRASS',
            ROAD_PLANE_GRASS:           'PLANE_GRASS',
            ROAD_PLANE_SWAMP_GRASS:     'PLANE_SWAMP_GRASS',
            ROAD_PLANE_CONIFER_FOREST:  'PLANE_GRASS',
            ROAD_PLANE_GREENWOOD:       'PLANE_GRASS',
            ROAD_PLANE_SWAMP_FOREST:    'PLANE_SWAMP_GRASS',
            ROAD_PLANE_JUNGLE:          'JUNGLE_BACKGROUD',
            ROAD_PLANE_WITHERED_FOREST: 'PLANE_SAND',
            ROAD_HILLS_SAND:            'PLANE_SAND',
            ROAD_HILLS_DRY_LAND:        'PLANE_DRY_LAND',
            ROAD_HILLS_MUD:             'PLANE_MUD',
            ROAD_HILLS_DRY_GRASS:       'PLANE_DRY_GRASS',
            ROAD_HILLS_GRASS:           'PLANE_GRASS',
            ROAD_HILLS_SWAMP_GRASS:     'PLANE_SWAMP_GRASS',
            ROAD_HILLS_CONIFER_FOREST:  'PLANE_GRASS',
            ROAD_HILLS_GREENWOOD:       'PLANE_GRASS',
            ROAD_HILLS_SWAMP_FOREST:    'PLANE_SWAMP_GRASS',
            ROAD_HILLS_JUNGLE:          'JUNGLE_BACKGROUD',
            ROAD_HILLS_WITHERED_FOREST: 'PLANE_SAND',

            city_human_small :   { y: 6 * 32, x: 0 * 32},
            city_human_medium :  { y: 6 * 32, x: 1 * 32},
            city_human_large :   { y: 6 * 32, x: 2 * 32},
            city_human_capital : { y: 6 * 32, x: 3 * 32},

            city_dwarf_small :   { y: 6 * 32, x: 4 * 32},
            city_dwarf_medium :  { y: 6 * 32, x: 5 * 32},
            city_dwarf_large :   { y: 6 * 32, x: 6 * 32},
            city_dwarf_capital : { y: 6 * 32, x: 7 * 32},

            city_elf_small :   { y: 6 * 32, x: 8 * 32},
            city_elf_medium :  { y: 6 * 32, x: 9 * 32},
            city_elf_large :   { y: 6 * 32, x: 10 * 32},
            city_elf_capital : { y: 6 * 32, x: 11 * 32},

            city_goblin_small :   { y: 7 * 32, x: 0 * 32},
            city_goblin_medium :  { y: 7 * 32, x: 1 * 32},
            city_goblin_large :   { y: 7 * 32, x: 2 * 32},
            city_goblin_capital : { y: 7 * 32, x: 3 * 32},

            city_orc_small :   { y: 7 * 32, x: 4 * 32},
            city_orc_medium :  { y: 7 * 32, x: 5 * 32},
            city_orc_large :   { y: 7 * 32, x: 6 * 32},
            city_orc_capital : { y: 7 * 32, x: 7 * 32},

            r4:      { x: 3 * 32, y: 3 * 32 },
            r3:      { x: 1 * 32, y: 3 * 32 },
            r_vert:  { x: 5 * 32, y: 3 * 32 },
            r_horiz: { x: 2 * 32, y: 3 * 32 },
            r_angle: { x: 4 * 32, y: 3 * 32 },
            r1:      { x: 0 * 32, y: 3 * 32 },

            select_land: { x: 0*32, y: 9 * 32},
            select_hero: { x: 1*32, y: 9 * 32}
        }
    }
};

// prepair tiles

for (var tilesetName in pgf.tilesets) {
    var tileset = pgf.tilesets[tilesetName];

    for (var spriteName in tileset.sprites) {
        var sprite = tileset.sprites[spriteName];

        if (typeof(sprite)=='string') continue;
        
        if (sprite.w == undefined) sprite.w = tileset.W;
        if (sprite.h == undefined) sprite.h = tileset.H;
        if (sprite.src == undefined) sprite.src = tileset.SRC;
    }
}