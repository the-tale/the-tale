# coding: utf-8

import datetime

from django.utils.log import getLogger

from common.utils.enum import create_enum
from common.postponed_tasks import postponed_task

from game.balance import constants as c

from game.mobs.storage import MobsDatabase

from game.map.places.storage import places_storage

from game.persons.storage import persons_storage

from game.heroes.models import PREFERENCE_TYPE
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
        return c.ANGEL_ENERGY_REGENERATION_TYPES.ID_2_TEXT[self.energy_regeneration_type]

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


CHOOSE_PREFERENCES_TASK_STATE = create_enum('CHOOSE_PREFERENCES_TASK_STATE', ( ('UNPROCESSED', 0, u'в очереди'),
                                                                               ('PROCESSED', 1, u'обработана'),
                                                                               ('COOLDOWN', 2, u'смена способности недоступна'),
                                                                               ('LOW_LEVEL', 3, u'низкий уровень героя'),
                                                                               ('UNAVAILABLE_PERSON', 4, u'персонаж недоступен'),
                                                                               ('OUTGAME_PERSON', 5, u'персонаж выведен из игры'),
                                                                               ('UNSPECIFIED_PREFERENCE', 6, u'предпочтение неуказано'),
                                                                               ('UNKNOWN_ENERGY_REGENERATION_TYPE', 7, u'неизвестный тип восстановления энергии'),
                                                                               ('UNKNOWN_MOB', 8, u'неизвестный тип монстра'),
                                                                               ('LARGE_MOB_LEVEL', 9, u'слишком сильный монстр'),
                                                                               ('UNKNOWN_PLACE', 10, u'неизвестное место'),
                                                                               ('ENEMY_AND_FRIEND', 11, u'персонаж одновременно и друг и враг'),
                                                                               ('UNKNOWN_PERSON', 12, u'неизвестный персонаж'),
                                                                               ('UNKNOWN_EQUIPMENT_SLOT', 13, u'неизвестный тип экипировки'),
                                                                               ('UNKNOWN_PREFERENCE', 14, u'неизвестный тип предпочтения'),) )


