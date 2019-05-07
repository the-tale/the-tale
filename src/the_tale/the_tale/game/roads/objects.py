
import smart_imports

smart_imports.all()


class Road:
    __slots__ = ('id', 'place_1_id', 'place_2_id', 'length', 'path')

    def __init__(self, id, place_1_id, place_2_id, length, path):
        self.id = id
        self.place_1_id = place_1_id
        self.place_2_id = place_2_id
        self.length = length
        self.path = path

    @property
    def place_1(self):
        return places_storage.places[self.place_1_id]

    @property
    def place_2(self):
        return places_storage.places[self.place_2_id]

    def get_cells(self):
        return logic.get_path_cells(start_x=self.place_1.x,
                                    start_y=self.place_1.y,
                                    path=self.path)

    def get_stabilization_price_for(self, place):

        if place.id not in (self.place_1_id, self.place_2_id):
            raise ValueError

        place_1_point = (self.place_1.x, self.place_1.y)
        place_2_point = (self.place_2.x, self.place_2.y)

        cells = [cell for cell in self.get_cells()
                 if cell not in (place_1_point, place_2_point) and
                 map_storage.cells(*cell).dominant_place_id == place.id]

        return logic.road_support_cost(cells)

    def map_info(self):
        return {'id': self.id,
                'point_1_id': self.place_1_id,
                'point_2_id': self.place_2_id,
                'path': self.path,
                'length': self.length}
