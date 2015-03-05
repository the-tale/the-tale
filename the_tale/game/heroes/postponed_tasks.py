# coding: utf-8
import datetime

import rels
from rels.django import DjangoEnum

from utg import words as utg_words

from the_tale.common.postponed_tasks import PostponedLogic, POSTPONED_TASK_LOGIC_RESULT

from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.relations import GENDER, RACE
from the_tale.game.balance import constants as c

from the_tale.game.map.places.storage import places_storage
from the_tale.game.mobs.storage import mobs_storage
from the_tale.game.persons.storage import persons_storage

from the_tale.game import relations as game_relations

from the_tale.game.heroes.habilities import ABILITIES, ABILITY_AVAILABILITY
from the_tale.game.heroes import relations


class CHOOSE_HERO_ABILITY_STATE(DjangoEnum):
    records = ( ('UNPROCESSED', 0, u'в очереди'),
                ('PROCESSED', 1, u'обработана'),
                ('WRONG_ID', 2, u'неверный идентификатор способности'),
                ('NOT_IN_CHOICE_LIST', 3, u'способность недоступна для выбора'),
                ('NOT_FOR_PLAYERS', 4, u'способность не для игроков'),
                ('MAXIMUM_ABILITY_POINTS_NUMBER', 5, u'все доступные способности выбраны'),
                ('ALREADY_MAX_LEVEL', 6, u'способность уже имеет максимальный уровень') )

class ChooseHeroAbilityTask(PostponedLogic):

    TYPE = 'choose-hero-ability'

    def __init__(self, hero_id, ability_id, state=CHOOSE_HERO_ABILITY_STATE.UNPROCESSED):
        super(ChooseHeroAbilityTask, self).__init__()
        self.hero_id = hero_id
        self.ability_id = ability_id
        self.state = state if isinstance(state, rels.Record) else CHOOSE_HERO_ABILITY_STATE(state)

    def serialize(self):
        return { 'hero_id': self.hero_id,
                 'ability_id': self.ability_id,
                 'state': self.state.value}

    @property
    def error_message(self): return self.state.text

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

        storage.save_bundle_data(hero.actions.current_action.bundle_id)

        self.state = CHOOSE_HERO_ABILITY_STATE.PROCESSED

        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS


class CHANGE_HERO_TASK_STATE(DjangoEnum):
    records = ( ('UNPROCESSED', 0, u'в очереди'),
                ('PROCESSED', 1, u'обработана') )

class ChangeHeroTask(PostponedLogic):

    TYPE = 'change-hero'

    def __init__(self, hero_id, name, race, gender, state=CHANGE_HERO_TASK_STATE.UNPROCESSED):
        super(ChangeHeroTask, self).__init__()
        self.hero_id = hero_id
        self.name = name if isinstance(name, utg_words.Word) else utg_words.Word.deserialize(name)
        self.race = race if isinstance(race, rels.Record) else RACE.index_value[race]
        self.gender = gender if isinstance(gender, rels.Record) else GENDER.index_value[gender]
        self.state = state if isinstance(state, rels.Record) else CHANGE_HERO_TASK_STATE(state)

    def serialize(self):
        return { 'hero_id': self.hero_id,
                 'name': self.name.serialize(),
                 'race': self.race.value,
                 'gender': self.gender.value,
                 'state': self.state.value}

    @property
    def error_message(self): return self.state.text

    def process(self, main_task, storage):

        hero = storage.heroes[self.hero_id]

        hero.set_utg_name(self.name)
        hero.gender = self.gender
        hero.race = self.race
        hero.settings_approved = True

        storage.save_bundle_data(hero.actions.current_action.bundle_id)

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

        storage.save_bundle_data(hero.actions.current_action.bundle_id)

        self.state = RESET_HERO_ABILITIES_TASK_STATE.PROCESSED

        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS


class CHOOSE_PREFERENCES_TASK_STATE(DjangoEnum):
    records = ( ('UNPROCESSED', 0, u'в очереди'),
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
                ('EMPTY_EQUIPMENT_SLOT', 17, u'пустой слот экипировки'),
                ('UNKNOWN_ARCHETYPE', 18, u'неизвестный архетип'),
                ('UNKNOWN_COMPANION_DEDICATION', 19, u'неизвестное отношение со спутником'),
                ('UNKNOWN_COMPANION_EMPATHY', 20, u'неизвестная форма эмпатии'))


