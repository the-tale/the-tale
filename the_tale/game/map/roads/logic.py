# -*- coding: utf-8 -*-
from dext.utils.decorators import nested_commit_on_success

from ..places.models import Place
from ..places.prototypes import get_place_by_model
from .models import Road, Waymark
from .prototypes import WaymarkPrototype, get_road_by_model, get_road_by_id

@nested_commit_on_success
def update_roads():
    roads = [ get_road_by_model(road) for road in list(Road.objects.all()) ]
    for road in roads:
        road.update()

def get_roads_info():
    roads = {}
    for road_model in Road.objects.all():
        road = get_road_by_model(road_model)

        road_info = road.map_info()

        if road.point_1_id not in roads:
            roads[road.point_1_id] = {}

        roads[road.point_1_id][road.point_1_id] = road_info

    return roads


class Path(object):

    def __init__(self):
        self.road_id = -1
        self.length = 9999999999999999999999999999

    def update_path(self, new_length, new_road_id):
        if self.length > new_length:
            self.road_id = new_road_id
            self.length = new_length

def update_waymarks():
    
    places = [ get_place_by_model(place) for place in list(Place.objects.all()) ]

    roads = [ get_road_by_model(road) for road in list(Road.objects.all()) ]

    places_len = len(places)

    paths = [ [ Path() for place in xrange(places_len) ] for i in xrange(places_len)]

    p2i = dict( (place.id, i) for i, place in enumerate(places))

    for i in xrange(len(places)):
        paths[i][i].update_path(0, None)

    for road in roads:
        i = p2i[road.point_1_id]
        j = p2i[road.point_2_id]
        paths[i][j].update_path(road.length, road.id)
        paths[j][i].update_path(road.length, road.id)

    for k in xrange(places_len):
        for i in xrange(places_len):
            for j in xrange(places_len):
                new_len = min(paths[i][j].length, 
                              paths[i][k].length + paths[k][j].length)
                paths[i][j].update_path(new_len, paths[i][k].road_id)

    for row in paths:
        res = []
        for el in row:
            res.append(el.road_id)

    with nested_commit_on_success():
        # Waymark.objects.all().delete()

        for i in xrange(places_len):
            for j in xrange(places_len):
                if paths[i][j].road_id is not None:
                    road = get_road_by_id(paths[i][j].road_id)
                else:
                    road = None

                if Waymark.objects.filter(point_from=places[i].model, point_to=places[j].model).exists():
                    Waymark.objects.filter(point_from=places[i].model, point_to=places[j].model).update(road=road.model if road else None,
                                                                                                        length=paths[i][j].length)
                else:
                    WaymarkPrototype.create(point_from=places[i],
                                            point_to=places[j],
                                            road=road,
                                            length=paths[i][j].length)

