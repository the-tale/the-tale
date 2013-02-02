
if (!window.pgf) {
    pgf = {};
}

if (!pgf.game) {
    pgf.game = {};
}

pgf.game.constants = {

    ACTOR_TYPE: {{actor_type|safe}},

    GENDER_TO_STR: {{gender_to_str|safe}},

    PERSON_TYPE_TO_STR: {{person_type_to_str|safe}},

    RACE_TO_STR: {{race_to_str|safe}},
    
    PVP_COMBAT_STYLES_ADVANTAGES: {{pvp_combat_styles_advantages|safe}}
};
