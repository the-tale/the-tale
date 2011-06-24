# -*- coding: utf-8 -*-
from django_next.utils.decorators import nested_commit_on_success

from ..places.models import Place
from ..places.prototypes import get_place_by_model
from .models import Road
from .prototypes import RoadPrototype, RoadsException, get_road_by_model, get_road_between

@nested_commit_on_success
def update_roads():
    places = list(Place.objects.all())
    places = [get_place_by_model(model) for model in places]

    for point_1 in places:
        for point_2 in places:
            if point_1.id >= point_2.id: 
                continue
            try:
                RoadPrototype.create(point_1, point_2)
            except RoadsException:
                get_road_between(point_1, point_2).update()


@nested_commit_on_success
def regenerate_roads():
    Road.objects.all().delete()

    places = list(Place.objects.all())
    places = [get_place_by_model(model) for model in places]

    for point_1 in places:
        for point_2 in places:
            if point_1.id >= point_2.id: 
                continue
            RoadPrototype.create(point_1, point_2)


def get_roads_info():
    roads = {}
    for road_model in Road.objects.all():
        road = get_road_by_model(road_model)

        road_info = road.map_info()

        if road.point_1_id not in roads:
            roads[road.point_1_id] = {}

        roads[road.point_1_id][road.point_1_id] = road_info

    return roads


