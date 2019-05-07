
import smart_imports

smart_imports.all()


# path time calculated in turns for normal_hero_speed


def neighbours_coordinates(x, y, width, height):
    cells = ((x - 1, y),
             (x, y - 1),
             (x, y + 1),
             (x + 1, y))

    for cell_x, cell_y in cells:
        if (0 <= cell_x < width and
            0 <= cell_y < height):
            yield (cell_x, cell_y)


def cell_travel_cost(transport, safety, expected_battle_complexity):
    # «Правильная» оценка стоимсти пути, к сожалению, не показала себя хорошо
    # из-за перекоса в баласне в сторону боёв
    # поэтому её не используем, оставлена на будущее (если уменьшится перекос или вообще баланс изменится)

    # transport_turns = 1.0 / (c.HERO_MOVE_SPEED * transport)
    # battles_number = transport_turns * battles_per_turn
    # battles_turns = battles_number * (c.BATTLE_LENGTH * expected_battle_complexity)
    # rest_turns = (battles_number * expected_battle_complexity / c.BATTLES_BEFORE_HEAL) * c.HEAL_LENGTH

    # return transport_turns + battles_turns + rest_turns

    # эвристически подобранная формула, отражающая «простую логику героя»:
    # - транспорт и безопасноть равны по вкладу в поиск пути
    # - чем больше транстпорт, тем быстрее доберёшься
    # - чем больше безопасность, тем быстрее доберёшься
    # - чем выше оцениваешь сложность боёв, тем сильнее должна влиять безопасность
    return 1 / (transport + safety * expected_battle_complexity)


def travel_cost(cell_1, cell_2, expected_battle_complexity):
    turns = (cell_travel_cost(transport=cell_1.transport,
                              safety=cell_1.safety,
                              expected_battle_complexity=expected_battle_complexity) +
             cell_travel_cost(transport=cell_2.transport,
                              safety=cell_2.safety,
                              expected_battle_complexity=expected_battle_complexity)) / 2
    return turns


class TravelCost:
    __slots__ = ('_cache', '_map', 'expected_battle_complexity', 'worst_cost')

    def __init__(self, map, expected_battle_complexity):
        self._cache = {}
        self._map = map

        self.expected_battle_complexity = expected_battle_complexity

        self.worst_cost = cell_travel_cost(transport=c.CELL_TRANSPORT_MIN,
                                           safety=c.CELL_SAFETY_MIN,
                                           expected_battle_complexity=expected_battle_complexity)

    def get_cost(self, x_1, y_1, x_2, y_2):
        key = (x_1, y_1, x_2, y_2)

        if key not in self._cache:
            self._cache[key] = travel_cost(cell_1=self._map[y_1][x_1],
                                           cell_2=self._map[y_2][x_2],
                                           expected_battle_complexity=self.expected_battle_complexity)

            self._cache[(x_2, y_2, x_1, y_1)] = self._cache[key]

        return self._cache[key]


def find_path_between_places(start_place, finish_place, travel_cost):
    excluded_cells = {(place.x, place.y)
                      for place in places_storage.places.all()
                      if place.id != finish_place.id}

    return find_shortest_path(from_x=start_place.x,
                              from_y=start_place.y,
                              to_x=finish_place.x,
                              to_y=finish_place.y,
                              width=map_conf.settings.WIDTH,
                              height=map_conf.settings.HEIGHT,
                              travel_cost=travel_cost,
                              excluded_cells=excluded_cells)


def find_shortest_path(from_x, from_y, to_x, to_y, width, height, travel_cost, excluded_cells):
    if from_x == to_x and from_y == to_y:
        return [(from_x, from_y)], 0

    path_map = _build_path_map(from_x=from_x,
                               from_y=from_y,
                               to_x=to_x,
                               to_y=to_y,
                               width=width,
                               height=height,
                               travel_cost=travel_cost,
                               excluded_cells=excluded_cells)

    return _restore_path(from_x=from_x,
                         from_y=from_y,
                         to_x=to_x,
                         to_y=to_y,
                         path_map=path_map,
                         width=width,
                         height=height)


def _build_path_map(from_x, from_y, to_x, to_y, width, height, travel_cost, excluded_cells):

    path_map = [[logic.MAX_COST for x in range(width)]
                for y in range(height)]

    heap = [(travel_cost.worst_cost * logic.manhattan_distance(x_1=from_x, y_1=from_y, x_2=to_x, y_2=to_y),
             0,
             from_x,
             from_y)]

    path_map[from_y][from_x] = 0

    while True:

        estimation, cost, x, y = heapq.heappop(heap)

        if to_x == x and to_y == y:
            break

        for next_x, next_y in neighbours_coordinates(x, y, width, height):
            if (next_x, next_y) in excluded_cells:
                continue

            move_cost = travel_cost.get_cost(x, y, next_x, next_y)

            real_cost = cost + move_cost

            if path_map[next_y][next_x] < real_cost:
                continue

            estimated_cost = travel_cost.worst_cost * logic.manhattan_distance(next_x, next_y, to_x, to_y)

            heapq.heappush(heap, (real_cost + estimated_cost,
                                  real_cost,
                                  next_x,
                                  next_y))

            path_map[next_y][next_x] = real_cost

    return path_map


def _restore_path(from_x, from_y, to_x, to_y, path_map, width, height):
    path = [(to_x, to_y)]

    while True:
        x, y = path[-1]

        if from_x == x and from_y == y:
            break

        min_cost = path_map[y][x]
        found_x = -1
        found_y = -1

        for next_x, next_y in neighbours_coordinates(x, y, width, height):
            if min_cost <= path_map[next_y][next_x]:
                continue

            min_cost = path_map[next_y][next_x]
            found_x = next_x
            found_y = next_y

        path.append((found_x, found_y))

    path.reverse()

    return path, path_map[to_y][to_x]
