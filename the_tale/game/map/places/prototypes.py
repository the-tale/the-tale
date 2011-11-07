# -*- coding: utf-8 -*-
import random
from .models import Place, PLACE_TYPE

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

    @property
    def terrain(self): return self.model.terrain

    @property
    def name(self): return self.model.name

    @property
    def type(self): return self.model.type

    @property
    def subtype(self): return self.model.subtype

    @property
    def size(self): return self.model.size

    @property
    def persons(self):
        from ...persons.prototypes import get_person_by_model

        if not hasattr(self, '_persons'):
            self._persons = []
            for person_model in self.model.persons.order_by('power'):
                person = get_person_by_model(person_model)
                self._persons.append(person)

        return self._persons

    @property
    def total_persons_power(self): return sum([person.power for person in self.persons])

    def sync_persons(self):
        persons_count = len(self.persons)

        from ...persons.prototypes import PersonPrototype
        from ...persons.models import PERSON_CHOICES

        while persons_count < 3:
            PersonPrototype.create(self, 
                                   random.choice(PERSON_CHOICES)[0],
                                   'person_%s' % random.choice('QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm'))
            persons_count += 1
            

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
    def save(self): self.model.save(force_update=True)

    def map_info(self):
        return {'id': self.id,
                'pos': {'x': self.x, 'y': self.y},
                'name': self.name,
                'type': self.type,
                'subtype': self.subtype,
                'size': self.size}
