# -*- coding: utf-8 -*-
import random

from django_next.utils import s11n

from .models import Place, PLACE_TYPE, RACE_TO_TERRAIN
from . import settings as places_settings

def get_place_by_id(model_id):
    model = Place.objects.get(id=model_id)
    return get_place_by_model(model)

def get_place_by_model(model):
    return PlacePrototype(model=model)

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

    def get_terrain(self): return self.model.terrain
    def set_terrain(self, value): self.model.terrain = value
    terrain = property(get_terrain, set_terrain)

    @property
    def name(self): return self.model.name

    @property
    def type(self): return self.model.type

    @property
    def subtype(self): return self.model.subtype

    def get_size(self): return self.model.size
    def set_size(self, value): self.model.size = value
    size = property(get_size, set_size)

    @property
    def persons(self):
        from ...persons.prototypes import get_person_by_model
        from ...persons.models import PERSON_STATE

        if not hasattr(self, '_persons'):
            self._persons = []
            for person_model in self.model.persons.filter(state=PERSON_STATE.IN_GAME).order_by('power'):
                person = get_person_by_model(person_model)
                self._persons.append(person)

        return self._persons

    @property
    def total_persons_power(self): return sum([person.power for person in self.persons])

    def sync_persons(self):
        persons_count = len(self.persons)

        from ...persons.prototypes import PersonPrototype
        from ...persons.models import PERSON_TYPE_CHOICES
        from ...game_info import RACE_CHOICES

        expected_persons_number = places_settings.SIZE_TO_PERSONS_NUMBER[self.size]

        while persons_count < expected_persons_number:
            PersonPrototype.create(place=self, 
                                   race=random.choice(RACE_CHOICES)[0],
                                   tp=random.choice(PERSON_TYPE_CHOICES)[0],
                                   name='person_%s' % random.choice('QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm'))
            persons_count += 1

        while persons_count > expected_persons_number:
            person = self.persons[persons_count-1]
            person.move_out_game()
            person.save()
            persons_count -= 1

        if hasattr(self, '_persons'):
            delattr(self, '_persons')

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = s11n.from_json(self.model.data)
        return self._data

    @property
    def power_points(self): 
        if 'power_points' not in self.data:
            self.data['power_points'] = []
        return self.data['power_points']
    
    @property
    def power(self): 
        if self.power_points:
            return max(sum(self.power_points), 0)
        return 0

    def push_power(self, value): 
        self.power_points.append(value)

        while len(self.power_points) > places_settings.POWER_HISTORY_LENGTH:
            self.power_points.pop(0)

    def sync_power(self, powers):
        power = 0
        for person in self.persons:
            power += powers.get(person.id, 0)
        self.push_power(power)

    def sync_size(self, max_power):
        self.size = int(places_settings.MAX_SIZE * (float(self.power) / (max_power+1)) ) + 1

    def sync_terrain(self):
        race_power = {}
        
        for person in self.persons:
            race_power[person.race] = race_power.get(person.race, 0) + person.power

        dominant_race = max(race_power.items(), key=lambda x: x[1])[0]

        self.terrain = RACE_TO_TERRAIN[dominant_race]

    def __unicode__(self):
        return self.model.__unicode__()

    def __repr__(self):
        return self.model.__repr__()

    ###########################################
    # Checks
    ###########################################

    @property
    def is_settlement(self): return self.type in [PLACE_TYPE.CITY]

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def random_place(cls):
        model = Place.objects.all().order_by('?')[0]
        return cls(model=model)

    def remove(self): self.model.delete()
    def save(self): 
        self.model.data = s11n.to_json(self.data)
        self.model.save(force_update=True)

    def map_info(self):
        return {'id': self.id,
                'pos': {'x': self.x, 'y': self.y},
                'name': self.name,
                'type': self.type,
                'subtype': self.subtype,
                'size': self.size}
