# coding: utf-8

from the_tale.common.utils.enum import create_enum

from the_tale.game.workers.environment import workers_environment

from the_tale.game.abilities.prototypes import AbilityPrototype
from the_tale.game.abilities.relations import ABILITY_TYPE, ABILITY_RESULT

ABILITY_TASK_STEP = create_enum('ABILITY_TASK_STEP', (('ERROR', 0, u'ошибка'),
                                                      ('LOGIC', 1, u'логика'),
                                                      ('PVP_BALANCER', 2, u'pvp балансировщик'),
                                                      ('SUCCESS', 3, u'обработка завершена') ))


class ArenaPvP1x1(AbilityPrototype):
    TYPE = ABILITY_TYPE.ARENA_PVP_1x1

    def use(self, data, step, main_task_id, storage, pvp_balancer, **kwargs):

        if step is None:

            hero = storage.heroes[data['hero_id']]

            if not hero.can_participate_in_pvp:
                return ABILITY_RESULT.FAILED, ABILITY_TASK_STEP.ERROR, ()

            hero.add_message('angel_ability_arena_pvp_1x1', hero=hero)

            return ABILITY_RESULT.CONTINUE, ABILITY_TASK_STEP.PVP_BALANCER, ((lambda: workers_environment.pvp_balancer.cmd_logic_task(hero.account_id, main_task_id)), )

        elif step == ABILITY_TASK_STEP.PVP_BALANCER:

            pvp_balancer.add_to_arena_queue(data['hero_id'])

            return ABILITY_RESULT.SUCCESSED, ABILITY_TASK_STEP.SUCCESS, ()
