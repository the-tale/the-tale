# coding: utf-8
import datetime

from dext.utils import s11n

from textgen.words import Fake

from common.utils.logic import choose_from_interval

from game.game_info import GENDER_ID_2_STR
from game.map.places.storage import places_storage
from game.heroes.models import Hero
from game.prototypes import TimePrototype
from game.helpers import add_power_management

from game.balance.enums import RACE, PERSON_TYPE
from game.balance import constants as c

from game.persons.models import Person, PERSON_STATE
from game.persons.conf import persons_settings
from game.persons.exceptions import PersonsException

MASTERY_VERBOSE = ( (0.0, u'полная непригодность'),
                    (0.1, u'бездарность'),
                    (0.2, u'невежда'),
                    (0.3, u'неуч'),
                    (0.4, u'ученик'),
                    (0.5, u'подмастерье'),
                    (0.6, u'умелец'),
                    (0.7, u'мастер'),
                    (0.8, u'эксперт'),
                    (0.9, u'мэтр'),
                    (1.0, u'гений') )


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
    def created_at_turn(self): return self.model.created_at_turn

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
        return RACE._ID_TO_TEXT[self.race]

    @property
    def type(self): return self.model.type

    @property
    def mastery(self): return c.PROFESSION_TO_RACE_MASTERY[self.type][self.race]

    @property
    def mastery_verbose(self): return choose_from_interval(self.mastery, MASTERY_VERBOSE)

    @property
    def state(self): return self.model.state

    @property
    def out_game_at(self): return self.model.out_game_at

    def move_out_game(self):
        self.model.out_game_at = datetime.datetime.now()
        self.model.state = PERSON_STATE.OUT_GAME

    def remove_from_game(self):
        self.model.state = PERSON_STATE.REMOVED

    def cmd_change_power(self, power):
        from game.workers.environment import workers_environment
        if self.place.modifier:
            power = self.place.modifier.modify_power(power)
        workers_environment.highlevel.cmd_change_person_power(self.id, power)

    @property
    def time_before_unfreeze(self):
        current_time = datetime.datetime.now()
        return max(datetime.timedelta(seconds=0),
                   self.model.created_at + datetime.timedelta(seconds=persons_settings.POWER_STABILITY_WEEKS*7*24*60*60) - current_time)

    @property
    def is_stable(self):
        if self.created_at_turn > TimePrototype.get_current_turn_number() - persons_settings.POWER_STABILITY_WEEKS*7*24*c.TURNS_IN_HOUR:
            return True

        power_percent = float(self.power) / self.place.power if self.place.power > 0.0001 else 0.0

        if power_percent  > persons_settings.POWER_STABILITY_PERCENT:
            return True

        return False

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
        return PERSON_TYPE._ID_TO_TEXT[self.type]

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
                                         name=name,
                                         created_at_turn=TimePrototype.get_current_turn_number())

        return cls(model=instance)
