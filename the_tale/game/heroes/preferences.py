# coding: utf-8

import datetime

from game.balance import constants as c, enums as e

from game.mobs.storage import mobs_storage

from game.map.places.storage import places_storage

from game.persons.storage import persons_storage

from game.heroes.models import PREFERENCE_TYPE
from game.heroes.bag import SLOTS
from game.heroes.exceptions import HeroException


class HeroPreferences(object):

    def __init__(self, hero_model):
        self.hero_model = hero_model

    def can_update(self, preferences_type, current_time):
        return self.time_before_update(preferences_type, current_time).total_seconds() == 0

    def _time_before_update(self, changed_at, current_time):
        return max(datetime.timedelta(seconds=0), (changed_at + datetime.timedelta(seconds=c.CHARACTER_PREFERENCES_CHANGE_DELAY) - current_time))

    def time_before_update(self, preferences_type, current_time):
        if preferences_type == PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE: return self._time_before_update(self.energy_regeneration_type_changed_at, current_time)
        if preferences_type == PREFERENCE_TYPE.MOB: return self._time_before_update(self.mob_changed_at, current_time)
        if preferences_type == PREFERENCE_TYPE.PLACE: return self._time_before_update(self.place_changed_at, current_time)
        if preferences_type == PREFERENCE_TYPE.FRIEND: return self._time_before_update(self.friend_changed_at, current_time)
        if preferences_type == PREFERENCE_TYPE.ENEMY: return self._time_before_update(self.enemy_changed_at, current_time)
        if preferences_type == PREFERENCE_TYPE.EQUIPMENT_SLOT: return self._time_before_update(self.equipment_slot_changed_at, current_time)

        raise HeroException('unknown preference type')

    # energy_regeneration_type
    def get_energy_regeneration_type(self): return self.hero_model.pref_energy_regeneration_type
    def set_energy_regeneration_type(self, value): self.hero_model.pref_energy_regeneration_type = value
    energy_regeneration_type = property(get_energy_regeneration_type, set_energy_regeneration_type)

    @property
    def energy_regeneration_type_name(self):
        return e.ANGEL_ENERGY_REGENERATION_TYPES._ID_TO_TEXT[self.energy_regeneration_type]

    def get_energy_regeneration_type_changed_at(self): return self.hero_model.pref_energy_regeneration_type_changed_at
    def set_energy_regeneration_type_changed_at(self, value): self.hero_model.pref_energy_regeneration_type_changed_at = value
    energy_regeneration_type_changed_at = property(get_energy_regeneration_type_changed_at, set_energy_regeneration_type_changed_at)

    def get_mob(self):
        if self.hero_model.pref_mob_id is None:
            return None
        mob = mobs_storage[self.hero_model.pref_mob_id]

        if not mob.state.is_enabled:
            # if mob is disabled, we reset its value, so when hero save in logic, new preferences will appear in gui
            self.hero_model.pref_mob = None
            self.hero_model.pref_mob_changed_at = datetime.datetime(2000, 1, 1)
            return None

        return mob
    def set_mob(self, value):
        self.hero_model.pref_mob = value.model if value is not None else None
    mob = property(get_mob, set_mob)

    def get_mob_changed_at(self): return self.hero_model.pref_mob_changed_at
    def set_mob_changed_at(self, value): self.hero_model.pref_mob_changed_at = value
    mob_changed_at = property(get_mob_changed_at, set_mob_changed_at)


    # place
    def get_place_id(self): return self.hero_model.pref_place_id
    def set_place_id(self, value): self.hero_model.pref_place_id = value
    place_id = property(get_place_id, set_place_id)

    @property
    def place(self): return places_storage.get(self.hero_model.pref_place_id)

    def get_place_changed_at(self): return self.hero_model.pref_place_changed_at
    def set_place_changed_at(self, value): self.hero_model.pref_place_changed_at = value
    place_changed_at = property(get_place_changed_at, set_place_changed_at)


    # friend
    def get_friend_id(self): return self.hero_model.pref_friend_id
    def set_friend_id(self, value): self.hero_model.pref_friend_id = value
    friend_id = property(get_friend_id, set_friend_id)

    @property
    def friend(self): return persons_storage[self.hero_model.pref_friend_id] if self.hero_model.pref_friend_id else None

    def get_friend_changed_at(self): return self.hero_model.pref_friend_changed_at
    def set_friend_changed_at(self, value): self.hero_model.pref_friend_changed_at = value
    friend_changed_at = property(get_friend_changed_at, set_friend_changed_at)

    # enemy
    def get_enemy_id(self): return self.hero_model.pref_enemy_id
    def set_enemy_id(self, value): self.hero_model.pref_enemy_id = value
    enemy_id = property(get_enemy_id, set_enemy_id)

    @property
    def enemy(self): return persons_storage[self.hero_model.pref_enemy_id] if self.hero_model.pref_enemy_id else None

    def get_enemy_changed_at(self): return self.hero_model.pref_enemy_changed_at
    def set_enemy_changed_at(self, value): self.hero_model.pref_enemy_changed_at = value
    enemy_changed_at = property(get_enemy_changed_at, set_enemy_changed_at)

    # equipment_slot
    def get_equipment_slot(self):
        if not self.hero_model.pref_equipment_slot:
            return None
        return self.hero_model.pref_equipment_slot
    def set_equipment_slot(self, value): self.hero_model.pref_equipment_slot = value
    equipment_slot = property(get_equipment_slot, set_equipment_slot)

    def get_equipment_slot_changed_at(self): return self.hero_model.pref_equipment_slot_changed_at
    def set_equipment_slot_changed_at(self, value): self.hero_model.pref_equipment_slot_changed_at = value
    equipment_slot_changed_at = property(get_equipment_slot_changed_at, set_equipment_slot_changed_at)

    @property
    def equipment_slot_name(self):
        return SLOTS._ID_TO_TEXT[self.equipment_slot]


    # helpers

    @classmethod
    def _heroes_query(cls):
        from game.heroes.prototypes import HeroPrototype
        return HeroPrototype._model_class.objects.filter(premium_state_end_at__gte=datetime.datetime.now())

    @classmethod
    def count_friends_of(cls, person):
        return cls._heroes_query().filter(pref_friend_id=person.id).count()

    @classmethod
    def count_enemies_of(cls, person):
        return cls._heroes_query().filter(pref_enemy_id=person.id).count()

    @classmethod
    def count_citizens_of(cls, place):
        return cls._heroes_query().filter(pref_place_id=place.id).count()

    @classmethod
    def get_friends_of(cls, person):
        from game.heroes.prototypes import HeroPrototype
        return [HeroPrototype(model=record) for record in cls._heroes_query().filter(pref_friend_id=person.id)]

    @classmethod
    def get_enemies_of(cls, person):
        from game.heroes.prototypes import HeroPrototype
        return [HeroPrototype(model=record) for record in cls._heroes_query().filter(pref_enemy_id=person.id)]

    @classmethod
    def get_citizens_of(cls, place):
        from game.heroes.prototypes import HeroPrototype
        return [HeroPrototype(model=record) for record in cls._heroes_query().filter(pref_place_id=place.id)]

    # get_friendly_heroes
    # get_enemy_heroes
    # get_place_heroes
