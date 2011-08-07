# -*- coding: utf-8 -*-

map_width = {{ map_width }}
map_height = {{ map_height }}

places_list = (
    {% for p in places_list %}
   
    {%- if p.type == PLACE_TYPE.CITY -%}
    places.City(x={{p.x}}, y={{p.y}}, significance={{p.size}}, terrain='{{p.terrain}}', name='{{p.name}}', place_id={{p.id}}),
    {% endif -%}

    {% endfor %}
)

# places.City(x=1,  y=1,  significance=1,  terrain=constants.TERRAIN.DESERT),
# places.City(x=14, y=1,  significance=1,  terrain=constants.TERRAIN.FOREST),
# places.City(x=27, y=1,  significance=6,  terrain=constants.TERRAIN.SWAMP),
# places.City(x=5,  y=3,  significance=5,  terrain=constants.TERRAIN.DESERT),

# places.City(x=19, y=5,  significance=3,  terrain=constants.TERRAIN.FOREST),
# places.City(x=11, y=6,  significance=4,  terrain=constants.TERRAIN.DESERT),
# places.City(x=20, y=8,  significance=9,  terrain=constants.TERRAIN.GRASS),
# places.City(x=24, y=8,  significance=12, terrain=constants.TERRAIN.FOREST),

# places.City(x=1,  y=9,  significance=6,  terrain=constants.TERRAIN.FOREST),
# places.City(x=11, y=11, significance=4,  terrain=constants.TERRAIN.SWAMP),
# places.City(x=5,  y=12, significance=1,  terrain=constants.TERRAIN.GRASS),
# places.City(x=17, y=12, significance=2,  terrain=constants.TERRAIN.GRASS),

# places.City(x=24, y=13, significance=1,  terrain=constants.TERRAIN.FOREST),
# places.City(x=27, y=13, significance=1,  terrain=constants.TERRAIN.GRASS),
# places.City(x=3,  y=17, significance=10, terrain=constants.TERRAIN.GRASS),
# places.City(x=10, y=18, significance=3,  terrain=constants.TERRAIN.FOREST),

# places.City(x=19, y=17, significance=8,  terrain=constants.TERRAIN.SWAMP),
# places.City(x=28, y=19, significance=3,  terrain=constants.TERRAIN.SWAMP)
