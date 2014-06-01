# coding: utf-8
import math

from the_tale.common.utils.prototypes import BasePrototype

from the_tale.game.balance import constants as c

from the_tale.game.map.conf import map_settings
from the_tale.game.map.places.storage import places_storage

from the_tale.game.map.roads.models import Road, Waymark
from the_tale.game.map.roads import exceptions
from the_tale.game.map.roads.relations import PATH_DIRECTION


class RoadPrototype(BasePrototype):
    _model_class = Road
    _readonly = ('id', 'path', 'point_1_id', 'point_2_id')
    _bidirectional = ('length', 'exists')
    _get_by = ('id',)

    @property
    def point_1(self): return places_storage[self._model.point_1_id]

    @property
    def point_2(self): return places_storage[self._model.point_2_id]

    ###########################################
    # Object operations
    ###########################################

    def remove(self): self._model.delete()
    def save(self): self._model.save(force_update=True)

    @classmethod
    def _distance_in_cells(cls, point_1, point_2):
        return abs(point_1.x - point_2.x) + abs(point_1.y - point_2.y)

    @classmethod
    def create(cls, point_1, point_2):
        from the_tale.game.map.roads.storage import roads_storage

        if point_1.id > point_2.id:
            point_1, point_2 = point_2, point_1

        try:
            Road.objects.get(point_1=point_1.id,
                             point_2=point_2.id)
            raise exceptions.RoadsAlreadyExistsError(start=point_1.id, stop=point_2.id)
        except Road.DoesNotExist:
            pass

        distance = cls._distance_in_cells(point_1, point_2)

        model = Road.objects.create(point_1=point_1._model,
                                    point_2=point_2._model,
                                    length=distance * c.MAP_CELL_LENGTH)

        prototype = cls(model)

        roads_storage.add_item(prototype.id, prototype)
        roads_storage.update_version()

        return prototype


    def update(self):
        # since road paved only vertically and horizontally
        distance = self._distance_in_cells(self.point_1, self.point_2)
        self.length = distance * c.MAP_CELL_LENGTH

        if self.point_1.id > self.point_2.id:
            self._model.point_1, self._model.point_2 = self._model.point_2, self._model.point_1

        self.roll()

    def roll(self):
        self._model.path = self._roll(self.point_1.x, self.point_1.y, self.point_2.x, self.point_2.y)

    @classmethod
    def _roll(cls, start_x, start_y, finish_x, finish_y):

        path = []

        x = start_x
        y = start_y

        if math.fabs(finish_x - start_x) >  math.fabs(finish_y - start_y):
            dx = math.copysign(1.0, finish_x - start_x)
            dy = dx * float(finish_y - start_y) / (finish_x - start_x)
        else:
            dy = math.copysign(1.0, finish_y - start_y)
            dx = dy * float(finish_x - start_x) / (finish_y - start_y)

        real_x = float(x)
        real_y = float(y)

        while x != finish_x or y != finish_y:

            real_x += dx
            real_y += dy

            if int(round(real_x)) == x + 1: path.append(PATH_DIRECTION.RIGHT.value)
            elif int(round(real_x)) == x - 1: path.append(PATH_DIRECTION.LEFT.value)

            if int(round(real_y)) == y + 1: path.append(PATH_DIRECTION.DOWN.value)
            elif int(round(real_y)) == y - 1: path.append(PATH_DIRECTION.UP.value)

            x = int(round(real_x))
            y = int(round(real_y))

        return ''.join(path)

    def map_info(self):
        return {'id': self.id,
                'point_1_id': self.point_1.id,
                'point_2_id': self.point_2.id,
                'path': self.path,
                'length': self.length,
                'exists': self.exists}



class WaymarkPrototype(BasePrototype):
    _model_class = Waymark
    _readonly = ('id', 'point_from_id', 'point_to_id', 'road_id')
    _bidirectional = ('length',)
    _get_by = ('id',)

    @property
    def point_from(self): return places_storage[self._model.point_from_id]

    @property
    def point_to(self): return places_storage[self._model.point_to_id]

    def get_road(self):
        if self._model.road_id is None:
            return None
        from the_tale.game.map.roads.storage import roads_storage
        return roads_storage[self._model.road_id]

    def set_road(self, value):
        if value is None:
            self._model.road = None
            return
        self._model.road = value._model
    road = property(get_road, set_road)

    ###########################################
    # Object operations
    ###########################################

    def remove(self): self._model.delete()
    def save(self): self._model.save()

    @classmethod
    def create(cls, point_from, point_to, road, length):
        from the_tale.game.map.roads.storage import waymarks_storage

        try:
            Waymark.objects.get(point_from=point_from.id,
                                point_to=point_to.id)
            raise exceptions.WaymarkAlreadyExistsError(start=point_from.id, stop=point_to.id)
        except Waymark.DoesNotExist:
            pass

        model = Waymark.objects.create(point_from=point_from._model,
                                       point_to=point_to._model,
                                       road=road._model if road else None,
                                       length=length)

        prototype = cls(model)

        waymarks_storage.add_item(prototype.id, prototype)
        waymarks_storage.update_version()

        return prototype
