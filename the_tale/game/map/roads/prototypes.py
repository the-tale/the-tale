# -*- coding: utf-8 -*-
import math

from game.map.conf import map_settings
from game.map.places.storage import places_storage

from game.map.roads.models import Road, Waymark
from game.map.roads.exceptions import RoadsException


class RoadPrototype(object):

    def __init__(self, model):
        self.model = model

    @classmethod
    def get_by_id(cls, id_):
        try:
            return cls(Road.objects.get(id=id_))
        except Road.DoesNotExist:
            return None

    @property
    def id(self): return self.model.id

    @property
    def point_1_id(self): return self.model.point_1_id

    @property
    def point_1(self): return places_storage[self.model.point_1_id]

    @property
    def point_2_id(self): return self.model.point_2_id

    @property
    def point_2(self): return places_storage[self.model.point_2_id]

    def get_length(self): return self.model.length
    def set_length(self, value): self.model.length = value
    length = property(get_length, set_length)

    def __unicode__(self):
        return self.model.__unicode__()

    def __repr__(self):
        return self.model.__repr__()

    ###########################################
    # Object operations
    ###########################################

    def remove(self): self.model.delete()
    def save(self): self.model.save(force_update=True)

    def map_info(self):
        return {'id': self.id,
                'point_1': self.point_1.map_info(),
                'point_2': self.point_2.map_info(),
                'length': self.length}

    @classmethod
    def create(cls, point_1, point_2):

        if point_1.id > point_2.id:
            point_1, point_2 = point_2, point_1

        try:
            Road.objects.get(point_1=point_1.model,
                             point_2=point_2.model)
            raise RoadsException('road (%i, %i) has already exist' % (point_1.id, point_2.id) )
        except Road.DoesNotExist:
            pass

        distance = math.sqrt( (point_1.x - point_2.x)**2 + (point_1.y - point_2.y)**2 )

        model = Road.objects.create(point_1=point_1.model,
                                    point_2=point_2.model,
                                    length=distance * map_settings.CELL_LENGTH)

        return cls(model)


    def update(self):
        distance = math.sqrt( (self.point_1.x - self.point_2.x)**2 + (self.point_1.y - self.point_2.y)**2 )
        self.length = distance * map_settings.CELL_LENGTH

        if self.point_1.id > self.point_2.id:
            self.model.point_1, self.model.point_2 = self.model.point_2, self.model.point_1

        self.save()


class WaymarkPrototype(object):

    def __init__(self, model):
        self.model = model

    @property
    def id(self): return self.model.id

    @property
    def point_from_id(self): return self.model.point_from_id

    @property
    def point_from(self): return places_storage[self.model.point_from_id]

    @property
    def point_to_id(self): return self.model.point_to_id

    @property
    def point_to(self): return places_storage[self.model.point_to_id]

    @property
    def road_id(self): return self.model.road_id

    @property
    def road(self):
        if self.model.road_id is None:
            return None
        from game.map.roads.storage import roads_storage
        return roads_storage[self.model.road_id]

    @property
    def length(self): return self.model.length

    ###########################################
    # Object operations
    ###########################################

    def remove(self): self.model.delete()
    def save(self): self.model.save()

    @classmethod
    def create(cls, point_from, point_to, road, length):

        try:
            Waymark.objects.get(point_from=point_from.model,
                                point_to=point_to.model)
            raise RoadsException('waymark (%i, %i) has already exist' % (point_from.id, point_to.id) )
        except Waymark.DoesNotExist:
            pass

        model = Waymark.objects.create(point_from=point_from.model,
                                       point_to=point_to.model,
                                       road=road.model if road else None,
                                       length=length)

        return cls(model)
