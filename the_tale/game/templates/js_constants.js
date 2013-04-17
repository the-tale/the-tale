
if (!window.pgf) {
    pgf = {};
}

if (!pgf.game) {
    pgf.game = {};
}

pgf.game.constants = {

    ACTOR_TYPE: {{actor_type|safe}},

    GENDER_TO_STR: {{gender_to_str|safe}},

    GENDER_TO_TEXT: {{gender_to_text|safe}},

    PERSON_TYPE_TO_TEXT: {{person_type_to_text|safe}},

    RACE_TO_STR: {{race_to_str|safe}},

    RACE_TO_TEXT: {{race_to_text|safe}},
    
    TERRAIN_ID_TO_STR: {{terrain_id_to_str|safe}},

    BUILDING_TYPE_TO_STR: {{building_type_to_str|safe}}
};