class ChoosePreferencesTask(PostponedLogic):

    TYPE = 'choose-hero-preferences'

    def __init__(self, hero_id, preference_type, preference_id, state=CHOOSE_PREFERENCES_TASK_STATE.UNPROCESSED):
        super(ChoosePreferencesTask, self).__init__()
        self.hero_id = hero_id
        self.preference_type = preference_type if isinstance(preference_type, rels.Record) else relations.PREFERENCE_TYPE(preference_type)
        self.preference_id = preference_id
        self.state = state if isinstance(state, rels.Record) else CHOOSE_PREFERENCES_TASK_STATE(state)

    def serialize(self):
        return { 'hero_id': self.hero_id,
                 'preference_type': self.preference_type.value,
                 'preference_id': self.preference_id,
                 'state': self.state.value }

    @property
    def error_message(self): return self.state.text

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

            if equipment_slot not in relations.EQUIPMENT_SLOT.index_value:
                main_task.comment = u'unknown equipment slot: %s' % (equipment_slot, )
                self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_EQUIPMENT_SLOT
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            equipment_slot = relations.EQUIPMENT_SLOT.index_value[equipment_slot]

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

            if equipment_slot not in relations.EQUIPMENT_SLOT.index_value:
                main_task.comment = u'unknown equipment slot: %s' % (equipment_slot, )
                self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_EQUIPMENT_SLOT
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            equipment_slot = relations.EQUIPMENT_SLOT.index_value[equipment_slot]

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

            if risk_level not in relations.RISK_LEVEL.index_value:
                main_task.comment = u'unknown risk level: %s' % (risk_level, )
                self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_RISK_LEVEL
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            risk_level = relations.RISK_LEVEL.index_value[risk_level]

        hero.preferences.set_risk_level(risk_level)

        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS


    def process_archetype(self, main_task, hero):

        try:
            archetype = int(self.preference_id) if self.preference_id is not None else None
        except:
            main_task.comment = u'unknown archetype: %s' % (self.preference_id, )
            self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_ARCHETYPE
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        if archetype is not None:

            if archetype not in game_relations.ARCHETYPE.index_value:
                main_task.comment = u'unknown archetype: %s' % (archetype, )
                self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_ARCHETYPE
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            archetype = game_relations.ARCHETYPE.index_value[archetype]

        hero.preferences.set_archetype(archetype)

        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS


    def process_companion_dedication(self, main_task, hero):

        try:
            companion_dedication = int(self.preference_id) if self.preference_id is not None else None
        except:
            main_task.comment = u'unknown companion dedication: %s' % (self.preference_id, )
            self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_COMPANION_DEDICATION
            return POSTPONED_TASK_LOGIC_RESULT.ERROR


        if companion_dedication is not None:

            if companion_dedication not in relations.COMPANION_DEDICATION.index_value:
                main_task.comment = u'unknown companion dedication: %s' % (companion_dedication, )
                self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_COMPANION_DEDICATION
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            companion_dedication = relations.COMPANION_DEDICATION.index_value[companion_dedication]

        hero.preferences.set_companion_dedication(companion_dedication)

        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS


    def process_companion_empathy(self, main_task, hero):

        try:
            companion_empathy = int(self.preference_id) if self.preference_id is not None else None
        except:
            main_task.comment = u'unknown companion empathy: %s' % (self.preference_id, )
            self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_COMPANION_EMPATHY
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        if companion_empathy is not None:

            if companion_empathy not in relations.COMPANION_EMPATHY.index_value:
                main_task.comment = u'unknown companion empathy: %s' % (companion_empathy, )
                self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_COMPANION_EMPATHY
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            companion_empathy = relations.COMPANION_EMPATHY.index_value[companion_empathy]

        hero.preferences.set_companion_empathy(companion_empathy)

        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS


    def process(self, main_task, storage):

        hero = storage.heroes[self.hero_id]

        account = AccountPrototype.get_by_id(hero.account_id)

        if not hero.preferences.can_update(self.preference_type, datetime.datetime.now()):
            main_task.comment = u'blocked since time delay'
            self.state = CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        if not hero.preferences.is_available(self.preference_type, account):
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

        elif self.preference_type.is_ARCHETYPE:
            result = self.process_archetype(main_task, hero)

        elif self.preference_type.is_COMPANION_DEDICATION:
            result = self.process_companion_dedication(main_task, hero)

        elif self.preference_type.is_COMPANION_EMPATHY:
            result = self.process_companion_empathy(main_task, hero)

        else:
            main_task.comment = u'unknown preference type: %s' % (self.preference_type, )
            self.state = CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_PREFERENCE
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        if result == POSTPONED_TASK_LOGIC_RESULT.SUCCESS:

            storage.save_bundle_data(hero.actions.current_action.bundle_id)

            self.state = CHOOSE_PREFERENCES_TASK_STATE.PROCESSED

        return result




