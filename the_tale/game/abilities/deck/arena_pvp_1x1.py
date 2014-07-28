# coding: utf-8

from the_tale.game.heroes.relations import HABIT_CHANGE_SOURCE

from the_tale.game.abilities.prototypes import AbilityPrototype
from the_tale.game.abilities.relations import ABILITY_TYPE

from the_tale.game.pvp.prototypes import Battle1x1Prototype

from the_tale.game.postponed_tasks import ComplexChangeTask


class ArenaPvP1x1(AbilityPrototype):
    TYPE = ABILITY_TYPE.ARENA_PVP_1x1

    def use(self, task, storage, pvp_balancer, **kwargs):

        if task.step.is_LOGIC:

            if not task.hero.can_participate_in_pvp:
                return task.logic_result(next_step=ComplexChangeTask.STEP.ERROR)

            task.hero.add_message('angel_ability_arena_pvp_1x1', hero=task.hero)

            task.hero.update_habits(HABIT_CHANGE_SOURCE.ARENA_SEND)

            return task.logic_result(next_step=ComplexChangeTask.STEP.PVP_BALANCER)

        elif task.step.is_PVP_BALANCER:

            battle = Battle1x1Prototype.get_by_account_id(task.data['account_id'])

            if battle is None:
                pvp_balancer.add_to_arena_queue(task.data['hero_id'])

            return task.logic_result()
