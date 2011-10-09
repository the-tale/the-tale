
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
        "use_form": {% if ability.need_form() %}true{% else %}false{% endif %},
        "name": "{{ ability.NAME }}",
        "description": "{{ ability.DESCRIPTION }}",
        "artistic": "{{ ability.ARTISTIC }}",
        "limited": {% if ability.LIMITED %}true{% else %}false{% endif %}
    }{%- if not loop.last -%},{%- endif -%}
    
    {% endfor %}

}