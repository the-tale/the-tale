# coding: utf-8
from dext.utils.decorators import nested_commit_on_success

from textgen.words import Fake

from common.postponed_tasks import PostponedLogic, POSTPONED_TASK_LOGIC_RESULT
from common.utils.enum import create_enum

from game.pvp.prototypes import Battle1x1Prototype
from game.pvp.abilities import ABILITIES

SAY_IN_HERO_LOG_TASK_STATE = create_enum('SAY_IN_HERO_LOG_TASK_STATE', ( ('UNPROCESSED', 0, u'в очереди'),
                                                                         ('ACCOUNT_HERO_NOT_FOUND', 1, u'герой не найден'),
                                                                         ('PROCESSED', 2, u'обработана') ) )



class SayInBattleLogTask(PostponedLogic):

    TYPE = 'say-in-hero-log'

    def __init__(self, battle_id, text, state=SAY_IN_HERO_LOG_TASK_STATE.UNPROCESSED):
        super(SayInBattleLogTask, self).__init__()
        self.battle_id = battle_id
        self.text = text
        self.state = state

    def serialize(self):
        return { 'battle_id': self.battle_id,
                 'text': self.text,
                 'state': self.state}

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



USE_PVP_ABILITY_TASK_STATE = create_enum('USE_PVP_ABILITY_TASK_STATE', ( ('UNPROCESSED', 0, u'в очереди'),
                                                                         ('HERO_NOT_FOUND', 1, u'герой не найден'),
                                                                         ('WRONG_ABILITY_ID', 2, u'неизвестная способность'),
                                                                         ('NO_ENERGY', 3, u'недостаточно энергии'),
                                                                         ('PROCESSED', 4, u'обработана'),
                                                                         ('BATTLE_FINISHED', 5, u'битва уже закончена')) )

class UsePvPAbilityTask(PostponedLogic):

    TYPE = 'use-pvp-ability'

    def __init__(self, battle_id, account_id, ability_id, state=USE_PVP_ABILITY_TASK_STATE.UNPROCESSED):
        super(UsePvPAbilityTask, self).__init__()
        self.battle_id = battle_id
        self.account_id = account_id
        self.ability_id = ability_id
        self.state = state

    def serialize(self):
        return { 'battle_id': self.battle_id,
                 'account_id': self.account_id,
                 'ability_id': self.ability_id,
                 'state': self.state}

    @property
    def error_message(self): return USE_PVP_ABILITY_TASK_STATE._CHOICES[self.state][1]

    def process(self, main_task, storage):

        battle = Battle1x1Prototype.get_by_id(self.battle_id)

        if battle is None: # battle ended
            self.state = USE_PVP_ABILITY_TASK_STATE.BATTLE_FINISHED
            main_task.comment = 'battle finished'
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

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

        pvp_ability.use()

        with nested_commit_on_success():
            storage.save_account_data(battle.account_id, update_cache=True)
            storage.save_account_data(battle.enemy_id, update_cache=True)

        self.state = USE_PVP_ABILITY_TASK_STATE.PROCESSED
        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS
