
import smart_imports

smart_imports.all()


class ArenaPvP1x1(prototypes.AbilityPrototype):
    TYPE = relations.ABILITY_TYPE.ARENA_PVP_1x1

    def use(self, task, storage, pvp_balancer, **kwargs):

        if task.step.is_LOGIC:

            if not task.hero.can_participate_in_pvp:
                return task.logic_result(next_step=game_postponed_tasks.ComplexChangeTask.STEP.ERROR)

            task.hero.add_message('angel_ability_arena_pvp_1x1', hero=task.hero, energy=self.TYPE.cost)

            task.hero.update_habits(heroes_relations.HABIT_CHANGE_SOURCE.ARENA_SEND)

            task.hero.process_removed_artifacts()

            return task.logic_result(next_step=game_postponed_tasks.ComplexChangeTask.STEP.PVP_BALANCER)

        elif task.step.is_PVP_BALANCER:

            battle = pvp_prototypes.Battle1x1Prototype.get_by_account_id(task.data['account_id'])

            if battle is None:
                pvp_balancer.add_to_arena_queue(task.data['hero_id'])

            return task.logic_result()
