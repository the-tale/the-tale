# coding: utf-8

import rels

from the_tale.common.postponed_tasks import PostponedLogic, POSTPONED_TASK_LOGIC_RESULT
from the_tale.common.utils.enum import create_enum

from the_tale.game.abilities.relations import ABILITY_TYPE


ABILITY_TASK_STATE = create_enum('ABILITY_TASK_STATE', (('UNPROCESSED', 0, u'в очереди'),
                                                        ('PROCESSED', 1, u'обработана'),
                                                        ('NO_ENERGY', 2, u'не хватает энергии'),
                                                        ('COOLDOWN', 3, u'способность не готова'),
                                                        ('CAN_NOT_PROCESS', 4, u'способность нельзя применить'),
                                                        ('BANNED', 5, u'нет прав на проведение операции')))

class UseAbilityTask(PostponedLogic):

    TYPE = 'use-ability'

    def __init__(self, ability_type, hero_id, data, step=None, state=ABILITY_TASK_STATE.UNPROCESSED):
        super(UseAbilityTask, self).__init__()
        self.ability_type = ability_type if isinstance(ability_type, rels.Record) else ABILITY_TYPE(ability_type)
        self.hero_id = hero_id
        self.data = data
        self.state = state
        self.step = step

    def serialize(self):
        return { 'ability_type': self.ability_type.value,
                 'hero_id': self.hero_id,
                 'data': self.data,
                 'state': self.state,
                 'step': self.step}

    @property
    def error_message(self): return ABILITY_TASK_STATE._CHOICES[self.state][1]

    def process(self, main_task, storage=None, pvp_balancer=None, highlevel=None): # pylint: disable=R0911
        from the_tale.game.abilities.deck import ABILITIES
        ability = ABILITIES[self.ability_type]()

        if self.step is None:

            hero = storage.heroes[self.hero_id]

            if hero.is_banned:
                main_task.comment = 'hero is banned'
                self.state = ABILITY_TASK_STATE.BANNED
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            energy = hero.energy_full

            if energy < ability.TYPE.cost:
                main_task.comment = 'energy < ability.COST'
                self.state = ABILITY_TASK_STATE.NO_ENERGY
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            result, self.step, postsave_actions = ability.use(data=self.data,
                                                              step=self.step,
                                                              main_task_id=main_task.id,
                                                              storage=storage,
                                                              pvp_balancer=pvp_balancer,
                                                              highlevel=highlevel)

            main_task.extend_postsave_actions(postsave_actions)

            if result.is_IGNORE:
                main_task.comment = 'result is None: do nothing'
                self.state = ABILITY_TASK_STATE.PROCESSED
                return POSTPONED_TASK_LOGIC_RESULT.SUCCESS

            if result.is_FAILED:
                main_task.comment = 'result is False'
                self.state = ABILITY_TASK_STATE.CAN_NOT_PROCESS
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            hero.change_energy(-ability.TYPE.cost)

            if result.is_SUCCESSED:
                self.state = ABILITY_TASK_STATE.PROCESSED
                return POSTPONED_TASK_LOGIC_RESULT.SUCCESS

            if result.is_CONTINUE:
                return POSTPONED_TASK_LOGIC_RESULT.CONTINUE

            main_task.comment = u'unknown result %r' % result
            self.state = ABILITY_TASK_STATE.CAN_NOT_PROCESS
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        else:
            result, self.step, postsave_actions = ability.use(data=self.data,
                                                              step=self.step,
                                                              main_task_id=main_task.id,
                                                              storage=storage,
                                                              pvp_balancer=pvp_balancer,
                                                              highlevel=highlevel)

            main_task.extend_postsave_actions(postsave_actions)

            if result.is_IGNORE:
                main_task.comment = 'result is None: do nothing'
                self.state = ABILITY_TASK_STATE.PROCESSED
                return POSTPONED_TASK_LOGIC_RESULT.SUCCESS


            if result.is_FAILED:
                main_task.comment = 'result is False on step %r' %  (self.step,)
                self.state = ABILITY_TASK_STATE.CAN_NOT_PROCESS
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            if result.is_SUCCESSED:
                self.state = ABILITY_TASK_STATE.PROCESSED
                return POSTPONED_TASK_LOGIC_RESULT.SUCCESS

            if result.is_CONTINUE:
                return POSTPONED_TASK_LOGIC_RESULT.CONTINUE

            main_task.comment = u'unknown result %r' % result
            self.state = ABILITY_TASK_STATE.CAN_NOT_PROCESS
            return POSTPONED_TASK_LOGIC_RESULT.ERROR
