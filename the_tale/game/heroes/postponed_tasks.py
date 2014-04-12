# coding: utf-8
import datetime

import rels
from rels.django import DjangoEnum

from textgen.words import Noun

from the_tale.common.postponed_tasks import PostponedLogic, POSTPONED_TASK_LOGIC_RESULT
from the_tale.common.utils.enum import create_enum

from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.relations import GENDER, RACE
from the_tale.game.balance import constants as c

from the_tale.game.map.places.storage import places_storage
from the_tale.game.mobs.storage import mobs_storage
from the_tale.game.persons.storage import persons_storage

from the_tale.game.heroes.habilities import ABILITIES, ABILITY_AVAILABILITY
from the_tale.game.heroes.relations import PREFERENCE_TYPE, EQUIPMENT_SLOT, RISK_LEVEL


CHOOSE_HERO_ABILITY_STATE = create_enum('CHOOSE_HERO_ABILITY_STATE', ( ('UNPROCESSED', 0, u'в очереди'),
                                                                       ('PROCESSED', 1, u'обработана'),
                                                                       ('WRONG_ID', 2, u'неверный идентификатор способности'),
                                                                       ('NOT_IN_CHOICE_LIST', 3, u'способность недоступна для выбора'),
                                                                       ('NOT_FOR_PLAYERS', 4, u'способность не для игроков'),
                                                                       ('MAXIMUM_ABILITY_POINTS_NUMBER', 5, u'все доступные способности выбраны'),
                                                                       ('ALREADY_MAX_LEVEL', 6, u'способность уже имеет максимальный уровень') ) )

class ChooseHeroAbilityTask(PostponedLogic):

    TYPE = 'choose-hero-ability'

    def __init__(self, hero_id, ability_id, state=CHOOSE_HERO_ABILITY_STATE.UNPROCESSED):
        super(ChooseHeroAbilityTask, self).__init__()
        self.hero_id = hero_id
        self.ability_id = ability_id
        self.state = state

    def serialize(self):
        return { 'hero_id': self.hero_id,
                 'ability_id': self.ability_id,
                 'state': self.state}

    @property
    def error_message(self): return CHOOSE_HERO_ABILITY_STATE._CHOICES[self.state][1]

    def process(self, main_task, storage):

        hero = storage.heroes[self.hero_id]

        if self.ability_id not in ABILITIES:
            self.state = CHOOSE_HERO_ABILITY_STATE.WRONG_ID
            main_task.comment = u'no ability with id "%s"' % self.ability_id
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        choices = hero.abilities.get_for_choose()

        if self.ability_id not in [choice.get_id() for choice in choices]:
            self.state = CHOOSE_HERO_ABILITY_STATE.NOT_IN_CHOICE_LIST
            main_task.comment = u'ability not in choices list: %s' % self.ability_id
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        ability_class = ABILITIES[self.ability_id]

        if not (ability_class.AVAILABILITY.value & ABILITY_AVAILABILITY.FOR_PLAYERS.value):
            self.state = CHOOSE_HERO_ABILITY_STATE.NOT_FOR_PLAYERS
            main_task.comment = u'ability "%s" does not available to players' % self.ability_id
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        if not hero.abilities.can_choose_new_ability:
            self.state = CHOOSE_HERO_ABILITY_STATE.MAXIMUM_ABILITY_POINTS_NUMBER
            main_task.comment = 'has maximum ability points number'
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        if hero.abilities.has(self.ability_id):
            ability = hero.abilities.get(self.ability_id)
            if ability.has_max_level:
                self.state = CHOOSE_HERO_ABILITY_STATE.ALREADY_MAX_LEVEL
                main_task.comment = 'ability has already had max_level'
                return POSTPONED_TASK_LOGIC_RESULT.ERROR
            hero.abilities.increment_level(self.ability_id)
        else:
            hero.abilities.add(self.ability_id)

        storage.save_bundle_data(hero.actions.current_action.bundle_id, update_cache=True)

        self.state = CHOOSE_HERO_ABILITY_STATE.PROCESSED

        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS


CHANGE_HERO_TASK_STATE = create_enum('CHANGE_HERO_TASK_STATE', ( ('UNPROCESSED', 0, u'в очереди'),
                                                                 ('PROCESSED', 1, u'обработана') ) )