class GET_CARD_TASK_STATE(DjangoEnum):
   records = ( ('UNPROCESSED', 0, u'в очереди'),
               ('PROCESSED', 1, u'обработана'),
               ('CAN_NOT_GET', 2, u'Вы пока не можете взять новую карту'))

class GetCardTask(PostponedLogic):

    TYPE = 'get-card'

    MESSAGE = u'''
<span class="%(rarity)s-card-label">%(name)s</span><br/><br/>

<blockquote>%(description)s</blockquote>
'''


    def __init__(self, hero_id, state=GET_CARD_TASK_STATE.UNPROCESSED, message=None, card_ui_info=None):
        super(GetCardTask, self).__init__()
        self.hero_id = hero_id
        self.state = state if isinstance(state, rels.Record) else GET_CARD_TASK_STATE(state)
        self.message = message
        self.card_ui_info = card_ui_info

    def serialize(self):
        return { 'hero_id': self.hero_id,
                 'state': self.state.value,
                 'message': self.message,
                 'card_ui_info': self.card_ui_info}

    @property
    def error_message(self): return self.state.text

    def create_message(self, card):
        return self.MESSAGE % {'name': card.name[0].upper() + card.name[1:],
                               'description': card.effect.DESCRIPTION,
                               'rarity': card.type.rarity.name.lower()}
    @property
    def processed_data(self):
        return {'message': self.message,
                'card': self.card_ui_info }

    def process(self, main_task, storage):

        hero = storage.heroes[self.hero_id]

        if hero.cards.help_count < c.CARDS_HELP_COUNT_TO_NEW_CARD:
            main_task.comment = u'can not get new card'
            self.state = GET_CARD_TASK_STATE.CAN_NOT_GET
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        card = hero.cards.get_new_card()

        self.message = self.create_message(card)

        hero.cards.change_help_count(-c.CARDS_HELP_COUNT_TO_NEW_CARD)

        self.card_ui_info = card.ui_info()

        storage.save_bundle_data(hero.actions.current_action.bundle_id)

        self.state = GET_CARD_TASK_STATE.PROCESSED

        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS



class COMBINE_CARDS_STATE(DjangoEnum):
   records = ( ('UNPROCESSED', 0, u'в очереди'),
               ('PROCESSED', 1, u'обработана'),
               ('CAN_NOT_COMBINE', 2, u'не удалось объединить карты'))

class CombineCardsTask(PostponedLogic):

    TYPE = 'combine-cards'

    MESSAGE = u'''
<p>Вы получаете новую карту: <span class="%(rarity)s-card-label">%(name)s</span><br/><br/></p>

<blockquote>%(description)s</blockquote>
'''


    def __init__(self, hero_id, cards=[], state=GET_CARD_TASK_STATE.UNPROCESSED, message=None, card_ui_info=None):
        super(CombineCardsTask, self).__init__()
        self.hero_id = hero_id
        self.cards = cards
        self.message = message
        self.state = state if isinstance(state, rels.Record) else GET_CARD_TASK_STATE(state)
        self.card_ui_info = card_ui_info

    def serialize(self):
        return { 'hero_id': self.hero_id,
                 'state': self.state.value,
                 'cards': self.cards,
                 'message': self.message,
                 'card_ui_info': self.card_ui_info}

    @property
    def error_message(self): return self.state.text

    def create_message(self, card):
        return self.MESSAGE % {'name': card.name[0].upper() + card.name[1:],
                               'description': card.effect.DESCRIPTION,
                               'rarity': card.type.rarity.name.lower()}

    @property
    def processed_data(self):
        return {'message': self.message,
                'card_ui_info': self.card_ui_info}

    def process(self, main_task, storage):

        hero = storage.heroes[self.hero_id]

        can_combine_cards = hero.cards.can_combine_cards(self.cards)

        if not can_combine_cards.is_ALLOWED:
            main_task.comment = u'can not get combine cards (status: %r)' % can_combine_cards
            self.state = COMBINE_CARDS_STATE.CAN_NOT_COMBINE
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        card = hero.cards.combine_cards(self.cards)

        self.message = self.create_message(card)

        hero.statistics.change_cards_combined(len(self.cards))

        self.card_ui_info = card.ui_info()

        storage.save_bundle_data(hero.actions.current_action.bundle_id)

        self.state = COMBINE_CARDS_STATE.PROCESSED

        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS
