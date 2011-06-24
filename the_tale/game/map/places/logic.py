# -*- coding: utf-8 -*-

from .models import Place
from .prototypes import get_place_by_model

def get_places_info():
    places = {}
    for place_model in Place.objects.all():
        place = get_place_by_model(place_model)
        places[place.id] = place.map_info()

    return places
