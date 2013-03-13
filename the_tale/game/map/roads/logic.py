# coding: utf-8
from game.map.places.storage import places_storage
from game.map.roads.storage import roads_storage, waymarks_storage
from game.map.roads.prototypes import WaymarkPrototype


class Path(object):

    def __init__(self):
        self.road_id = -1
        self.length = 9999999999999999999999999999

    def update_path(self, new_length, new_road_id):
        if self.length > new_length:
            self.road_id = new_road_id
            self.length = new_length

@waymarks_storage.postpone_version_update
def update_waymarks():

    places = places_storage.all()

    roads = roads_storage.all_exists_roads()

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


    for i in xrange(places_len):
        for j in xrange(places_len):
            if paths[i][j].road_id is not None:
                road = roads_storage[paths[i][j].road_id]
            else:
                road = None

            waymark = waymarks_storage.look_for_road(point_from=places[i].id, point_to=places[j].id)

            if waymark:
                waymark.road = road
                waymark.length = paths[i][j].length
                waymark.save()
            else:
                waymark = WaymarkPrototype.create(point_from=places[i],
                                                  point_to=places[j],
                                                  road=road,
                                                  length=paths[i][j].length)

    waymarks_storage.update_version()
