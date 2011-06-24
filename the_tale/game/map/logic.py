# -*- coding: utf-8 -*-

from .places.logic import get_places_info
from .roads.logic import get_roads_info

def get_map_info():
    info = {}

    info['places'] = get_places_info()
    info['roads'] = get_roads_info()

    return info
