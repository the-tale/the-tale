
import smart_imports

smart_imports.all()


class Path(object):

    def __init__(self):
        self.road_id = -1
        self.length = 9999999999999999999999999999

    def update_path(self, new_length, new_road_id):
        if self.length > new_length:
            self.road_id = new_road_id
            self.length = new_length


@storage.waymarks.postpone_version_update
def update_waymarks():  # pylint: disable=R0912

    places = places_storage.places.all()

    roads = storage.roads.all_exists_roads()

    places_len = len(places)

    paths = [[Path() for place in range(places_len)] for i in range(places_len)]  # pylint: disable=W0612

    p2i = dict((place.id, i) for i, place in enumerate(places))

    for i in range(len(places)):
        paths[i][i].update_path(0, None)

    for road in roads:
        i = p2i[road.point_1_id]
        j = p2i[road.point_2_id]
        paths[i][j].update_path(road.length, road.id)
        paths[j][i].update_path(road.length, road.id)

    for k in range(places_len):
        for i in range(places_len):
            for j in range(places_len):
                new_len = min(paths[i][j].length,
                              paths[i][k].length + paths[k][j].length)
                paths[i][j].update_path(new_len, paths[i][k].road_id)

    for row in paths:
        res = []
        for el in row:
            res.append(el.road_id)

    for i in range(places_len):
        for j in range(places_len):
            if paths[i][j].road_id is not None:
                road = storage.roads[paths[i][j].road_id]
            else:
                road = None

            waymark = storage.waymarks.look_for_road(point_from=places[i].id, point_to=places[j].id)

            if waymark:
                waymark.road = road
                waymark.length = paths[i][j].length
                waymark.save()
            else:
                waymark = prototypes.WaymarkPrototype.create(point_from=places[i],
                                                             point_to=places[j],
                                                             road=road,
                                                             length=paths[i][j].length)

    storage.waymarks.update_version()


def road_between_places(place_1, place_2):
    for road in storage.roads.all():

        if not road.exists:
            continue

        if (road.point_1_id == place_1.id and road.point_2_id == place_2.id or
                road.point_1_id == place_2.id and road.point_2_id == place_1.id):
            return road

    return None


def get_places_connected_to(place):
    places_ids = set()

    for road in storage.roads.all():
        if not road.exists:
            continue

        if road.point_1_id == place.id:
            places_ids.add(road.point_2_id)
            continue

        if road.point_2_id == place.id:
            places_ids.add(road.point_1_id)

    return (places_storage.places[place_id] for place_id in places_ids)
