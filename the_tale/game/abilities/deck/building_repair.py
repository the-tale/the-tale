# coding: utf-8

from common.utils.enum import create_enum

from game.workers.environment import workers_environment

from game.balance import constants as c

from game.map.places.storage import buildings_storage

from game.abilities.prototypes import AbilityPrototype


ABILITY_TASK_STEP = create_enum('ABILITY_TASK_STEP', (('ERROR', 0, u'ошибка'),
                                                      ('LOGIC', 1, u'логика'),
                                                      ('HIGHLEVEL', 2, u'высокоуровневая логика'),
                                                      ('SUCCESS', 3, u'обработка завершена') ))


class BuildingRepair(AbilityPrototype):

    COST = c.BUILDING_WORKERS_ENERGY_COST

    COMMAND_PREFIX = 'building_repair'

    NAME = u'Вызвать рабочего'
    DESCRIPTION = u'Вызвать рабочего для ремонта здания'

    def use(self, data, step, main_task_id, storage, highlevel, **kwargs):

        building_id = data.get('building_id')

        if building_id is None:
            return False, ABILITY_TASK_STEP.ERROR, ()

        if step is None:

            if building_id not in buildings_storage:
                return False, ABILITY_TASK_STEP.ERROR, ()

            if not buildings_storage[building_id].need_repair:
                return False, ABILITY_TASK_STEP.ERROR, ()

            hero = storage.heroes[data['hero_id']]

            if not hero.can_repair_building:
                return False, ABILITY_TASK_STEP.ERROR, ()

            hero.add_message('angel_ability_building_repair', hero=hero)

            return None, ABILITY_TASK_STEP.HIGHLEVEL, ((lambda: workers_environment.highlevel.cmd_logic_task(hero.account_id, main_task_id)), )

        elif step == ABILITY_TASK_STEP.HIGHLEVEL:

            if building_id not in buildings_storage:
                return False, ABILITY_TASK_STEP.ERROR, ()

            building = buildings_storage[building_id]
            building.repair()
            building.save()

            buildings_storage.update_version()

            return True, ABILITY_TASK_STEP.SUCCESS, ()
