# -*- coding: utf-8 -*-
import math

from game.map.conf import map_settings
from game.map.places.storage import places_storage
from game.map.places.conf import places_settings

E = 0.01

def dst(x, y, x2, y2):
    return math.sqrt((x-x2)**2 + (y-y2)**2)

def update_nearest_cells():
    places = places_storage.all()

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

    places_storage.save_all()
