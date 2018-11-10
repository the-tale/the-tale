
import smart_imports

smart_imports.all()


def old_round(value):
    floor = math.floor(value)
    if value - floor >= 0.5:
        floor += 1
    return floor


class RoadPrototype(utils_prototypes.BasePrototype):
    _model_class = models.Road
    _readonly = ('id', 'path', 'point_1_id', 'point_2_id')
    _bidirectional = ('length', 'exists')
    _get_by = ('id',)

    @property
    def point_1(self): return places_storage.places[self._model.point_1_id]

    @property
    def point_2(self): return places_storage.places[self._model.point_2_id]

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
        if point_1.id > point_2.id:
            point_1, point_2 = point_2, point_1

        try:
            models.Road.objects.get(point_1=point_1.id,
                                    point_2=point_2.id)
            raise exceptions.RoadsAlreadyExistsError(start=point_1.id, stop=point_2.id)
        except models.Road.DoesNotExist:
            pass

        distance = cls._distance_in_cells(point_1, point_2)

        model = models.Road.objects.create(point_1_id=point_1.id,
                                           point_2_id=point_2.id,
                                           length=distance * c.MAP_CELL_LENGTH)

        prototype = cls(model)

        storage.roads.add_item(prototype.id, prototype)
        storage.roads.update_version()

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

        if math.fabs(finish_x - start_x) > math.fabs(finish_y - start_y):
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

            if int(old_round(real_x)) == x + 1:
                path.append(relations.PATH_DIRECTION.RIGHT.value)
            elif int(old_round(real_x)) == x - 1:
                path.append(relations.PATH_DIRECTION.LEFT.value)

            if int(old_round(real_y)) == y + 1:
                path.append(relations.PATH_DIRECTION.DOWN.value)
            elif int(old_round(real_y)) == y - 1:
                path.append(relations.PATH_DIRECTION.UP.value)

            x = int(old_round(real_x))
            y = int(old_round(real_y))

        return ''.join(path)

    def map_info(self):
        return {'id': self.id,
                'point_1_id': self.point_1.id,
                'point_2_id': self.point_2.id,
                'path': self.path,
                'length': self.length,
                'exists': self.exists}


class WaymarkPrototype(utils_prototypes.BasePrototype):
    _model_class = models.Waymark
    _readonly = ('id', 'point_from_id', 'point_to_id', 'road_id')
    _bidirectional = ('length',)
    _get_by = ('id',)

    @property
    def point_from(self): return places_storage.places[self._model.point_from_id]

    @property
    def point_to(self): return places_storage.places[self._model.point_to_id]

    def get_road(self):
        if self._model.road_id is None:
            return None
        return storage.roads[self._model.road_id]

    def set_road(self, value):
        if value is None:
            self._model.road = None
            return
        self._model.road = value._model
    road = property(get_road, set_road)

    ###########################################
    # Object operations
    ###########################################

    def remove(self):
        self._model.delete()

    def save(self):
        self._model.save()

    @classmethod
    def create(cls, point_from, point_to, road, length):

        try:
            models.Waymark.objects.get(point_from=point_from.id,
                                       point_to=point_to.id)
            raise exceptions.WaymarkAlreadyExistsError(start=point_from.id, stop=point_to.id)
        except models.Waymark.DoesNotExist:
            pass

        model = models.Waymark.objects.create(point_from_id=point_from.id,
                                              point_to_id=point_to.id,
                                              road=road._model if road else None,
                                              length=length)

        prototype = cls(model)

        storage.waymarks.add_item(prototype.id, prototype)
        storage.waymarks.update_version()

        return prototype
