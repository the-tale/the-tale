# coding: utf-8
import random

from dext.utils.decorators import nested_commit_on_success

from textgen.words import Fake

from common.postponed_tasks import postponed_task, POSTPONED_TASK_LOGIC_RESULT
from common.utils.enum import create_enum

from game.heroes.prototypes import HeroPrototype

from game.pvp.prototypes import Battle1x1Prototype
from game.pvp.abilities import ABILITIES

SAY_IN_HERO_LOG_TASK_STATE = create_enum('SAY_IN_HERO_LOG_TASK_STATE', ( ('UNPROCESSED', 0, u'в очереди'),
                                                                         ('ACCOUNT_HERO_NOT_FOUND', 1, u'герой не найден'),
                                                                         ('PROCESSED', 2, u'обработана') ) )



@postponed_task
class SayInBattleLogTask(object):

    TYPE = 'say-in-hero-log'

    def __init__(self, battle_id, text, state=SAY_IN_HERO_LOG_TASK_STATE.UNPROCESSED):
        self.battle_id = battle_id
        self.text = text
        self.state = state

    def __eq__(self, other):
        return (self.battle_id == other.battle_id and
                self.text == other.text and
                self.state == other.state )

    def serialize(self):
        return { 'battle_id': self.battle_id,
                 'text': self.text,
                 'state': self.state}

    @classmethod
    def deserialize(cls, data):
        return cls(**data)

    @property
    def uuid(self): return self.battle_id

    @property
    def response_data(self): return {}

    @property
    def error_message(self): return SAY_IN_HERO_LOG_TASK_STATE._CHOICES[self.state][1]

    def process(self, main_task, storage):

        battle = Battle1x1Prototype.get_by_id(self.battle_id)

        account_hero = storage.accounts_to_heroes.get(battle.account_id)
        enemy_hero = storage.accounts_to_heroes.get(battle.enemy_id)

        if account_hero is None:
            self.state = SAY_IN_HERO_LOG_TASK_STATE.ACCOUNT_HERO_NOT_FOUND
            main_task.comment = 'hero for account %d not found' % battle.account_id
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        account_hero.add_message('pvp_say', text=Fake(self.text))

        if enemy_hero is not None:
            enemy_hero.add_message('pvp_say', text=Fake(self.text))

        with nested_commit_on_success():
            storage.save_account_data(battle.account_id, update_cache=True)

            if enemy_hero is not None:
                storage.save_account_data(battle.enemy_id, update_cache=True)

        self.state = SAY_IN_HERO_LOG_TASK_STATE.PROCESSED
        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS



ACCEPT_BATTLE_TASK_STATE = create_enum('ACCEPT_BATTLE_TASK_STATE', ( ('UNPROCESSED', 0, u'в очереди'),
                                                                     ('BATTLE_NOT_FOUND', 1, u'битва не найдена'),
                                                                     ('WRONG_ACCEPTED_BATTLE_STATE', 2, u'герой не успел принять вызов'),
                                                                     ('WRONG_INITIATOR_BATTLE_STATE', 3, u'герой уже находится в сражении'),
                                                                     ('NOT_IN_QUEUE', 4, u'битва не находится в очереди балансировщика'),
                                                                     ('PROCESSED', 5, u'обработана') ) )

@postponed_task
class AcceptBattleTask(object):

    TYPE = 'accept-battle-task'

    def __init__(self, battle_id, accept_initiator_id, state=ACCEPT_BATTLE_TASK_STATE.UNPROCESSED):
        self.battle_id = battle_id
        self.accept_initiator_id = accept_initiator_id
        self.state = state

    def __eq__(self, other):
        return (self.battle_id == other.battle_id and
                self.accept_initiator_id == other.accept_initiator_id and
                self.state == other.state )

    def serialize(self):
        return { 'battle_id': self.battle_id,
                 'accept_initiator_id': self.accept_initiator_id,
                 'state': self.state}

    @classmethod
    def deserialize(cls, data):
        return cls(**data)

    @property
    def uuid(self): return self.accept_initiator_id

    @property
    def response_data(self): return {}

    @property
    def error_message(self): return ACCEPT_BATTLE_TASK_STATE._CHOICES[self.state][1]

    def process(self, main_task, pvp_balancer):

        accepted_battle = Battle1x1Prototype.get_by_id(self.battle_id)

        if accepted_battle is None:
            self.state = ACCEPT_BATTLE_TASK_STATE.BATTLE_NOT_FOUND
            main_task.comment = 'battle %d not found' % self.battle_id
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        if not accepted_battle.state._is_WAITING:
            self.state = ACCEPT_BATTLE_TASK_STATE.WRONG_ACCEPTED_BATTLE_STATE
            main_task.comment = 'battle %d has wrong state %s' % (self.battle_id, accepted_battle.state.value)
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        if not accepted_battle.account_id in pvp_balancer.arena_queue:
            self.state = ACCEPT_BATTLE_TASK_STATE.NOT_IN_QUEUE
            main_task.comment = 'battle %d not in queue' % self.battle_id
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        initiator_battle = Battle1x1Prototype.get_by_account_id(self.accept_initiator_id)

        if initiator_battle is not None and not initiator_battle.state._is_WAITING:
            self.state = ACCEPT_BATTLE_TASK_STATE.WRONG_INITIATOR_BATTLE_STATE
            main_task.comment = 'initiator battle %d has wrong state %s' % (initiator_battle.id, initiator_battle.state.value)
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        if self.accept_initiator_id not in pvp_balancer.arena_queue:
            pvp_balancer.add_to_arena_queue(HeroPrototype.get_by_account_id(self.accept_initiator_id).id)

        pvp_balancer.force_battle(accepted_battle.account_id, self.accept_initiator_id)

        self.state = ACCEPT_BATTLE_TASK_STATE.PROCESSED
        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS




