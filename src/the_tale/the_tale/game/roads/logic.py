
import smart_imports

smart_imports.all()


def road_between_places(place_1, place_2):
    for road in storage.roads.all():

        if (road.place_1_id == place_1.id and road.place_2_id == place_2.id or
            road.place_1_id == place_2.id and road.place_2_id == place_1.id):
            return road

    return None


def get_roads_connected_to(place):
    roads = []

    for road in storage.roads.all():

        if road.place_1_id == place.id:
            roads.append(road)

        elif road.place_2_id == place.id:
            roads.append(road)

    return roads


def get_places_connected_to(place):
    places_ids = set()

    for road in get_roads_connected_to(place):
        if road.place_1_id != place.id:
            places_ids.add(road.place_1_id)
        else:
            places_ids.add(road.place_2_id)

    return [places_storage.places[place_id] for place_id in places_ids]


def reverse_path(path):
    return ''.join(relations.PATH_DIRECTION(c).reversed for c in path[::-1])


def load_road(road_id=None, road_model=None):

    if road_model is None:
        road_model = models.Road.objects.get(id=road_id)

    return objects.Road(id=road_model.id,
                        place_1_id=road_model.point_1.id,
                        place_2_id=road_model.point_2.id,
                        length=road_model.length,
                        path=road_model.path)


def create_road(place_1, place_2, path):
    if place_1.id > place_2.id:
        place_1, place_2 = place_2, place_1
        path = reverse_path(path)

    length = len(path)

    road_model = models.Road.objects.create(point_1_id=place_1.id,
                                            point_2_id=place_2.id,
                                            length=length,
                                            path=path)

    road = load_road(road_model=road_model)

    storage.roads.add_item(road.id, road)
    storage.roads.update_version()

    return road


def delete_road(road_id):
    models.Road.objects.filter(id=road_id).delete()
    storage.roads.update_version()
    storage.roads.refresh()


def change_road(road_id, path):
    road = storage.roads[road_id]

    cells = get_path_cells(road.place_1.x, road.place_1.y, path)

    if cells[-1] != (road.place_2.x, road.place_2.y):
        path = reverse_path(path)

    cells = get_path_cells(road.place_1.x, road.place_1.y, path)

    if cells[-1] != (road.place_2.x, road.place_2.y):
        raise exceptions.RoadPathMustEndInPlace(road=road_id, path=path)

    models.Road.objects.filter(id=road_id).update(path=path)
    storage.roads.update_version()
    storage.roads.refresh()


def get_path_cells(start_x, start_y, path):
    x, y = start_x, start_y

    cells = [(x, y)]

    for direction in path:
        if direction == roads_relations.PATH_DIRECTION.LEFT.value:
            x -= 1
        elif direction == roads_relations.PATH_DIRECTION.RIGHT.value:
            x += 1
        elif direction == roads_relations.PATH_DIRECTION.UP.value:
            y -= 1
        elif direction == roads_relations.PATH_DIRECTION.DOWN.value:
            y += 1

        cells.append((x, y))

    return cells


def is_path_suitable_for_road(start_x, start_y, path):

    if not ({c for c in path} <= {direction.value for direction in relations.PATH_DIRECTION.records}):
        return relations.ROAD_PATH_ERRORS.WRONG_FORMAT

    cells = get_path_cells(start_x, start_y, path)

    for building in places_storage.buildings.all():
        if (building.x, building.y) in cells:
            return relations.ROAD_PATH_ERRORS.PASS_THROUGH_BUILDING

    places_cells = {(place.x, place.y) for place in places_storage.places.all()}

    if places_cells & set(cells[1:-1]):
        return relations.ROAD_PATH_ERRORS.PASS_THROUGH_PLACE

    if cells[0] not in places_cells:
        return relations.ROAD_PATH_ERRORS.NO_START_PLACE

    if cells[-1] not in places_cells:
        return relations.ROAD_PATH_ERRORS.NO_FINISH_PLACE

    for x, y in cells:
        if (x < 0 or
            y < 0 or
            map_conf.settings.WIDTH <= x or
            map_conf.settings.HEIGHT <= y):
            return relations.ROAD_PATH_ERRORS.CELL_NOT_ON_MAP

    if len(cells) != len(set(cells)):
        return relations.ROAD_PATH_ERRORS.HAS_CYCLES

    return relations.ROAD_PATH_ERRORS.NO_ERRORS


def road_support_cost(cells,
                      stabilization_price=c.CELL_STABILIZATION_PRICE,
                      roads_number_getter=None):

    from the_tale.game.map import storage as map_storage

    if roads_number_getter is None:
        roads_number_getter = lambda x, y: len(map_storage.cells(x, y).roads_ids)

    production = 0

    for x, y in cells:
        roads_number = roads_number_getter(x, y)

        cell_price = float(stabilization_price) / roads_number

        production += cell_price

    return production