@postponed_task
class ChoosePreferencesTask(object):

    TYPE = 'choose-hero-preferences'
    INITIAL_STATE = CHOOSE_PREFERENCES_TASK_STATE.UNPROCESSED
    LOGGER = getLogger('the-tale.workers.game_logic')

    def __init__(self, hero_id, preference_type, preference_id, state=INITIAL_STATE):
        self.hero_id = hero_id
        self.preference_type = preference_type
        self.preference_id = preference_id
        self.state = state

    def __eq__(self, other):
        return (self.hero_id == other.hero_id and
                self.preference_type == other.preference_type and
                self.preference_id == other.preference_id and
                self.state == other.state )

    def serialize(self):
        return { 'hero_id': self.hero_id,
                 'preference_type': self.preference_type,
                 'preference_id': self.preference_id,
                 'state': self.state }

    @classmethod
    def deserialize(cls, data):
        return cls(**data)

    @property
    def uuid(self): return self.hero_id

    @property
    def response_data(self): return {}

    @property
    def error_message(self): return CHOOSE_PREFERENCES_TASK_STATE.CHOICES[self.state]

    def process(self, main_task, storage):

        hero = storage.heroes[self.hero_id]

        if not hero.preferences.can_update(self.preference_type, datetime.datetime.now()):
            main_task.comment = u'blocked since time delay'
            self.state = CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN
            return False

        if self.preference_type == PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE:

            if hero.level < c.CHARACTER_PREFERENCES_ENERGY_REGENERATION_TYPE_LEVEL_REQUIRED:
                main_task.comment = u'hero level < required level (%d < %d)' % (hero.level, c.CHARACTER_PREFERENCES_ENERGY_REGENERATION_TYPE_LEVEL_REQUIRED)
                self.state = CHOOSE_PREFERENCES_TASK_STATE.LOW_LEVEL
                return False

            energy_regeneration_type = int(self.preference_id) if self.preference_id is not None else None

            if energy_regeneration_type is None:
                main_task.comment = u'energy regeneration preference can not be None'
                self.state = CHOOSE_PREFERENCES_TASK_STATE.UNSPECIFIED_PREFERENCE
                return False

            if energy_regeneration_type not in c.ANGEL_ENERGY_REGENERATION_DELAY:
                main_task.comment = u'unknown energy regeneration type: %s' % (energy_regeneration_type, )
                self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_ENERGY_REGENERATION_TYPE
                return False

            hero.preferences.energy_regeneration_type = energy_regeneration_type
            hero.preferences.energy_regeneration_type_changed_at = datetime.datetime.now()


        elif self.preference_type == PREFERENCE_TYPE.MOB:

            mob_id = self.preference_id

            if mob_id is not None:

                if hero.level < c.CHARACTER_PREFERENCES_MOB_LEVEL_REQUIRED:
                    main_task.comment = u'hero level < required level (%d < %d)' % (hero.level, c.CHARACTER_PREFERENCES_MOB_LEVEL_REQUIRED)
                    self.state = CHOOSE_PREFERENCES_TASK_STATE.LOW_LEVEL
                    return False

                if self.preference_id not in MobsDatabase.storage():
                    main_task.comment = u'unknown mob id: %s' % (self.preference_id, )
                    self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_MOB
                    return False

                mob = MobsDatabase.storage()[self.preference_id]

                if hero.level < mob.level:
                    main_task.comment = u'hero level < mob level (%d < %d)' % (hero.level, mob.level)
                    self.state = CHOOSE_PREFERENCES_TASK_STATE.LARGE_MOB_LEVEL
                    return False

            hero.preferences.mob_id = mob_id
            hero.preferences.mob_changed_at = datetime.datetime.now()

        elif self.preference_type == PREFERENCE_TYPE.PLACE:

            place_id = int(self.preference_id) if self.preference_id is not None else None

            if place_id is not None:

                if hero.level < c.CHARACTER_PREFERENCES_PLACE_LEVEL_REQUIRED:
                    main_task.comment = u'hero level < required level (%d < %d)' % (hero.level, c.CHARACTER_PREFERENCES_PLACE_LEVEL_REQUIRED)
                    self.state = CHOOSE_PREFERENCES_TASK_STATE.LOW_LEVEL
                    return False

                if place_id not in places_storage:
                    main_task.comment = u'unknown place id: %s' % (place_id, )
                    self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_PLACE
                    return False

            hero.preferences.place_id = place_id
            hero.preferences.place_changed_at = datetime.datetime.now()

        elif self.preference_type == PREFERENCE_TYPE.FRIEND:

            friend_id = int(self.preference_id) if self.preference_id is not None else None

            if friend_id is not None:
                if hero.level < c.CHARACTER_PREFERENCES_FRIEND_LEVEL_REQUIRED:
                    main_task.comment = u'hero level < required level (%d < %d)' % (hero.level, c.CHARACTER_PREFERENCES_FRIEND_LEVEL_REQUIRED)
                    self.state = CHOOSE_PREFERENCES_TASK_STATE.LOW_LEVEL
                    return False

                if hero.preferences.enemy_id == friend_id:
                    main_task.comment = u'try set enemy as a friend (%d)' % (friend_id, )
                    self.state = CHOOSE_PREFERENCES_TASK_STATE.ENEMY_AND_FRIEND
                    return False

                if friend_id not in persons_storage:
                    main_task.comment = u'unknown person id: %s' % (friend_id, )
                    self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_PERSON
                    return False

                if persons_storage[friend_id].out_game:
                    main_task.comment = u'person was moved out game: %s' % (friend_id, )
                    self.state = CHOOSE_PREFERENCES_TASK_STATE.OUTGAME_PERSON
                    return False

            hero.preferences.friend_id = friend_id
            hero.preferences.friend_changed_at = datetime.datetime.now()

        elif self.preference_type == PREFERENCE_TYPE.ENEMY:

            enemy_id = int(self.preference_id) if self.preference_id is not None else None

            if enemy_id is not None:
                if hero.level < c.CHARACTER_PREFERENCES_ENEMY_LEVEL_REQUIRED:
                    main_task.comment = u'hero level < required level (%d < %d)' % (hero.level, c.CHARACTER_PREFERENCES_ENEMY_LEVEL_REQUIRED)
                    self.state = CHOOSE_PREFERENCES_TASK_STATE.LOW_LEVEL
                    return False

                if hero.preferences.friend_id == enemy_id:
                    main_task.comment = u'try set friend as an enemy (%d)' % (enemy_id, )
                    self.state = CHOOSE_PREFERENCES_TASK_STATE.ENEMY_AND_FRIEND
                    return False

                if enemy_id not in persons_storage:
                    main_task.comment = u'unknown person id: %s' % (enemy_id, )
                    self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_PERSON
                    return False

                if persons_storage[enemy_id].out_game:
                    main_task.comment = u'person was moved out game: %s' % (enemy_id, )
                    self.state = CHOOSE_PREFERENCES_TASK_STATE.OUTGAME_PERSON
                    return False


            hero.preferences.enemy_id = enemy_id
            hero.preferences.enemy_changed_at = datetime.datetime.now()

        elif self.preference_type == PREFERENCE_TYPE.EQUIPMENT_SLOT:

            equipment_slot = self.preference_id

            if equipment_slot is not None:

                if hero.level < c.CHARACTER_PREFERENCES_EQUIPMENT_SLOT_LEVEL_REQUIRED:
                    main_task.comment = u'hero level < required level (%d < %d)' % (hero.level, c.CHARACTER_PREFERENCES_EQUIPMENT_SLOT_LEVEL_REQUIRED)
                    self.state = CHOOSE_PREFERENCES_TASK_STATE.LOW_LEVEL
                    return False

                if self.preference_id not in SLOTS_LIST:
                    main_task.comment = u'unknown equipment slot: %s' % (equipment_slot, )
                    self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_EQUIPMENT_SLOT
                    return False

            hero.preferences.equipment_slot = equipment_slot
            hero.preferences.equipment_slot_changed_at = datetime.datetime.now()

        else:
            main_task.comment = u'unknown preference type: %s' % (self.preference_type, )
            self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_PREFERENCE
            return False


        self.state = CHOOSE_PREFERENCES_TASK_STATE.PROCESSED
        return True
