# -*- coding: utf-8 -*-
import math

from .. import settings as map_settings

from .models import Road

def get_road_by_id(model_id):
    model = Road.objects.get(id=model_id)
    return get_road_by_model(model)

def get_road_by_model(model):
    return RoadPrototype(model=model)

def get_road_between(place_1, place_2):
    if place_1.id > place_2.id:
        place_1, place_2 = place_2, place_1

    road = Road.objects.get(point_1=place_1.model, point_2=place_2.model)
    return get_road_by_model(model=road)

def get_place_prototype(place_model):
    from ..places.prototypes import PlacePrototype
    return PlacePrototype(model=place_model)

class RoadsException(Exception): pass

class RoadPrototype(object):

    def __init__(self, model, *argv, **kwargs):
        super(RoadPrototype, self).__init__(*argv, **kwargs)
        self.model = model

    @property
    def id(self): return self.model.id

    @property
    def point_1_id(self): return self.model.point_1_id

    @property
    def point_1(self): 
        if not hasattr(self, '_point_1'):
            self._point_1 = get_place_prototype(self.model.point_1)
        return self._point_1

    @property
    def point_2_id(self): return self.model.point_2_id

    @property
    def point_2(self): 
        if not hasattr(self, '_point_2'):
            self._point_2 = get_place_prototype(self.model.point_2)
        return self._point_2

    def get_length(self): return self.model.length
    def set_length(self, value): self.model.length = value
    length = property(get_length, set_length)

    ###########################################
    # Object operations
    ###########################################

    def remove(self): self.model.delete()
    def save(self): self.model.save()

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
        self.save()

