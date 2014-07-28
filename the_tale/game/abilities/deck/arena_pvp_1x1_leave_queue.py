# coding: utf-8

from the_tale.game.pvp.prototypes import Battle1x1Prototype

from the_tale.game.heroes.relations import HABIT_CHANGE_SOURCE

from the_tale.game.abilities.prototypes import AbilityPrototype
from the_tale.game.abilities.relations import ABILITY_TYPE

from the_tale.game.postponed_tasks import ComplexChangeTask


class ArenaPvP1x1LeaveQueue(AbilityPrototype):
    TYPE = ABILITY_TYPE.ARENA_PVP_1x1_LEAVE_QUEUE

    def use(self, task, storage, pvp_balancer=None, **kwargs):

        if task.step.is_LOGIC:

            battle = Battle1x1Prototype.get_by_account_id(task.hero.account_id)

            if battle is None:
                return task.logic_result()

            task.hero.add_message('angel_ability_arena_pvp_1x1_leave_queue', hero=task.hero)

            task.hero.update_habits(HABIT_CHANGE_SOURCE.ARENA_LEAVE)

            return task.logic_result(next_step=ComplexChangeTask.STEP.PVP_BALANCER)

        elif task.step.is_PVP_BALANCER:

            pvp_balancer.leave_arena_queue(task.data['hero_id'])

            return task.logic_result()
