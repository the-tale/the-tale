# coding: utf-8

import datetime

from game.balance import constants as c

from game.mobs.storage import MobsDatabase

from game.map.places.storage import places_storage

from game.persons.storage import persons_storage

from game.heroes.models import PREFERENCE_TYPE
from game.heroes.bag import SLOTS_DICT
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
        return c.ANGEL_ENERGY_REGENERATION_TYPES._ID_TO_TEXT[self.energy_regeneration_type]

    def get_energy_regeneration_type_changed_at(self): return self.hero_model.pref_energy_regeneration_type_changed_at
    def set_energy_regeneration_type_changed_at(self, value): self.hero_model.pref_energy_regeneration_type_changed_at = value
    energy_regeneration_type_changed_at = property(get_energy_regeneration_type_changed_at, set_energy_regeneration_type_changed_at)


    # mob
    def get_mob_id(self):
        if not self.hero_model.pref_mob_id:
            return None
        return self.hero_model.pref_mob_id
    def set_mob_id(self, value): self.hero_model.pref_mob_id = value
    mob_id = property(get_mob_id, set_mob_id)

    @property
    def mob(self):
        if self.mob_id is None:
            return None
        return MobsDatabase.storage()[self.mob_id]

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
        return SLOTS_DICT.get(self.equipment_slot)
