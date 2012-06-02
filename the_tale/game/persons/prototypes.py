# coding: utf-8

from textgen.words import Fake

from game.game_info import GENDER_ID_2_STR

from .models import Person, PERSON_STATE

def get_person_by_model(model):
    return PersonPrototype(model=model)

class PersonPrototype(object):

    def __init__(self, model):
        self.model = model

    @classmethod
    def get_by_id(cls, id_):
        return cls(Person.objects.get(id=id_))

    @property
    def id(self): return self.model.id

    @property
    def name(self): return self.model.name

    @property
    def normalized_name(self): return (Fake(self.model.name), GENDER_ID_2_STR[self.gender])

    @property
    def gender(self): return self.model.gender

    @property
    def race(self): return self.model.race

    @property
    def race_verbose(self):
        from ..game_info import RACE_DICT
        return RACE_DICT[self.race]

    @property
    def type(self): return self.model.type

    @property
    def state(self): return self.model.state

    def move_out_game(self): self.model.state = PERSON_STATE.OUT_GAME
    def move_in_game(self):  self.model.state = PERSON_STATE.IN_GAME

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
    def create(cls, place, race, tp, name, gender, power=0):

        instance = Person.objects.create(place=place.model,
                                         state=PERSON_STATE.IN_GAME,
                                         race=race,
                                         type=tp,
                                         gender=gender,
                                         name=name,
                                         power=power)

        return cls(model=instance)
