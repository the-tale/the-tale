# coding: utf-8
import math

from the_tale.game.balance import constants as c

from the_tale.game.map.places.storage import places_storage
from the_tale.game.map.roads.storage import roads_storage

from the_tale.game.map.storage import map_info_storage

from the_tale.game.prototypes import TimePrototype

from . import storage


class Position(object):
    __slots__ = ('last_place_visited_turn',
                 'moved_out_place',
                 'place_id',
                 'road_id',
                 'previous_place_id',
                 'invert_direction',
                 'percents',
                 'from_x',
                 'from_y',
                 'to_x',
                 'to_y')

    def __init__(self,
                 last_place_visited_turn,
                 moved_out_place,
                 place_id,
                 road_id,
                 previous_place_id,
                 invert_direction,
                 percents,
                 from_x,
                 from_y,
                 to_x,
                 to_y):
        self.last_place_visited_turn = last_place_visited_turn
        self.moved_out_place = moved_out_place
        self.place_id = place_id
        self.road_id = road_id
        self.previous_place_id = previous_place_id

        self.invert_direction = invert_direction
        self.percents = percents
        self.from_x = from_x
        self.from_y = from_y
        self.to_x = to_x
        self.to_y = to_y

    @classmethod
    def create(cls, place_id, road_id):
        return cls(last_place_visited_turn=TimePrototype.get_current_turn_number(),
                   moved_out_place=False,
                   place_id=place_id,
                   road_id=road_id,
                   previous_place_id=None,
                   invert_direction=False,
                   percents=0,
                   from_x=None,
                   from_y=None,
                   to_x=None,
                   to_y=None)

    def move_out_place(self):
        self.moved_out_place = True

    def move_in_place(self):
        self.moved_out_place = False
        self.last_place_visited_turn = TimePrototype.get_current_turn_number()

    def get_description(self):
        if self.place:
            return storage.position_descriptions.text_in_place(self.place_id)

        if self.road:
            place_from_id, place_to_id = self.road.point_1_id, self.road.point_2_id
            if self.invert_direction:
                place_from_id, place_to_id = place_to_id, place_from_id
            return storage.position_descriptions.text_on_road(place_from_id, place_to_id)

        dominant_place = self.get_dominant_place()

        if dominant_place:
            return storage.position_descriptions.text_near_place(dominant_place.id)

        return storage.position_descriptions.text_in_wild_lands()


    @property
    def place(self): return places_storage.get(self.place_id)

    @property
    def previous_place(self): return places_storage.get(self.previous_place_id)

    def update_previous_place(self):
        self.previous_place_id = self.place_id

    def _reset_position(self):
        self.place_id = None
        self.road_id = None
        self.invert_direction = None
        self.percents = None
        self.from_x = None
        self.from_y = None
        self.to_x = None
        self.to_y = None

    def set_place(self, place):
        self._reset_position()
        self.place_id = place.id

    @property
    def road(self): return roads_storage.get(self.road_id)

    def set_road(self, road, percents=0, invert=False):
        self._reset_position()

        self.road_id = road.id
        self.invert_direction = invert
        self.percents = percents

        self.update_previous_place()

    @property
    def coordinates_from(self): return self.from_x, self.from_y

    @property
    def coordinates_to(self): return self.to_x, self.to_y

    def subroad_len(self): return math.sqrt( (self.from_x-self.to_x)**2 + (self.from_y-self.to_y)**2)

    def set_coordinates(self, from_x, from_y, to_x, to_y, percents):
        self._reset_position()

        self.from_x = from_x
        self.from_y = from_y
        self.to_x = to_x
        self.to_y = to_y
        self.percents = percents

        self.update_previous_place()

    @property
    def is_walking(self):
        return (self.from_x is not None and
                self.from_y is not None and
                self.to_x is not None and
                self.to_y is not None)

    @property
    def cell_coordinates(self):
        if self.place:
            return self.get_cell_coordinates_in_place()
        elif self.road:
            return self.get_cell_coordinates_on_road()
        else:
            return self.get_cell_coordinates_near_place()

    def get_cell_coordinates_in_place(self):
        return self.place.x, self.place.y

    def get_cell_coordinates_on_road(self):
        point_1 = self.road.point_1
        point_2 = self.road.point_2

        percents = self.percents

        if self.invert_direction:
            percents = 1 - percents

        x = point_1.x + (point_2.x - point_1.x) * percents
        y = point_1.y + (point_2.y - point_1.y) * percents

        return int(x), int(y)

    def get_cell_coordinates_near_place(self):
        from_x, from_y = self.coordinates_from
        to_x, to_y = self.coordinates_to
        percents = self.percents

        x = from_x + (to_x - from_x) * percents
        y = from_y + (to_y - from_y) * percents

        return int(x), int(y)

    def get_terrain(self):
        map_info = map_info_storage.item
        x, y = self.cell_coordinates
        return map_info.terrain[y][x]

    def get_dominant_place(self):
        if self.place:
            return self.place
        else:
            return map_info_storage.item.get_dominant_place(*self.cell_coordinates)

    def get_nearest_place(self):
        x, y = self.cell_coordinates
        best_distance = 999999999999999
        best_place = None
        for place in places_storage.all():
            distance = math.hypot(place.x-x, place.y-y)
            if distance < best_distance:
                best_distance = distance
                best_place = place

        return best_place

    def get_nearest_dominant_place(self):
        place = self.get_dominant_place()
        if place is None:
            place = self.get_nearest_place()
        return place

    @classmethod
    def raw_transport(cls):
        from the_tale.game.map.places import conf
        return 1.0 - c.WHILD_TRANSPORT_PENALTY - c.TRANSPORT_FROM_PLACE_SIZE_PENALTY * conf.places_settings.MAX_SIZE

    def get_minumum_distance_to(self, destination):
        from the_tale.game.map.roads.storage import waymarks_storage

        if self.place:
            return waymarks_storage.look_for_road(self.place, destination).length

        if self.is_walking:
            x = self.coordinates_from[0] + (self.coordinates_to[0] - self.coordinates_from[0]) * self.percents
            y = self.coordinates_from[1] + (self.coordinates_to[1] - self.coordinates_from[1]) * self.percents
            nearest_place = self.get_nearest_place()
            return math.hypot(x-nearest_place.x, y-nearest_place.y) + waymarks_storage.look_for_road(nearest_place, destination).length

        # if on road
        place_from = self.road.point_1
        place_to = self.road.point_2

        if self.invert_direction:
            place_from, place_to = place_to, place_from

        delta_from = self.road.length * self.percents
        delta_to = self.road.length * (1-self.percents)

        return min(waymarks_storage.look_for_road(place_from, destination).length + delta_from,
                   waymarks_storage.look_for_road(place_to, destination).length + delta_to)


    def get_position_on_map(self):

        if self.place:
            return (self.place.x, self.place.y, 0, 0)

        if self.road:
            percents = self.percents
            path = self.road.path

            x = self.road.point_1.x
            y = self.road.point_1.y

            dx = self.road.point_1.x - self.road.point_2.x
            dy = self.road.point_1.y - self.road.point_2.y

            if self.invert_direction:
                percents = 1 - percents
                dx = -dx
                dy = -dy

            length = percents * len(path)
            index = 0
            character = None

            for c in path:
                character = c

                index += 1

                if index > length:
                    break

                if c == 'l': x -= 1
                elif c == 'r': x += 1
                elif c == 'u': y -= 1
                elif c == 'd': y += 1

            else:
                index += 1

            delta = length - (index-1)

            if character == 'l': x -= delta
            elif character == 'r': x += delta
            elif character == 'u': y -= delta
            elif character == 'd': y += delta

            return (x, y, dx, dy)

        if self.is_walking:

            to_x = self.coordinates_to[0]
            to_y = self.coordinates_to[1]
            from_x = self.coordinates_from[0]
            from_y = self.coordinates_from[1]

            x = from_x + (to_x - from_x) * self.percents
            y = from_y + (to_y - from_y) * self.percents

            return (x, y, from_x - to_x, from_y - to_y)



    ###########################################
    # Object operations
    ###########################################

    def ui_info(self):
        x, y, dx, dy = self.get_position_on_map()
        return { 'x': x,
                 'y': y,
                 'dx': dx,
                 'dy': dy}

    def __eq__(self, other):
        return ( self.place_id == other.place_id and
                 self.road_id == other.road_id and
                 self.percents == other.percents and
                 self.invert_direction == other.invert_direction and
                 self.coordinates_from == other.coordinates_from and
                 self.coordinates_to == other.coordinates_to)
