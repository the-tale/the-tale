
if (!window.pgf) {
    pgf = {};
}

if (!pgf.game) {
    pgf.game = {};
}

if (!pgf.game.data) {
    pgf.game.data = {};
}

pgf.game.data.abilities = {
    
    {% for ability_type, ability in abilities.items() %}

    "{{ ability_type }}": {
        "type": "{{ ability_type }}",
        "use_form": true,
        "name": "{{ ability.NAME }}",
        "description": "{{ ability.DESCRIPTION }}",
        "artistic": "{{ ability.ARTISTIC }}"
    }{%- if not loop.last -%},{%- endif -%}
    
    {% endfor %}

}