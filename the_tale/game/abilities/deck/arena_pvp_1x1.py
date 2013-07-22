# coding: utf-8

from common.utils.enum import create_enum

from game.workers.environment import workers_environment

from game.abilities.prototypes import AbilityPrototype


ABILITY_TASK_STEP = create_enum('ABILITY_TASK_STEP', (('ERROR', 0, u'ошибка'),
                                                      ('LOGIC', 1, u'логика'),
                                                      ('PVP_BALANCER', 2, u'pvp балансировщик'),
                                                      ('SUCCESS', 3, u'обработка завершена') ))


class ArenaPvP1x1(AbilityPrototype):

    COST = 1
    NAME = u'Отправить на арену'
    DESCRIPTION = u'Отправить героя на гладиаторскую арену'

    def use(self, data, step, main_task_id, storage, pvp_balancer, **kwargs):

        if step is None:

            hero = storage.heroes[data['hero_id']]

            if not hero.can_participate_in_pvp:
                return False, ABILITY_TASK_STEP.ERROR, ()

            hero.add_message('angel_ability_arena_pvp_1x1', hero=hero)

            return None, ABILITY_TASK_STEP.PVP_BALANCER, ((lambda: workers_environment.pvp_balancer.cmd_logic_task(hero.account_id, main_task_id)), )

        elif step == ABILITY_TASK_STEP.PVP_BALANCER:

            pvp_balancer.add_to_arena_queue(data['hero_id'])

            return True, ABILITY_TASK_STEP.SUCCESS, ()
