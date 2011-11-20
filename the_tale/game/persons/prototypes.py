# coding: utf-8

from .models import Person

def get_person_by_model(model):
    return PersonPrototype(model=model)

class PersonPrototype(object):

    def __init__(self, model):
        self.model = model

    @property
    def id(self): return self.model.id

    @property
    def name(self): return self.model.name

    @property
    def race(self): return self.model.race

    @property
    def race_verbose(self):
        from ..game_info import RACE_DICT
        return RACE_DICT[self.race]
    
    @property
    def type(self): return self.model.type

    @property
    def type_verbose(self):
        from .models import PERSON_TYPE_DICT
        return PERSON_TYPE_DICT[self.type]

    def get_power(self): return self.model.power
    def set_power(self, value): self.model.power = value
    power = property(get_power, set_power)

    def save(self):
        self.model.save()

    def remove(self):
        self.model.remove()

    @classmethod
    def create(cls, place, race, tp, name, power=0):
        
        instance = Person.objects.create(place=place.model,
                                         race=race,
                                         type=tp,
                                         name=name,
                                         power=power)

        return cls(model=instance)
