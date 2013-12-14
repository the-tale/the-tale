
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

    TERRAIN_ID_TO_STR: {{terrain_id_to_str|safe}},

    BUILDING_TYPE_TO_STR: {{building_type_to_str|safe}}
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