class ChangeHeroTask(PostponedLogic):

    TYPE = 'change-hero'

    def __init__(self, hero_id, name, race, gender, state=CHANGE_HERO_TASK_STATE.UNPROCESSED):
        super(ChangeHeroTask, self).__init__()
        self.hero_id = hero_id
        self.name = name if isinstance(name, Noun) else Noun.deserialize(name)
        self.race = race if isinstance(race, rels.Record) else RACE.index_value[race]
        self.gender = gender if isinstance(gender, rels.Record) else GENDER.index_value[gender]
        self.state = state

    def serialize(self):
        return { 'hero_id': self.hero_id,
                 'name': self.name.serialize(),
                 'race': self.race.value,
                 'gender': self.gender.value,
                 'state': self.state}

    @property
    def error_message(self): return CHANGE_HERO_TASK_STATE._CHOICES[self.state][1]

    def process(self, main_task, storage):

        hero = storage.heroes[self.hero_id]

        hero.set_name_forms(self.name)
        hero.gender = self.gender
        hero.race = self.race
        hero.settings_approved = True

        storage.save_bundle_data(hero.actions.current_action.bundle_id, update_cache=True)

        self.state = CHANGE_HERO_TASK_STATE.PROCESSED

        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS


class RESET_HERO_ABILITIES_TASK_STATE(DjangoEnum):
   records = ( ('UNPROCESSED', 0, u'в очереди'),
                ('PROCESSED', 1, u'обработана'),
                ('RESET_TIMEOUT', 2, u'сброс способностей пока не доступен'))

class ResetHeroAbilitiesTask(PostponedLogic):

    TYPE = 'reset-hero-abilities'

    def __init__(self, hero_id, state=RESET_HERO_ABILITIES_TASK_STATE.UNPROCESSED):
        super(ResetHeroAbilitiesTask, self).__init__()
        self.hero_id = hero_id
        self.state = state if isinstance(state, rels.Record) else RESET_HERO_ABILITIES_TASK_STATE(state)

    def serialize(self):
        return { 'hero_id': self.hero_id,
                 'state': self.state.value}

    @property
    def error_message(self): return self.state.text

    def process(self, main_task, storage):

        hero = storage.heroes[self.hero_id]

        if not hero.abilities.can_reset:
            main_task.comment = u'reset timeout'
            self.state = RESET_HERO_ABILITIES_TASK_STATE.RESET_TIMEOUT
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        hero.abilities.reset()

        storage.save_bundle_data(hero.actions.current_action.bundle_id, update_cache=True)

        self.state = RESET_HERO_ABILITIES_TASK_STATE.PROCESSED

        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS


CHOOSE_PREFERENCES_TASK_STATE = create_enum('CHOOSE_PREFERENCES_TASK_STATE', ( ('UNPROCESSED', 0, u'в очереди'),
                                                                               ('PROCESSED', 1, u'обработана'),
                                                                               ('COOLDOWN', 2, u'смена способности недоступна'),
                                                                               ('LOW_LEVEL', 3, u'низкий уровень героя'),
                                                                               ('UNAVAILABLE_PERSON', 4, u'житель недоступен'),
                                                                               ('OUTGAME_PERSON', 5, u'житель выведен из игры'),
                                                                               ('UNSPECIFIED_PREFERENCE', 6, u'предпочтение неуказано'),
                                                                               ('UNKNOWN_ENERGY_REGENERATION_TYPE', 7, u'неизвестный тип восстановления энергии'),
                                                                               ('UNKNOWN_MOB', 8, u'неизвестный тип монстра'),
                                                                               ('LARGE_MOB_LEVEL', 9, u'слишком сильный монстр'),
                                                                               ('UNKNOWN_PLACE', 10, u'неизвестное место'),
                                                                               ('ENEMY_AND_FRIEND', 11, u'житель одновременно и друг и враг'),
                                                                               ('UNKNOWN_PERSON', 12, u'неизвестный житель'),
                                                                               ('UNKNOWN_EQUIPMENT_SLOT', 13, u'неизвестный тип экипировки'),
                                                                               ('UNKNOWN_PREFERENCE', 14, u'неизвестный тип предпочтения'),
                                                                               ('MOB_NOT_IN_GAME', 15, u'этот тип противника выведен из игры'),
                                                                               ('UNKNOWN_RISK_LEVEL', 16, u'неизвестный уровень риска'),
                                                                               ('EMPTY_EQUIPMENT_SLOT', 17, u'пустой слот экипировки')) )


