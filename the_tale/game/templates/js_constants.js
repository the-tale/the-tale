
if (!window.pgf) {
    pgf = {};
}

if (!pgf.game) {
    pgf.game = {};
}

pgf.game.constants = {

    ACTOR_TYPE: {{actor_type|safe}},

    GENDER_TO_TEXT: {{gender_to_text|safe}},
    GENDER_TO_STR: {{gender_to_str|safe}},

    PERSON_TYPE_TO_TEXT: {{person_type_to_text|safe}},

    RACE_TO_TEXT: {{race_to_text|safe}},
    RACE_TO_STR: {{race_to_str|safe}},
};

pgf.game.constants.abilities = {

    {% for ability_type in ABILITY_TYPE.records %}

    "{{ ability_type.value }}": {
        "type": "{{ ability_type.value }}",
        "name": "{{ ability_type.text }}",
        "description": "{{ ability_type.description }}",
        "cost": {{ ability_type.cost }}
    }{%- if not loop.last -%},{%- endif -%}

    {% endfor %}

}

pgf.game.constants.sprites = {

    {% for sprite in SPRITES.records %}

    "{{ sprite.value }}": {
        "x": "{{ sprite.x }}",
        "y": "{{ sprite.y }}"
    },

    {% endfor %}

    "{{SPRITES.CELL_HIGHLIGHTING.name}}": "{{SPRITES.CELL_HIGHLIGHTING.value}}",
    "{{SPRITES.SELECT_LAND.name}}": "{{SPRITES.SELECT_LAND.value}}"

}

pgf.game.constants.tilesets = {

    main: {
        TILE_SIZE: {{CELL_SIZE}},
        W: {{CELL_SIZE}},
        H: {{CELL_SIZE}},
        SRC: "/game/images/map.png",
        sprites: jQuery.extend(true, {}, pgf.game.constants.sprites)
    },

    winter: {
        TILE_SIZE: {{CELL_SIZE}},
        W: {{CELL_SIZE}},
        H: {{CELL_SIZE}},
        SRC: "/game/images/map_winter.png",
        sprites: jQuery.extend(true, {}, pgf.game.constants.sprites)
    },

    large_pixel: {
        TILE_SIZE: {{CELL_SIZE}},
        W: {{CELL_SIZE}},
        H: {{CELL_SIZE}},
        SRC: "/game/images/map_large_pixel.png",
        sprites: jQuery.extend(true, {}, pgf.game.constants.sprites)
    }
};


for (var tilesetName in pgf.game.constants.tilesets) {
    var tileset = pgf.game.constants.tilesets[tilesetName];

    for (var spriteName in tileset.sprites) {
        var sprite = tileset.sprites[spriteName];

        if (typeof(sprite)=='string') continue;

        if (sprite.w == undefined) sprite.w = tileset.W;
        if (sprite.h == undefined) sprite.h = tileset.H;
        if (sprite.src == undefined) sprite.src = tileset.SRC;
    }
}
