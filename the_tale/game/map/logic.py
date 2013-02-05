# -*- coding: utf-8 -*-

from .roads.logic import get_roads_info

from game.map.places.storage import places_storage

# def get_map_info():
#     info = {}

#     info['places'] = dict([ (place.id, place.map_info()) for place in places_storage.all()])
#     info['roads'] = get_roads_info()

#     return info