USE_PVP_ABILITY_TASK_STATE = create_enum('USE_PVP_ABILITY_TASK_STATE', ( ('UNPROCESSED', 0, u'в очереди'),
                                                                         ('HERO_NOT_FOUND', 1, u'герой не найден'),
                                                                         ('WRONG_ABILITY_ID', 2, u'неизвестная способность'),
                                                                         ('NO_ENERGY', 3, u'недостаточно энергии'),
                                                                         ('PROCESSED', 4, u'обработана') ) )

@postponed_task
class UsePvPAbilityTask(object):

    TYPE = 'use-pvp-ability'

    def __init__(self, battle_id, account_id, ability_id, state=USE_PVP_ABILITY_TASK_STATE.UNPROCESSED):
        self.battle_id = battle_id
        self.account_id = account_id
        self.ability_id = ability_id
        self.state = state

    def __eq__(self, other):
        return (self.battle_id == other.battle_id and
                self.account_id == other.account_id and
                self.ability_id == other.ability_id and
                self.state == other.state )

    def serialize(self):
        return { 'battle_id': self.battle_id,
                 'account_id': self.account_id,
                 'ability_id': self.ability_id,
                 'state': self.state}

    @classmethod
    def deserialize(cls, data):
        return cls(**data)

    @property
    def uuid(self): return self.account_id

    @property
    def response_data(self): return {}

    @property
    def error_message(self): return USE_PVP_ABILITY_TASK_STATE._CHOICES[self.state][1]

    def process(self, main_task, storage):

        battle = Battle1x1Prototype.get_by_id(self.battle_id)

        hero = storage.accounts_to_heroes.get(self.account_id)
        enemy_hero = storage.accounts_to_heroes.get(battle.enemy_id)

        if hero is None:
            self.state = USE_PVP_ABILITY_TASK_STATE.HERO_NOT_FOUND
            main_task.comment = 'hero for account %d not found' % self.account_id
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        pvp_ability_class = ABILITIES.get(self.ability_id)

        if pvp_ability_class is None:
            self.state = USE_PVP_ABILITY_TASK_STATE.WRONG_ABILITY_ID
            main_task.comment = 'unknown ability id "%s"' % self.ability_id
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        pvp_ability = pvp_ability_class(hero=hero, enemy=enemy_hero)

        if not pvp_ability.has_resources:
            self.state = USE_PVP_ABILITY_TASK_STATE.NO_ENERGY
            main_task.comment = 'no resources for ability %s' % self.ability_id
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        if random.uniform(0, 1.0) < pvp_ability.probability:
            pvp_ability.apply()
            hero.add_message('pvp_use_ability_%s' % pvp_ability.str_id.lower(), hero=hero)
            enemy_hero.add_message('pvp_use_ability_%s' % pvp_ability.str_id.lower(), hero=hero)
        else:
            hero.add_message('pvp_miss_ability_%s' % pvp_ability.str_id.lower(), hero=hero)
            enemy_hero.add_message('pvp_miss_ability_%s' % pvp_ability.str_id.lower(), hero=hero)

        with nested_commit_on_success():
            storage.save_account_data(battle.account_id, update_cache=True)
            storage.save_account_data(battle.enemy_id, update_cache=True)

        self.state = USE_PVP_ABILITY_TASK_STATE.PROCESSED
        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS
