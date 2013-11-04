# coding: utf-8

from the_tale.common.utils.enum import create_enum

from the_tale.game.pvp.prototypes import Battle1x1Prototype

from the_tale.game.workers.environment import workers_environment

from the_tale.game.abilities.prototypes import AbilityPrototype
from the_tale.game.abilities.relations import ABILITY_TYPE

ABILITY_TASK_STEP = create_enum('ABILITY_TASK_STEP', (('ERROR', 0, u'ошибка'),
                                                      ('LOGIC', 1, u'логика'),
                                                      ('PVP_BALANCER', 2, u'pvp балансировщик'),
                                                      ('SUCCESS', 3, u'обработка завершена') ))

class ArenaPvP1x1LeaveQueue(AbilityPrototype):
    TYPE = ABILITY_TYPE.ARENA_PVP_1x1_LEAVE_QUEUE

    def use(self, data, step, main_task_id, storage, pvp_balancer, **kwargs):

        if step is None:

            hero = storage.heroes[data['hero_id']]

            battle = Battle1x1Prototype.get_by_account_id(hero.account_id)

            if battle is None:
                return True, None, ()

            hero.add_message('angel_ability_arena_pvp_1x1_leave_queue', hero=hero)

            return None, ABILITY_TASK_STEP.PVP_BALANCER, ((lambda: workers_environment.pvp_balancer.cmd_logic_task(hero.account_id, main_task_id)), )

        elif step == ABILITY_TASK_STEP.PVP_BALANCER:

            pvp_balancer.leave_arena_queue(data['hero_id'])

            return True, ABILITY_TASK_STEP.SUCCESS, ()
