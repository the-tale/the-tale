
import smart_imports

smart_imports.all()

MAX_DISTANCE_BETWEEN_CONNECTED_PLACES = 25


def distance(x_1, y_1, x_2, y_2):
    return abs(x_1 - x_2) + abs(y_1 - y_2)


def allowed_places_pairs(max_distance_between_places):
    for place_1 in places_storage.places.all():
        for place_2 in places_storage.places.all():
            if place_1.id >= place_2.id:
                continue

            min_distance = distance(place_1.x, place_1.y, place_2.x, place_2.y)

            if (min_distance > max_distance_between_places and
                roads_logic.road_between_places(place_1, place_2) is None):
                continue

            yield (place_1, place_2)


def build_paths(travel_cost, places_pairs):
    paths = {}

    for place_1, place_2 in places_pairs:
        path, cost = pathfinder.find_path_between_places(start_place=place_1,
                                                         finish_place=place_2,
                                                         travel_cost=travel_cost)
        # base paths must be storen in unmutable tuples, to prevent any chance of modification of them
        paths[(place_1.id, place_2.id)] = (tuple(path), cost)
        paths[(place_2.id, place_1.id)] = (tuple(reversed(path)), cost)

    return paths


def get_path_between_places(from_place_id, to_place_id, paths, cost_modifiers):
    if from_place_id == to_place_id:
        place = places_storage.places[from_place_id]
        return path.Path(cells=[(place.x, place.y)]), 0

    meta_path = waypoints.search_meta_path(from_id=from_place_id,
                                           to_id=to_place_id,
                                           cost_modifiers=cost_modifiers,
                                           paths=paths)

    cells, cost = paths[(meta_path[0], meta_path[1])]

    full_path = path.Path(cells=cells)
    full_cost = cost

    current_place_id = meta_path[1]

    for next_place_id in meta_path[2:]:
        cells, cost = paths[(current_place_id, next_place_id)]

        full_cost += cost
        full_path.append(path.Path(cells))

        current_place_id = next_place_id

    return full_path, full_cost


class Navigator:
    __slots__ = ('_paths', '_travel_cost')

    def __init__(self):
        self._paths = None
        self._travel_cost = None

    def sync(self, travel_cost):
        places_pairs = allowed_places_pairs(max_distance_between_places=MAX_DISTANCE_BETWEEN_CONNECTED_PLACES)

        self._paths = build_paths(travel_cost=travel_cost,
                                  places_pairs=places_pairs)

        self._travel_cost = travel_cost

    def get_path_between_places(self, from_place_id, to_place_id, cost_modifiers):
        path_and_cost = get_path_between_places(from_place_id=from_place_id,
                                                to_place_id=to_place_id,
                                                paths=self._paths,
                                                cost_modifiers=cost_modifiers)
        return path_and_cost

    def _calculate_shortest_path(self, from_x, from_y, to_x, to_y):
        cells, cost = pathfinder.find_shortest_path(from_x=from_x,
                                                    from_y=from_y,
                                                    to_x=to_x,
                                                    to_y=to_y,
                                                    width=map_conf.settings.WIDTH,
                                                    height=map_conf.settings.HEIGHT,
                                                    travel_cost=self._travel_cost,
                                                    excluded_cells=())
        return path.Path(cells=cells), cost

    def build_path_to_place(self, from_x, from_y, to_place_id, cost_modifiers):

        cell = map_storage.cells(from_x, from_y)

        if cell.place_id is not None:
            path, cost = self.get_path_between_places(from_place_id=cell.place_id,
                                                      to_place_id=to_place_id,
                                                      cost_modifiers=cost_modifiers)
            return path

        main_path_1, main_cost_1 = self.get_path_between_places(from_place_id=cell.nearest_place_id,
                                                                to_place_id=to_place_id,
                                                                cost_modifiers=cost_modifiers)

        nearest_place = cell.nearest_place()

        path_1, cost_1 = self._calculate_shortest_path(from_x=from_x,
                                                       from_y=from_y,
                                                       to_x=nearest_place.x,
                                                       to_y=nearest_place.y)

        cost_1 += main_cost_1

        _, alternative_place_id = main_path_1.next_place_at(percents=0.0001)

        if alternative_place_id is None:
            path_1.append(main_path_1)
            return path_1

        main_path_2, main_cost_2 = self.get_path_between_places(from_place_id=alternative_place_id,
                                                                to_place_id=to_place_id,
                                                                cost_modifiers=cost_modifiers)

        alternative_place = places_storage.places[alternative_place_id]

        path_2, cost_2 = self._calculate_shortest_path(from_x=from_x,
                                                       from_y=from_y,
                                                       to_x=alternative_place.x,
                                                       to_y=alternative_place.y)

        cost_2 += main_cost_2

        if cost_1 < cost_2:
            path_1.append(main_path_1)
            return path_1

        path_2.append(main_path_2)
        return path_2
