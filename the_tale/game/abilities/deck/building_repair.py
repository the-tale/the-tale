# coding: utf-8
import random

from the_tale.common.utils.enum import create_enum

from the_tale.game.workers.environment import workers_environment

from the_tale.game.map.places.storage import buildings_storage

from the_tale.game.abilities.prototypes import AbilityPrototype
from the_tale.game.abilities.relations import ABILITY_TYPE, ABILITY_RESULT


ABILITY_TASK_STEP = create_enum('ABILITY_TASK_STEP', (('ERROR', 0, u'ошибка'),
                                                      ('LOGIC', 1, u'логика'),
                                                      ('HIGHLEVEL', 2, u'высокоуровневая логика'),
                                                      ('SUCCESS', 3, u'обработка завершена') ))


class BuildingRepair(AbilityPrototype):
    TYPE = ABILITY_TYPE.BUILDING_REPAIR

    def use(self, data, step, main_task_id, storage, highlevel, **kwargs): # pylint: disable=R0911,W0613

        building_id = data.get('building_id')

        if building_id is None:
            return ABILITY_RESULT.FAILED, ABILITY_TASK_STEP.ERROR, ()

        if step is None:

            if building_id not in buildings_storage:
                return ABILITY_RESULT.FAILED, ABILITY_TASK_STEP.ERROR, ()

            if not buildings_storage[building_id].need_repair:
                return ABILITY_RESULT.FAILED, ABILITY_TASK_STEP.ERROR, ()

            hero = storage.heroes[data['hero_id']]

            if not hero.can_repair_building:
                return ABILITY_RESULT.FAILED, ABILITY_TASK_STEP.ERROR, ()

            critical = random.uniform(0, 1) < hero.might_crit_chance

            data['critical'] = critical

            if critical:
                hero.add_message('angel_ability_building_repair_crit', hero=hero)
            else:
                hero.add_message('angel_ability_building_repair', hero=hero)

            return ABILITY_RESULT.CONTINUE, ABILITY_TASK_STEP.HIGHLEVEL, ((lambda: workers_environment.highlevel.cmd_logic_task(hero.account_id, main_task_id)), )

        elif step == ABILITY_TASK_STEP.HIGHLEVEL:

            if building_id not in buildings_storage:
                return ABILITY_RESULT.FAILED, ABILITY_TASK_STEP.ERROR, ()

            building = buildings_storage[building_id]
            building.repair()

            if data.get('critical'): # repair second time
                building.repair()

            building.save()

            buildings_storage.update_version()

            return ABILITY_RESULT.SUCCESSED, ABILITY_TASK_STEP.SUCCESS, ()
