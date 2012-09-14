# coding: utf-8

import datetime

from game.balance import constants as c

from game.mobs.storage import MobsDatabase

from game.map.places.storage import places_storage

from game.persons.models import Person
from game.persons.storage import persons_storage

from game.heroes.models import ChoosePreferencesTask, PREFERENCE_TYPE, CHOOSE_PREFERENCES_STATE, ANGEL_ENERGY_REGENERATION_TYPES_DICT
from game.heroes.bag import SLOTS_LIST, SLOTS_DICT
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
        return ANGEL_ENERGY_REGENERATION_TYPES_DICT[self.energy_regeneration_type]

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


class ChoosePreferencesTaskPrototype(object):

    def __init__(self, model):
        self.model = model

    @classmethod
    def get_by_id(cls, id_):
        try:
            return cls(ChoosePreferencesTask.objects.get(id=id_))
        except ChoosePreferencesTask.DoesNotExist:
            return None

    @classmethod
    def create(cls, hero, preference_type, preference_id):

        model = ChoosePreferencesTask.objects.create(hero=hero.model,
                                                     preference_type=preference_type,
                                                     preference_id=str(preference_id) if preference_id is not None else None)

        return cls(model)

    @classmethod
    def reset_all(cls):
        ChoosePreferencesTask.objects.filter(state=CHOOSE_PREFERENCES_STATE.WAITING).update(state=CHOOSE_PREFERENCES_STATE.RESET)

    @property
    def state(self): return self.model.state

    @property
    def id(self): return self.model.id

    @property
    def hero_id(self): return self.model.hero_id

    @property
    def is_unprocessed(self):
        return self.model.state == CHOOSE_PREFERENCES_STATE.WAITING

    def process(self, bundle):

        if not self.is_unprocessed:
            return

        hero = bundle.heroes[self.model.hero_id]

        if not hero.preferences.can_update(self.model.preference_type, datetime.datetime.now()):
            self.model.comment = u'blocked since time delay'
            self.model.state = CHOOSE_PREFERENCES_STATE.COOLDOWN
            return

        if self.model.preference_type == PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE:

            if hero.level < c.CHARACTER_PREFERENCES_ENERGY_REGENERATION_TYPE_LEVEL_REQUIRED:
                self.model.comment = u'hero level < required level (%d < %d)' % (hero.level, c.CHARACTER_PREFERENCES_ENERGY_REGENERATION_TYPE_LEVEL_REQUIRED)
                self.model.state = CHOOSE_PREFERENCES_STATE.ERROR
                return

            energy_regeneration_type = int(self.model.preference_id) if self.model.preference_id is not None else None

            if energy_regeneration_type is None:
                raise HeroException(u'energy_regeneration_type property is None, something go wrong, hero: %d' % hero.id)

            if energy_regeneration_type not in c.ANGEL_ENERGY_REGENERATION_DELAY:
                self.model.comment = u'unknown energy regeneration type: %s' % (energy_regeneration_type, )
                self.model.state = CHOOSE_PREFERENCES_STATE.ERROR
                return

            hero.preferences.energy_regeneration_type = energy_regeneration_type
            hero.preferences.energy_regeneration_type_changed_at = datetime.datetime.now()


        elif self.model.preference_type == PREFERENCE_TYPE.MOB:

            mob_id = self.model.preference_id

            if mob_id is not None:

                if hero.level < c.CHARACTER_PREFERENCES_MOB_LEVEL_REQUIRED:
                    self.model.comment = u'hero level < required level (%d < %d)' % (hero.level, c.CHARACTER_PREFERENCES_MOB_LEVEL_REQUIRED)
                    self.model.state = CHOOSE_PREFERENCES_STATE.ERROR
                    return

                if self.model.preference_id not in MobsDatabase.storage():
                    self.model.comment = u'unknown mob id: %s' % (self.model.preference_id, )
                    self.model.state = CHOOSE_PREFERENCES_STATE.ERROR
                    return

                mob = MobsDatabase.storage()[self.model.preference_id]

                if hero.level < mob.level:
                    self.model.comment = u'hero level < mob level (%d < %d)' % (hero.level, mob.level)
                    self.model.state = CHOOSE_PREFERENCES_STATE.ERROR
                    return

            hero.preferences.mob_id = mob_id
            hero.preferences.mob_changed_at = datetime.datetime.now()

        elif self.model.preference_type == PREFERENCE_TYPE.PLACE:

            place_id = int(self.model.preference_id) if self.model.preference_id is not None else None

            if place_id is not None:

                if hero.level < c.CHARACTER_PREFERENCES_PLACE_LEVEL_REQUIRED:
                    self.model.comment = u'hero level < required level (%d < %d)' % (hero.level, c.CHARACTER_PREFERENCES_PLACE_LEVEL_REQUIRED)
                    self.model.state = CHOOSE_PREFERENCES_STATE.ERROR
                    return

                if place_id not in places_storage:
                    self.model.comment = u'unknown place id: %s' % (place_id, )
                    self.model.state = CHOOSE_PREFERENCES_STATE.ERROR
                    return

            hero.preferences.place_id = place_id
            hero.preferences.place_changed_at = datetime.datetime.now()

        elif self.model.preference_type == PREFERENCE_TYPE.FRIEND:

            friend_id = int(self.model.preference_id) if self.model.preference_id is not None else None

            if friend_id is not None:
                if hero.level < c.CHARACTER_PREFERENCES_FRIEND_LEVEL_REQUIRED:
                    self.model.comment = u'hero level < required level (%d < %d)' % (hero.level, c.CHARACTER_PREFERENCES_FRIEND_LEVEL_REQUIRED)
                    self.model.state = CHOOSE_PREFERENCES_STATE.ERROR
                    return

                if not Person.objects.filter(id=friend_id).exists():
                    self.model.comment = u'unknown person id: %s' % (place_id, )
                    self.model.state = CHOOSE_PREFERENCES_STATE.ERROR
                    return

            hero.preferences.friend_id = friend_id
            hero.preferences.friend_changed_at = datetime.datetime.now()

        elif self.model.preference_type == PREFERENCE_TYPE.ENEMY:

            enemy_id = int(self.model.preference_id) if self.model.preference_id is not None else None

            if enemy_id is not None:
                if hero.level < c.CHARACTER_PREFERENCES_ENEMY_LEVEL_REQUIRED:
                    self.model.comment = u'hero level < required level (%d < %d)' % (hero.level, c.CHARACTER_PREFERENCES_ENEMY_LEVEL_REQUIRED)
                    self.model.state = CHOOSE_PREFERENCES_STATE.ERROR
                    return

                if not Person.objects.filter(id=enemy_id).exists():
                    self.model.comment = u'unknown person id: %s' % (place_id, )
                    self.model.state = CHOOSE_PREFERENCES_STATE.ERROR
                    return

            hero.preferences.enemy_id = enemy_id
            hero.preferences.enemy_changed_at = datetime.datetime.now()

        elif self.model.preference_type == PREFERENCE_TYPE.EQUIPMENT_SLOT:

            equipment_slot = self.model.preference_id

            if equipment_slot is not None:

                if hero.level < c.CHARACTER_PREFERENCES_EQUIPMENT_SLOT_LEVEL_REQUIRED:
                    self.model.comment = u'hero level < required level (%d < %d)' % (hero.level, c.CHARACTER_PREFERENCES_EQUIPMENT_SLOT_LEVEL_REQUIRED)
                    self.model.state = CHOOSE_PREFERENCES_STATE.ERROR
                    return

                if self.model.preference_id not in SLOTS_LIST:
                    self.model.comment = u'unknown equipment slot: %s' % (equipment_slot, )
                    self.model.state = CHOOSE_PREFERENCES_STATE.ERROR
                    return

            hero.preferences.equipment_slot = equipment_slot
            hero.preferences.equipment_slot_changed_at = datetime.datetime.now()

        else:
            self.model.comment = u'unknown preference type: %s' % (self.model.preference_type, )
            self.model.state = CHOOSE_PREFERENCES_STATE.ERROR
            return


        self.model.state = CHOOSE_PREFERENCES_STATE.PROCESSED


    def save(self):
        self.model.save()
