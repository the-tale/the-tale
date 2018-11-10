
import smart_imports

smart_imports.all()


class ArenaPvP1x1LeaveQueue(prototypes.AbilityPrototype):
    TYPE = relations.ABILITY_TYPE.ARENA_PVP_1x1_LEAVE_QUEUE

    def use(self, task, storage, pvp_balancer=None, **kwargs):

        if task.step.is_LOGIC:

            battle = pvp_prototypes.Battle1x1Prototype.get_by_account_id(task.hero.account_id)

            if battle is None:
                return task.logic_result()

            task.hero.add_message('angel_ability_arena_pvp_1x1_leave_queue', hero=task.hero)

            task.hero.update_habits(heroes_relations.HABIT_CHANGE_SOURCE.ARENA_LEAVE)

            task.hero.process_removed_artifacts()

            return task.logic_result(next_step=game_postponed_tasks.ComplexChangeTask.STEP.PVP_BALANCER)

        elif task.step.is_PVP_BALANCER:

            pvp_balancer.leave_arena_queue(task.data['hero_id'])

            return task.logic_result()
