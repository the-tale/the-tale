# -*- coding: utf-8 -*-
import math

from game.map.conf import map_settings
from game.map.places.conf import places_settings
from game.map.places.models import Place
from game.map.places.prototypes import get_place_by_model

E = 0.01

def dst(x, y, x2, y2):
    return math.sqrt((x-x2)**2 + (y-y2)**2)

def get_places_info():
    places = {}
    for place_model in Place.objects.all():
        place = get_place_by_model(place_model)
        places[place.id] = place.map_info()

    return places

def update_nearest_cells():
    places = [get_place_by_model(model) for model in Place.objects.all()]

    for place in places:
        place.nearest_cells = []

    for x in xrange(0, map_settings.WIDTH):
        for y in xrange(0, map_settings.HEIGHT):
            nearest_place = None
            nearest_power = 0

            for place in places:
                cur_dst = dst(x, y, place.x, place.y)

                if cur_dst < E:
                    place_power = places_settings.MAX_SIZE**2
                else:
                    place_power = float(place.size) / (cur_dst**2)

                if nearest_power < place_power:
                    nearest_place = place
                    nearest_power = place_power

            if nearest_place:
                nearest_place.nearest_cells.append((x, y))


    for place in places:
        place.save()
