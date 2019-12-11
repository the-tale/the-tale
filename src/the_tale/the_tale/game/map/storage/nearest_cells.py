
import smart_imports

smart_imports.all()


E = 0.01
GUARANTIED_RADIUS = math.sqrt(1 + 1) + E  # guarantied raidius of places cells
SKIPPED_ANGLE = math.pi / 6


def dst(x, y, x2, y2):
    return math.sqrt((x - x2)**2 + (y - y2)**2)


def skip_one(x, y, current_place, checked_place):
    current_angle = math.atan2(y - current_place.y, x - current_place.x)
    checked_angle = math.atan2(y - checked_place.y, x - checked_place.x)
    return abs(current_angle - checked_angle) < SKIPPED_ANGLE


def get_availabled_places(x, y, reset_cache=False, cache={}):

    if django_settings.TESTS_RUNNING:
        cache.clear()

    if (x, y) in cache:
        return cache[(x, y)]

    places = []

    for checked_place in places_storage.places.all():
        can_be_taken = True
        checked_dst = dst(x, y, checked_place.x, checked_place.y)

        for other_place in places_storage.places.all():
            if checked_place.id == other_place.id:
                continue

            other_dst = dst(x, y, other_place.x, other_place.y)

            if skip_one(x, y, checked_place, other_place):
                if checked_dst > other_dst:
                    can_be_taken = False
                    break

        if can_be_taken:
            places.append((checked_dst, checked_place.id))

    cache[(x, y)] = places

    return places


def _get_dominant_place_id_by_position(x, y):
    nearest_place_id = None
    nearest_power = 0

    for cur_dst, place_id in get_availabled_places(x, y):

        place = places_storage.places[place_id]

        if cur_dst > place.attrs.politic_radius:
            continue

        if cur_dst < GUARANTIED_RADIUS:
            place_power = c.PLACE_MAX_SIZE**2 + place.attrs.size
        else:
            place_power = float(place.attrs.size) / (cur_dst**2)

        if nearest_power < place_power:
            nearest_place_id = place.id
            nearest_power = place_power

    return nearest_place_id


def _get_place_politic_power_on_road(road, x, y):
    if road.place_1.attrs.politic_radius + road.place_2.attrs.politic_radius == 0:
        # initial or test map
        border = 0.5
    else:
        border = road.place_1.attrs.politic_radius / (road.place_1.attrs.politic_radius + road.place_2.attrs.politic_radius)

    cells = road.get_cells()

    cell_index = cells.index((x, y))

    cell_percents = cell_index / (len(cells) - 1)

    if cell_percents < border:
        target_place = road.place_1
    else:
        target_place = road.place_2
        cell_percents = 1.0 - cell_percents

    place_power = (1.0 - cell_percents) * road.place_1.attrs.politic_radius

    return target_place, place_power


def _get_dominant_place_id_by_roads(map, x, y):
    dominant_place_id = None
    dominant_place_power = -1

    for road_id in map[y][x].roads_ids:
        road = roads_storage.roads[road_id]

        target_place, place_power = _get_place_politic_power_on_road(road, x, y)

        if dominant_place_power < place_power:
            dominant_place_power = place_power
            dominant_place_id = target_place.id

    return dominant_place_id


def _update_dominant_place(map):
    for x in range(0, map_conf.settings.WIDTH):
        for y in range(0, map_conf.settings.HEIGHT):
            map[y][x].dominant_place_id = _get_dominant_place_id_by_position(x, y)

    for place in places_storage.places.all():
        map[place.y][place.x].dominant_place_id = place.id
        map[place.y][place.x].place_id = place.id

    for building in places_storage.buildings.all():
        map[building.y][building.x].dominant_place_id = building.place.id
        map[building.y][building.x].building_id = building.id

    for x in range(0, map_conf.settings.WIDTH):
        for y in range(0, map_conf.settings.HEIGHT):
            if not map[y][x].roads_ids:
                continue

            map[y][x].dominant_place_id = _get_dominant_place_id_by_roads(map, x, y)


def _update_roads_lists(map):
    for road in roads_storage.roads.all():
        for x, y in road.get_cells():
            map[y][x].roads_ids.append(road.id)


def _update_nearest_place(map):
    for x in range(0, map_conf.settings.WIDTH):
        for y in range(0, map_conf.settings.HEIGHT):
            cell = map[y][x]

            if cell.dominant_place_id is not None:
                cell.nearest_place_id = cell.dominant_place_id
                continue

            best_distance = 999999999

            for place in places_storage.places.all():
                distance = dst(x, y, place.x, place.y)

                if distance < best_distance:
                    best_distance = distance
                    cell.nearest_place_id = place.id


def update(map):
    _update_roads_lists(map)
    _update_dominant_place(map)
    _update_nearest_place(map)
