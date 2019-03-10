
import smart_imports

smart_imports.all()


class Position(object):
    __slots__ = ('last_place_visited_turn',
                 'moved_out_place',
                 'place_id',
                 'previous_place_id',
                 'x',
                 'y',
                 'cell_x',
                 'cell_y',
                 'dx',
                 'dy')

    def __init__(self,
                 last_place_visited_turn=None,
                 moved_out_place=False,
                 place_id=None,
                 previous_place_id=None,
                 x=0,
                 y=0,
                 cell_x=None,
                 cell_y=None,
                 dx=0,
                 dy=0):
        self.last_place_visited_turn = last_place_visited_turn
        self.moved_out_place = moved_out_place
        self.place_id = place_id
        self.previous_place_id = previous_place_id

        self.x = x
        self.y = y
        self.cell_x = cell_x
        self.cell_y = cell_y
        self.dx = dx
        self.dy = dy

    @classmethod
    def create(cls, place):
        position = cls()

        position.set_place(place)
        position.move_in_place()

        position.dx = 0
        position.dy = 0

        return position

    def move_out_place(self):
        self.moved_out_place = True

    def move_in_place(self):
        self.moved_out_place = False
        self.last_place_visited_turn = game_turn.number()

    def get_description(self):
        from . import storage

        if self.place:
            return storage.position_descriptions.text_in_place(self.place_id)

        cell = self.cell()

        if cell.roads_ids:
            road = roads_storage.roads[random.choice(cell.roads_ids)]

            place_from_id, place_to_id = road.place_1_id, road.place_2_id

            return storage.position_descriptions.text_on_road(place_from_id, place_to_id)

        if cell.dominant_place_id is not None:
            return storage.position_descriptions.text_near_place(cell.dominant_place_id)

        return storage.position_descriptions.text_in_wild_lands()

    @property
    def place(self):
        from the_tale.game.places import storage as places_storage

        return places_storage.places.get(self.place_id)

    @property
    def previous_place(self):
        from the_tale.game.places import storage as places_storage
        return places_storage.places.get(self.previous_place_id)

    def update_previous_place(self):
        self.previous_place_id = self.place_id

    def set_place(self, place):
        self.set_position(place.x, place.y)

        self.place_id = place.id

    def set_position(self, x, y):
        self.dx = self.x - x
        self.dy = self.y - y

        self.x = x
        self.y = y

        self.cell_x = int(round(self.x))
        self.cell_y = int(round(self.y))

        self.update_previous_place()

        self.place_id = None

    def cell(self):
        from the_tale.game.map import storage as map_storage
        return map_storage.cells(self.cell_x, self.cell_y)

    def is_near_cell_center(self, delta):
        if delta < abs(self.cell_x - self.x):
            return False

        if delta < abs(self.cell_y - self.y):
            return False

        return True

    def can_visit_current_place(self, delta):
        if not self.is_near_cell_center(delta=delta):
            return False

        return self.cell().place_id is not None

    def should_visit_current_place(self, delta):
        return (self.can_visit_current_place(delta=delta) and
                self.previous_place_id != self.cell().place_id)

    ###########################################
    # Object operations
    ###########################################

    def ui_info(self):
        return {'x': self.x,
                'y': self.y,
                'dx': self.dx,
                'dy': self.dy}

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                all(getattr(self, name) == getattr(other, name) for name in self.__slots__))

    def serialize(self):
        return {'last_place_visited_turn': self.last_place_visited_turn,
                'moved_out_place': self.moved_out_place,
                'place_id': self.place_id,
                'previous_place_id': self.previous_place_id,
                'x': self.x,
                'y': self.y,
                'cell_x': self.cell_x,
                'cell_y': self.cell_y,
                'dx': self.dx,
                'dy': self.dy}

    @classmethod
    def deserialize(cls, data):
        return cls(**data)
