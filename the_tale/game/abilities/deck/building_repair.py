# coding: utf-8
import random

from the_tale.game.places import storage as places_storage

from the_tale.game.abilities.prototypes import AbilityPrototype
from the_tale.game.abilities.relations import ABILITY_TYPE

from the_tale.game.postponed_tasks import ComplexChangeTask


class BuildingRepair(AbilityPrototype):
    TYPE = ABILITY_TYPE.BUILDING_REPAIR

    def use(self, task, storage, highlevel=None, **kwargs): # pylint: disable=R0911,W0613

        building_id = task.data.get('building_id')

        if building_id is None:
            return task.logic_result(next_step=ComplexChangeTask.STEP.ERROR)

        if task.step.is_LOGIC:

            if building_id not in places_storage.buildings:
                return task.logic_result(next_step=ComplexChangeTask.STEP.ERROR)

            if not places_storage.buildings[building_id].need_repair:
                return task.logic_result(next_step=ComplexChangeTask.STEP.ERROR)

            if not task.hero.can_repair_building:
                return task.logic_result(next_step=ComplexChangeTask.STEP.ERROR)

            critical = random.uniform(0, 1) < task.hero.might_crit_chance

            task.data['critical'] = critical

            task.hero.cards.change_help_count(1)

            if critical:
                task.hero.add_message('angel_ability_building_repair_crit', hero=task.hero)
            else:
                task.hero.add_message('angel_ability_building_repair', hero=task.hero)

            return task.logic_result(next_step=ComplexChangeTask.STEP.HIGHLEVEL)

        elif task.step.is_HIGHLEVEL:

            if building_id not in places_storage.buildings:
                return task.logic_result(next_step=ComplexChangeTask.STEP.ERROR)

            building = places_storage.buildings[building_id]
            building.repair()

            if task.data.get('critical'): # repair second time
                building.repair()

            building.save()

            places_storage.buildings.update_version()

            return task.logic_result(next_step=ComplexChangeTask.STEP.SUCCESS)
