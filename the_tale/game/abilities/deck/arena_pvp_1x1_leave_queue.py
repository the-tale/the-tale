# coding: utf-8

from the_tale.game.pvp.prototypes import Battle1x1Prototype

from the_tale.game.workers.environment import workers_environment

from the_tale.game.heroes.relations import HABIT_CHANGE_SOURCE

from the_tale.game.abilities.prototypes import AbilityPrototype
from the_tale.game.abilities.relations import ABILITY_TYPE

from the_tale.game.postponed_tasks import ComplexChangeTask


class ArenaPvP1x1LeaveQueue(AbilityPrototype):
    TYPE = ABILITY_TYPE.ARENA_PVP_1x1_LEAVE_QUEUE

    def use(self, data, step, main_task_id, storage, pvp_balancer, **kwargs):

        if step.is_LOGIC:
            hero = storage.heroes[data['hero_id']]

            battle = Battle1x1Prototype.get_by_account_id(hero.account_id)

            if battle is None:
                return ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()

            hero.add_message('angel_ability_arena_pvp_1x1_leave_queue', hero=hero)

            hero.update_habits(HABIT_CHANGE_SOURCE.ARENA_LEAVE)

            return ComplexChangeTask.RESULT.CONTINUE, ComplexChangeTask.STEP.PVP_BALANCER, ((lambda: workers_environment.pvp_balancer.cmd_logic_task(hero.account_id, main_task_id)), )

        elif step.is_PVP_BALANCER:

            pvp_balancer.leave_arena_queue(data['hero_id'])

            return ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()
