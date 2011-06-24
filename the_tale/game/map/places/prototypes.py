# -*- coding: utf-8 -*-

from .models import Place, HeroPosition
from ..roads.prototypes import RoadPrototype

def get_place_by_id(model_id):
    model = Place.objects.get(id=model_id)
    return get_place_by_model(model)

def get_place_by_model(model):
    return PlacePrototype(model=model)

def get_hero_position_by_id(model_id):
    model = HeroPosition.objects.get(id=model_id)
    return get_hero_position_by_model(model)

def get_hero_position_by_model(model):
    return HeroPositionPrototype(model=model)


class PlacePrototype(object):

    TYPE = 'BASE'

    def __init__(self, model, *argv, **kwargs):
        super(PlacePrototype, self).__init__(*argv, **kwargs)
        self.model = model

    @property
    def id(self): return self.model.id

    @property
    def x(self): return self.model.x

    @property
    def y(self): return self.model.y

    @property
    def name(self): return self.model.name

    @property
    def type(self): return self.model.type

    @property
    def subtype(self): return self.model.subtype

    @property
    def size(self): return self.model.size

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def random_place(cls):
        model = Place.objects.all().order_by('?')[0]
        return cls(model=model)

    def remove(self): self.model.delete()
    def save(self): self.model.save()

    def map_info(self):
        return {'id': self.id,
                'pos': {'x': self.x, 'y': self.y},
                'name': self.name,
                'type': self.type,
                'subtype': self.subtype,
                'size': self.size}


class HeroPositionPrototype(object):

    def __init__(self, model, *argv, **kwargs):
        super(HeroPositionPrototype, self).__init__(*argv, **kwargs)
        self.model = model

    @property
    def id(self): return self.model.id

    @property
    def place_id(self): return self.model.place_id

    @property
    def place(self): 
        if not hasattr(self, '_place'):
            self._place = PlacePrototype(model=self.model.place) if self.model.place else None
        return self._place

    def set_place(self, place):
        if hasattr(self, '_place'):
            delattr(self, '_place')
        self.model.place = place.model
        self.model.road = None
        self.model.invert_direction = None
        self.percents = None

    @property
    def road(self): 
        if not hasattr(self, '_road'):
            self._road = RoadPrototype(model=self.model.road) if self.model.road else None
        return self._road

    def set_road(self, road, percents=0, invert=False):
        if hasattr(self, '_road'):
            delattr(self, '_road')
        self.model.place = None
        self.model.road = road.model
        self.model.invert_direction = invert
        self.percents = percents

    def get_percents(self): return self.model.percents
    def set_percents(self, value): self.model.percents = value
    percents = property(get_percents, set_percents)

    def get_invert_direction(self): return self.model.invert_direction
    def set_invert_direction(self, value): self.model.invert_direction = value
    invert_direction = property(get_invert_direction, set_invert_direction)

    @property
    def hero_id(self): return self.model.hero_id

    @property
    def hero(self): 
        from game.heroes.prototypes import HeroPrototype
        return HeroPrototype(model=self.model.hero)


    ###########################################
    # Object operations
    ###########################################

    def remove(self): self.model.delete()
    def save(self): self.model.save()

    @classmethod
    def create(cls, hero, place):
        position = HeroPosition.objects.create(hero=hero.model,
                                               place=place.model)
        return cls(position)


    def ui_info(self):
        return {'id': self.id,
                'place': self.place.map_info() if self.place else None,
                'road': self.road.map_info() if self.road else None,
                'invert_direction': self.invert_direction,
                'percents': self.percents}
