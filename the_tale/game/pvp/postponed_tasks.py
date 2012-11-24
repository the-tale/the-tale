# coding: utf-8

from dext.utils.decorators import nested_commit_on_success

from textgen.words import Fake

from common.postponed_tasks import postponed_task
from common.utils.enum import create_enum

from game.pvp.prototypes import Battle1x1Prototype

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
    def error_message(self): return SAY_IN_HERO_LOG_TASK_STATE.CHOICES[self.state][1]

    @nested_commit_on_success
    def process(self, main_task, storage):

        battle = Battle1x1Prototype.get_by_id(self.battle_id)

        account_hero = storage.accounts_to_heroes.get(battle.account_id)
        enemy_hero = storage.accounts_to_heroes.get(battle.enemy_id)

        if account_hero is None:
            self.state = SAY_IN_HERO_LOG_TASK_STATE.ACCOUNT_HERO_NOT_FOUND
            main_task.comment = 'hero for account %d not found' % battle.account_id
            return False

        account_hero.add_message('pvp_say', text=Fake(self.text))

        if enemy_hero is not None:
            enemy_hero.add_message('pvp_say', text=Fake(self.text))

        with nested_commit_on_success():
            storage.save_account_data(battle.account_id)

            if enemy_hero is not None:
                storage.save_account_data(battle.enemy_id)

        self.state = SAY_IN_HERO_LOG_TASK_STATE.PROCESSED
        return True
