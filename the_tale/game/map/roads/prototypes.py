# -*- coding: utf-8 -*-
import math

from ..conf import map_settings

from .models import Road, Waymark

def get_road_by_id(model_id):
    model = Road.objects.get(id=model_id)
    return get_road_by_model(model)

def get_road_by_model(model):
    if model is None:
        return None
    return RoadPrototype(model=model)

def get_waymark_by_id(model_id):
    model = Waymark.objects.get(id=model_id)
    return get_waymark_by_model(model)

def get_waymark_by_model(model):
    return WaymarkPrototype(model=model)

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

    def __init__(self, model, *argv, **kwargs):
        super(WaymarkPrototype, self).__init__(*argv, **kwargs)
        self.model = model

    @property
    def id(self): return self.model.id

    @property
    def point_from_id(self): return self.model.point_from_id

    @property
    def point_from(self): 
        if not hasattr(self, '_point_from'):
            self._point_from = get_place_prototype(self.model.point_from)
        return self._point_1

    @property
    def point_to_id(self): return self.model.point_to_id

    @property
    def point_to(self): 
        if not hasattr(self, '_point_to'):
            self._point_to = get_place_prototype(self.model.point_to)
        return self._point_to

    @property
    def road_id(self): return self.model.road_id

    @property
    def road(self): 
        if not hasattr(self, '_road'):
            self._road = get_road_by_model(self.model.road)
        return self._road

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


    @classmethod
    def look_for_road(cls, point_from, point_to):
        if not isinstance(point_from, int):
            point_from = point_from.id
        if not isinstance(point_to, int):
            point_to = point_to.id

        waymark = cls(Waymark.objects.get(point_from=point_from, point_to=point_to))
        return waymark.road, waymark.length
    
            

