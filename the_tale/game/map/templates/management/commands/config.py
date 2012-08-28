# -*- coding: utf-8 -*-

map_width = {{ map_width }}
map_height = {{ map_height }}

places_list = (
    {% for p in places_list %}

    {%- if p.type == PLACE_TYPE.CITY -%}
    places.City(x={{p.x}}, y={{p.y}}, significance={{p.size}}, terrain='{{p.terrain}}', name='{{p.name}}', place_id={{p.id}}, size={{p.size}}),
    {% endif -%}

    {% endfor %}
)

roads_list = (
    {% for r in roads_list %}

    roads.Road(road_id={{ r.id }}, point_1={{ r.point_1_id }}, point_2={{ r.point_2_id }}, length={{ r.length }}, exists={{r.exists}}),

    {% endfor %}
)
