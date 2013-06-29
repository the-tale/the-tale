# coding: utf-8
import math

from common.utils.prototypes import BasePrototype

from game.map.conf import map_settings
from game.map.places.storage import places_storage

from game.map.roads.models import Road, Waymark
from game.map.roads.exceptions import RoadsException
from game.map.roads.relations import PATH_DIRECTION


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
    def create(cls, point_1, point_2):
        from game.map.roads.storage import roads_storage

        if point_1.id > point_2.id:
            point_1, point_2 = point_2, point_1

        try:
            Road.objects.get(point_1=point_1.id,
                             point_2=point_2.id)
            raise RoadsException('road (%i, %i) has already exist' % (point_1.id, point_2.id) )
        except Road.DoesNotExist:
            pass

        distance = math.sqrt( (point_1.x - point_2.x)**2 + (point_1.y - point_2.y)**2 )

        model = Road.objects.create(point_1=point_1._model,
                                    point_2=point_2._model,
                                    length=distance * map_settings.CELL_LENGTH)

        prototype = cls(model)

        roads_storage.add_item(prototype.id, prototype)
        roads_storage.update_version()

        return prototype


    def update(self):
        distance = math.sqrt( (self.point_1.x - self.point_2.x)**2 + (self.point_1.y - self.point_2.y)**2 )
        self.length = distance * map_settings.CELL_LENGTH

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
        from game.map.roads.storage import roads_storage
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
        from game.map.roads.storage import waymarks_storage

        try:
            Waymark.objects.get(point_from=point_from.id,
                                point_to=point_to.id)
            raise RoadsException('waymark (%i, %i) has already exist' % (point_from.id, point_to.id) )
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