class ChoosePreferencesTask(PostponedLogic):

    TYPE = 'choose-hero-preferences'

    def __init__(self, hero_id, preference_type, preference_id, state=CHOOSE_PREFERENCES_TASK_STATE.UNPROCESSED):
        super(ChoosePreferencesTask, self).__init__()
        self.hero_id = hero_id
        self.preference_type = preference_type if isinstance(preference_type, rels.Record) else PREFERENCE_TYPE(preference_type)
        self.preference_id = preference_id
        self.state = state

    def serialize(self):
        return { 'hero_id': self.hero_id,
                 'preference_type': self.preference_type.value,
                 'preference_id': self.preference_id,
                 'state': self.state }

    @property
    def error_message(self): return CHOOSE_PREFERENCES_TASK_STATE._CHOICES[self.state][1]

    def process_energy_regeneration(self, main_task, hero):

        try:
            energy_regeneration_type = int(self.preference_id) if self.preference_id is not None else None
        except:
            main_task.comment = u'unknown energy regeneration type: %s' % (self.preference_id, )
            self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_ENERGY_REGENERATION_TYPE
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        if energy_regeneration_type is None:
            main_task.comment = u'energy regeneration preference can not be None'
            self.state = CHOOSE_PREFERENCES_TASK_STATE.UNSPECIFIED_PREFERENCE
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        if energy_regeneration_type not in c.ANGEL_ENERGY_REGENERATION_DELAY:
            main_task.comment = u'unknown energy regeneration type: %s' % (energy_regeneration_type, )
            self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_ENERGY_REGENERATION_TYPE
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        hero.preferences.set_energy_regeneration_type(energy_regeneration_type)

        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS


    def process_mob(self, main_task, hero):
        mob_uuid = self.preference_id

        if mob_uuid is not None:

            if  not mobs_storage.has_mob(mob_uuid):
                main_task.comment = u'unknown mob id: %s' % (mob_uuid, )
                self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_MOB
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            mob = mobs_storage.get_by_uuid(mob_uuid)

            if not mob.state.is_ENABLED:
                main_task.comment = u'mob %s not in game' % (mob_uuid, )
                self.state = CHOOSE_PREFERENCES_TASK_STATE.MOB_NOT_IN_GAME
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            if hero.level < mob.level:
                main_task.comment = u'hero level < mob level (%d < %d)' % (hero.level, mob.level)
                self.state = CHOOSE_PREFERENCES_TASK_STATE.LARGE_MOB_LEVEL
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

        hero.preferences.set_mob(mobs_storage.get_by_uuid(mob_uuid))

        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS


    def process_place(self, main_task, hero):
        try:
            place_id = int(self.preference_id) if self.preference_id is not None else None
        except:
            main_task.comment = u'unknown place id: %s' % (self.preference_id, )
            self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_PLACE
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        if place_id is not None:

            if place_id not in places_storage:
                main_task.comment = u'unknown place id: %s' % (place_id, )
                self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_PLACE
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

        hero.preferences.set_place(places_storage.get(place_id))

        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS


    def process_friend(self, main_task, hero):
        try:
            friend_id = int(self.preference_id) if self.preference_id is not None else None
        except:
            main_task.comment = u'unknown person id: %s' % (self.preference_id, )
            self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_PERSON
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        if friend_id is not None:
            if hero.preferences.enemy and hero.preferences.enemy.id == friend_id:
                main_task.comment = u'try set enemy as a friend (%d)' % (friend_id, )
                self.state = CHOOSE_PREFERENCES_TASK_STATE.ENEMY_AND_FRIEND
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            if friend_id not in persons_storage:
                main_task.comment = u'unknown person id: %s' % (friend_id, )
                self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_PERSON
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            if persons_storage[friend_id].out_game:
                main_task.comment = u'person was moved out game: %s' % (friend_id, )
                self.state = CHOOSE_PREFERENCES_TASK_STATE.OUTGAME_PERSON
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

        hero.preferences.set_friend(persons_storage.get(friend_id))

        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS


    def process_enemy(self, main_task, hero):
        try:
            enemy_id = int(self.preference_id) if self.preference_id is not None else None
        except:
            main_task.comment = u'unknown person id: %s' % (self.preference_id, )
            self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_PERSON
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        if enemy_id is not None:
            if hero.preferences.friend and hero.preferences.friend.id == enemy_id:
                main_task.comment = u'try set friend as an enemy (%d)' % (enemy_id, )
                self.state = CHOOSE_PREFERENCES_TASK_STATE.ENEMY_AND_FRIEND
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            if enemy_id not in persons_storage:
                main_task.comment = u'unknown person id: %s' % (enemy_id, )
                self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_PERSON
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            if persons_storage[enemy_id].out_game:
                main_task.comment = u'person was moved out game: %s' % (enemy_id, )
                self.state = CHOOSE_PREFERENCES_TASK_STATE.OUTGAME_PERSON
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

        hero.preferences.set_enemy(persons_storage.get(enemy_id))

        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS


    def process_equipment_slot(self, main_task, hero):

        try:
            equipment_slot = int(self.preference_id) if self.preference_id is not None else None
        except:
            main_task.comment = u'unknown equipment slot: %s' % (self.preference_id, )
            self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_EQUIPMENT_SLOT
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        if equipment_slot is not None:

            if equipment_slot not in EQUIPMENT_SLOT.index_value:
                main_task.comment = u'unknown equipment slot: %s' % (equipment_slot, )
                self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_EQUIPMENT_SLOT
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            equipment_slot = EQUIPMENT_SLOT.index_value[equipment_slot]

        hero.preferences.set_equipment_slot(equipment_slot)

        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS

    def process_favorite_item(self, main_task, hero):

        try:
            equipment_slot = int(self.preference_id) if self.preference_id is not None else None
        except:
            main_task.comment = u'unknown equipment slot: %s' % (self.preference_id, )
            self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_EQUIPMENT_SLOT
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        if equipment_slot is not None:

            if equipment_slot not in EQUIPMENT_SLOT.index_value:
                main_task.comment = u'unknown equipment slot: %s' % (equipment_slot, )
                self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_EQUIPMENT_SLOT
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            equipment_slot = EQUIPMENT_SLOT.index_value[equipment_slot]

            if hero.equipment.get(equipment_slot) is None:
                main_task.comment = u'empty equipment slot for favorite item: %s' % (equipment_slot, )
                self.state = CHOOSE_PREFERENCES_TASK_STATE.EMPTY_EQUIPMENT_SLOT
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

        hero.preferences.set_favorite_item(equipment_slot)

        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS


    def process_risk_level(self, main_task, hero):

        try:
            risk_level = int(self.preference_id) if self.preference_id is not None else None
        except:
            main_task.comment = u'unknown risk level: %s' % (self.preference_id, )
            self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_RISK_LEVEL
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        if risk_level is not None:

            if risk_level not in RISK_LEVEL.index_value:
                main_task.comment = u'unknown risk level: %s' % (risk_level, )
                self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_RISK_LEVEL
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            risk_level = RISK_LEVEL.index_value[risk_level]

        hero.preferences.set_risk_level(risk_level)

        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS

    def process(self, main_task, storage):

        hero = storage.heroes[self.hero_id]

        account = AccountPrototype.get_by_id(hero.account_id)

        if not hero.preferences.can_update(self.preference_type, datetime.datetime.now()):
            main_task.comment = u'blocked since time delay'
            self.state = CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        purchased = False
        if hasattr(self.preference_type, 'purchase_type'):
            if self.preference_type.purchase_type in account.permanent_purchases:
                purchased = True

        if not purchased and hero.level < self.preference_type.level_required:
            main_task.comment = u'hero level < required level (%d < %d)' % (hero.level, self.preference_type.level_required)
            self.state = CHOOSE_PREFERENCES_TASK_STATE.LOW_LEVEL
            return POSTPONED_TASK_LOGIC_RESULT.ERROR


        if self.preference_type.is_ENERGY_REGENERATION_TYPE:
            result = self.process_energy_regeneration(main_task, hero)

        elif self.preference_type.is_MOB:
            result = self.process_mob(main_task, hero)

        elif self.preference_type.is_PLACE:
            result = self.process_place(main_task, hero)

        elif self.preference_type.is_FRIEND:
            result = self.process_friend(main_task, hero)

        elif self.preference_type.is_ENEMY:
            result = self.process_enemy(main_task, hero)

        elif self.preference_type.is_EQUIPMENT_SLOT:
            result = self.process_equipment_slot(main_task, hero)

        elif self.preference_type.is_RISK_LEVEL:
            result = self.process_risk_level(main_task, hero)

        elif self.preference_type.is_FAVORITE_ITEM:
            result = self.process_favorite_item(main_task, hero)

        else:
            main_task.comment = u'unknown preference type: %s' % (self.preference_type, )
            self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_PREFERENCE
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        if result == POSTPONED_TASK_LOGIC_RESULT.SUCCESS:

            storage.save_bundle_data(hero.actions.current_action.bundle_id, update_cache=True)

            self.state = CHOOSE_PREFERENCES_TASK_STATE.PROCESSED

        return result
