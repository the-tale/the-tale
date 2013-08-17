# coding: utf-8
import time
import datetime

import rels

from common.utils.prototypes import BasePrototype

from game.balance import constants as c, enums as e

from game.mobs.storage import mobs_storage

from game.map.places.storage import places_storage

from game.persons.storage import persons_storage

from game.heroes.exceptions import WrongPreferenceTypeError
from game.heroes.relations import EQUIPMENT_SLOT, PREFERENCE_TYPE
from game.heroes.prototypes import HeroPrototype, HeroPreferencesPrototype


class _PreferencesMetaclass(type):

    @classmethod
    def create_preference_getter(cls, preference):

        def getter(self):
            return self._get(preference)
        getter.__name__ = preference.base_name

        return getter

    @classmethod
    def create_preference_setter(cls, preference):

        def setter(self, value, change_time=None):
            return self._set(preference, value, change_time=change_time)
        setter.__name__ = 'set_%s' % preference.base_name

        return setter

    @classmethod
    def create_preference_reseter(cls, preference):

        def reseter(self):
            return self._reset(preference)
        reseter.__name__ = 'reset_%s' % preference.base_name

        return reseter


    @classmethod
    def create_preference_changed_at_getter(cls, preference):

        def getter(self):
            return self._get_changed_at(preference)
        getter.__name__ = '%s_changed_at' % preference.base_name

        return getter


    def __new__(mcs, name, bases, attributes):

        for preference in PREFERENCE_TYPE._records:
            getter = mcs.create_preference_getter(preference)
            attributes[getter.__name__] = property(getter)

            getter = mcs.create_preference_changed_at_getter(preference)
            attributes[getter.__name__] = property(getter)

            setter = mcs.create_preference_setter(preference)
            attributes[setter.__name__] = setter

            reseter = mcs.create_preference_reseter(preference)
            attributes[reseter.__name__] = reseter

        return super(_PreferencesMetaclass, mcs).__new__(mcs, name, bases, attributes)


class HeroPreferences(object):

    __metaclass__ = _PreferencesMetaclass

    def __init__(self, hero_id):
        self.data = {}
        self.updated = False
        self.hero_id = hero_id

    def serialize(self):
        return self.data

    @classmethod
    def deserialize(cls, hero_id, data):
        obj = cls(hero_id=hero_id)
        obj.data = data
        return obj

    def can_update(self, preferences_type, current_time):
        return self.time_before_update(preferences_type, current_time).total_seconds() == 0

    def _time_before_update(self, changed_at, current_time):
        return max(datetime.timedelta(seconds=0), (changed_at + datetime.timedelta(seconds=c.CHARACTER_PREFERENCES_CHANGE_DELAY) - current_time))

    def time_before_update(self, preferences_type, current_time):
        if preferences_type._is_ENERGY_REGENERATION_TYPE: return self._time_before_update(self.energy_regeneration_type_changed_at, current_time)
        if preferences_type._is_MOB: return self._time_before_update(self.mob_changed_at, current_time)
        if preferences_type._is_PLACE: return self._time_before_update(self.place_changed_at, current_time)
        if preferences_type._is_FRIEND: return self._time_before_update(self.friend_changed_at, current_time)
        if preferences_type._is_ENEMY: return self._time_before_update(self.enemy_changed_at, current_time)
        if preferences_type._is_EQUIPMENT_SLOT: return self._time_before_update(self.equipment_slot_changed_at, current_time)

        raise WrongPreferenceTypeError(preference_type=preferences_type)

    def _prepair_value_prototype(self, value):
        return value.id if value is not None else None

    def _prepair_value_record(self, value):
        return value.value if value is not None else None

    def value_to_set(self, value):
        if isinstance(value, BasePrototype):
            return self._prepair_value_prototype(value)
        if isinstance(value, rels.Record):
            return self._prepair_value_record(value)
        return value

    def _set(self, preferences_type, value, change_time=None):
        self.updated = True

        if change_time is None:
            change_time = datetime.datetime.now()

        value = self.value_to_set(value)

        self.data[preferences_type.base_name] = {'value': value,
                                                 'changed_at': time.mktime(change_time.timetuple())}
        HeroPreferencesPrototype.update(self.hero_id, preferences_type.base_name, value)

    def _reset(self, preferences_type):
        self._set(preferences_type, None, change_time=datetime.datetime.fromtimestamp(0))

    def _prepair_mob(self, mob_id):
        mob = mobs_storage.get(mob_id)

        if mob and not mob.state.is_enabled:
            self.set_mob(None, change_time=datetime.datetime.fromtimestamp(0))
            return None

        return mob

    def _prepair_place(self, place_id): return places_storage.get(place_id)

    def _prepair_person(self, person_id): return persons_storage.get(person_id)

    def _prepair_equipment_slot(self, slot_id):
        if slot_id is None: return None
        return EQUIPMENT_SLOT._index_value.get(int(slot_id))

    def _get(self, preferences_type):
        if preferences_type.base_name not in self.data:
            return None

        value = self.data[preferences_type.base_name]['value']

        if preferences_type._is_ENERGY_REGENERATION_TYPE:
            return value
        if preferences_type._is_MOB:
            return self._prepair_mob(value)
        if preferences_type._is_PLACE:
            return self._prepair_place(value)
        if preferences_type._is_FRIEND:
            return self._prepair_person(value)
        if preferences_type._is_ENEMY:
            return self._prepair_person(value)
        if preferences_type._is_EQUIPMENT_SLOT:
            return self._prepair_equipment_slot(value)

    def _get_changed_at(self, preferences_type, default=datetime.datetime.fromtimestamp(0)):
        if preferences_type.base_name not in self.data:
            return default
        return datetime.datetime.fromtimestamp(self.data[preferences_type.base_name]['changed_at'])

    @property
    def energy_regeneration_type_name(self):
        return e.ANGEL_ENERGY_REGENERATION_TYPES._ID_TO_TEXT[self.energy_regeneration_type]

    # helpers

    @classmethod
    def _preferences_query(cls):
        current_time = datetime.datetime.now()
        return HeroPreferencesPrototype._model_class.objects.filter(hero__ban_state_end_at__lt=current_time, hero__premium_state_end_at__gte=current_time)

    @classmethod
    def _heroes_query(cls):
        current_time = datetime.datetime.now()
        return HeroPrototype._model_class.objects.filter(ban_state_end_at__lt=current_time, premium_state_end_at__gte=current_time)

    @classmethod
    def count_friends_of(cls, person):
        return cls._preferences_query().filter(friend_id=person.id).count()

    @classmethod
    def count_enemies_of(cls, person):
        return cls._preferences_query().filter(enemy_id=person.id).count()

    @classmethod
    def count_citizens_of(cls, place):
        return cls._preferences_query().filter(place_id=place.id).count()

    @classmethod
    def get_friends_of(cls, person):
        return [HeroPrototype(model=record) for record in cls._heroes_query().filter(heropreferences__friend_id=person.id)]

    @classmethod
    def get_enemies_of(cls, person):
        return [HeroPrototype(model=record) for record in cls._heroes_query().filter(heropreferences__enemy_id=person.id)]

    @classmethod
    def get_citizens_of(cls, place):
        return [HeroPrototype(model=record) for record in cls._heroes_query().filter(heropreferences__place_id=place.id)]
