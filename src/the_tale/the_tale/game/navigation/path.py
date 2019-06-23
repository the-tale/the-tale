
import smart_imports

smart_imports.all()


class Path:
    __slots__ = ('_cells', 'length', '_places_cache', '_start_from', '_start_length')

    def __init__(self, cells):
        self._cells = list(cells)
        self._start_from = cells[0]

        self._start_length = 0

        self._update_length()

        self._places_cache = None

    def clone(self):
        path = self.__class__(cells=list(self._cells))
        path.set_start(*self._start_from)
        return path

    def reverse(self):
        self._cells.reverse()
        self._places_cache = None

    def _update_length(self):
        self.length = self._start_length + len(self._cells) - 1

    def set_start(self, x, y):
        distance = logic.euclidean_distance(x, y, *self._cells[0])

        if len(self._cells) > 1:
            alternative_distance = logic.euclidean_distance(x, y, *self._cells[1])

            if alternative_distance < logic.manhattan_distance(*self._cells[0], *self._cells[1]):
                self._cells.pop(0)
                distance = alternative_distance

        self._start_from = (x, y)
        self._start_length = distance

        self._update_length()

    def append(self, path):
        appended_cells = path._cells

        if self._cells[-1] == appended_cells[0]:
            appended_cells = appended_cells[1:]

        if not appended_cells:
            return

        end_x, end_y = self._cells[-1]
        next_x, next_y = appended_cells[0]

        if logic.manhattan_distance(next_x, next_y, end_x, end_y) != 1:
            raise ValueError('paths {path_1} and {path_2} can not be cancatenated'.format(path_1=self._cells,
                                                                                          path_2=path._cells))

        self._cells.extend(appended_cells)

        self._cells = logic.normalise_path(self._cells)

        self._update_length()

    def next_place_at(self, percents):
        if self._places_cache is None:
            self._places_cache = self._places_positions()

        for place_percent, place_id in self._places_cache:
            if percents < place_percent:
                return place_percent, place_id

        return None, None

    def _places_positions(self):
        map = map_storage.cells.get_map()

        positions = []

        start_percents = self._start_length / self.length if self.length > 0 else 0

        for i, (x, y) in enumerate(self._cells):
            cell = map[y][x]

            if cell.place_id is None:
                continue

            if self.length > 0:
                positions.append((start_percents + i / self.length, cell.place_id))
            else:
                positions.append((start_percents, cell.place_id))

        return positions

    def coordinates(self, percents):
        if self.length == 0:
            return self._cells[0]

        start_percents = self._start_length / self.length

        if percents < start_percents:
            start_x, start_y = self._start_from
            next_x, next_y = self._cells[0]
            return (start_x + (next_x - start_x) * (percents / start_percents),
                    start_y + (next_y - start_y) * (percents / start_percents))

        cells_intervals = len(self._cells) - 1

        if cells_intervals == 0:
            return self._cells[0]

        percents = (percents - start_percents) / (1.0 - start_percents)

        cell_index = int(cells_intervals * percents)

        index_percents = cell_index / cells_intervals

        delta_percents = (percents - index_percents) * cells_intervals

        if cell_index == cells_intervals:
            return self._cells[-1]

        x_1, y_1 = self._cells[cell_index]
        x_2, y_2 = self._cells[cell_index + 1]

        return (x_1 + (x_2 - x_1) * delta_percents,
                y_1 + (y_2 - y_1) * delta_percents)

    def _extract_percents(self, percents):
        if self.length == 0:
            return

        self._places_cache = None

        start_percents = self._start_length / self.length

        if percents < start_percents:
            start_x, start_y = self._start_from
            next_x, next_y = self._cells[0]

            new_start_x = start_x + (next_x - start_x) * percents / start_percents
            new_start_y = start_y + (next_y - start_y) * percents / start_percents

            self.set_start(new_start_x, new_start_y)

            return

        percents = (percents - start_percents) / (1 - start_percents)

        percents_step = 1 / (len(self._cells) - 1)

        base_index = int(percents // percents_step + sys.float_info.epsilon)

        if len(self._cells) - 1 <= base_index:
            self._cells = [self._cells[-1]]
            self.set_start(*self._cells[0])
            return

        new_start_percents = (percents % percents_step) / percents_step

        start_x, start_y = self._cells[base_index]

        self._cells[:base_index + 1] = []

        new_start_x = start_x + (self._cells[0][0] - start_x) * new_start_percents
        new_start_y = start_y + (self._cells[0][1] - start_y) * new_start_percents

        self.set_start(new_start_x, new_start_y)

    def subpath_from_percents(self, percents):
        path = self.clone()
        path._extract_percents(percents)
        return path

    def nearest_coordinates(self, expected_x, expected_y):
        best_distance, best_percents, best_x, best_y = logic.nearest_point_on_section(expected_x, expected_y,
                                                                                      *self._start_from,
                                                                                      *self._cells[0])

        processed_percents = self._start_length / self.length

        percents_delta = 1.0 / self.length

        best_percents *= processed_percents

        for i in range(len(self._cells) - 1):
            distance, percents, x, y = logic.nearest_point_on_section(expected_x, expected_y,
                                                                      *self._cells[i],
                                                                      *self._cells[i+1])

            if distance <= best_distance + sys.float_info.epsilon:
                best_distance = distance
                best_percents = processed_percents + percents * percents_delta
                best_x = x
                best_y = y

            processed_percents += percents_delta

        return best_percents, best_x, best_y

    def destination_coordinates(self):
        return self._cells[-1]

    def serialize(self):
        return {'cells': self._cells,
                'start_from': self._start_from}

    @classmethod
    def deserialize(cls, data):
        path = cls(cells=data['cells'])
        path.set_start(*data['start_from'])
        return path

    def ui_info(self):
        return {'cells': self._cells}

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                all(getattr(self, name) == getattr(other, name) for name in self.__slots__ if name != '_places_cache'))

    def __ne__(self, other):
        return not self.__eq__(other)


def simple_path(from_x, from_y, to_x, to_y):

    cells = [(from_x, from_y)]

    delta = logic.manhattan_distance(to_x, to_y, from_x, from_y)

    if delta == 0:
        return Path(cells=cells)

    dx = abs(to_x - from_x) / delta
    dy = abs(to_y - from_y) / delta

    delta_x = dx
    delta_y = dy

    if from_x < to_x:
        move_x = 1
    elif to_x < from_x:
        move_x = -1
    else:
        move_x = 0

    if from_y < to_y:
        move_y = 1
    elif to_y < from_y:
        move_y = -1
    else:
        move_y = 0

    while cells[-1] != (to_x, to_y):

        if delta_x < delta_y:
            delta_x += dx
            cells.append((cells[-1][0], cells[-1][1] + move_y))
            continue

        delta_y += dy
        cells.append((cells[-1][0] + move_x, cells[-1][1]))

    return Path(cells=cells)
