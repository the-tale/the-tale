# coding: utf-8

from dext.utils import s11n

from textgen.words import Fake

from game.game_info import GENDER_ID_2_STR
from game.map.places.storage import places_storage
from game.heroes.models import Hero
from game.prototypes import TimePrototype
from game.helpers import add_power_management

from game.persons.models import Person, PERSON_STATE
from game.persons.conf import persons_settings
from game.persons.exceptions import PersonsException


@add_power_management(persons_settings.POWER_HISTORY_LENGTH, PersonsException)
class PersonPrototype(object):

    def __init__(self, model):
        self.model = model

    @classmethod
    def get_by_id(cls, id_):
        return cls(Person.objects.get(id=id_))

    @property
    def id(self): return self.model.id

    @property
    def place_id(self): return self.model.place_id

    @property
    def place(self): return places_storage[self.model.place_id]

    @property
    def name(self): return self.model.name

    @property
    def normalized_name(self): return (Fake(self.model.name), (GENDER_ID_2_STR[self.gender], u'загл'))

    @property
    def gender(self): return self.model.gender

    @property
    def race(self): return self.model.race

    @property
    def race_verbose(self):
        from game.game_info import RACE
        return RACE.ID_2_TEXT[self.race]

    @property
    def type(self): return self.model.type

    @property
    def state(self): return self.model.state

    def move_out_game(self): self.model.state = PERSON_STATE.OUT_GAME
    def move_in_game(self):  self.model.state = PERSON_STATE.IN_GAME

    @property
    def out_game(self): return self.model.state == PERSON_STATE.OUT_GAME

    @property
    def in_game(self):  return self.model.state == PERSON_STATE.IN_GAME

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = s11n.from_json(self.model.data)
        return self._data

    @property
    def type_verbose(self):
        from .models import PERSON_TYPE_DICT
        return PERSON_TYPE_DICT[self.type]

    @property
    def friends_number(self): return self.model.friends_number
    def update_friends_number(self):
        current_turn = TimePrototype.get_current_turn_number()
        self.model.friends_number = Hero.objects.filter(pref_friend_id=self.id, active_state_end_at__gte=current_turn).count()

    @property
    def enemies_number(self): return self.model.enemies_number
    def update_enemies_number(self):
        current_turn = TimePrototype.get_current_turn_number()
        self.model.enemies_number = Hero.objects.filter(pref_enemy_id=self.id, active_state_end_at__gte=current_turn).count()

    def save(self):
        self.model.data = s11n.to_json(self.data)
        self.model.save()

    def remove(self):
        self.model.remove()

    @classmethod
    def create(cls, place, race, tp, name, gender, state=None):

        instance = Person.objects.create(place=place.model,
                                         state=state if state is not None else PERSON_STATE.IN_GAME,
                                         race=race,
                                         type=tp,
                                         gender=gender,
                                         name=name)

        return cls(model=instance)
