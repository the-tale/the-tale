# coding: utf-8
import mock

from common.utils import testcase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user
from game.logic_storage import LogicStorage

from game.workers.environment import workers_environment

from game.logic import create_test_map

from game.map.places.prototypes import BuildingPrototype

from game.abilities.deck.building_repair import BuildingRepair, ABILITY_TASK_STEP

class BuildingRepairTest(testcase.TestCase):

    def setUp(self):
        super(BuildingRepairTest, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        result, account_2_id, bundle_id = register_user('test_user_2')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)
        self.account_2 = AccountPrototype.get_by_id(account_2_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)
        self.storage.load_account_data(self.account_2)

        self.hero_1 = self.storage.accounts_to_heroes[self.account_1.id]
        self.hero_2 = self.storage.accounts_to_heroes[self.account_2.id]

        self.ability_1 = BuildingRepair.get_by_hero_id(self.hero_1.id)
        self.ability_2 = BuildingRepair.get_by_hero_id(self.hero_2.id)

        workers_environment.deinitialize()
        workers_environment.initialize()

        self.highlevel = workers_environment.highlevel
        self.highlevel.process_initialize(0, 'highlevel')

        self.building = BuildingPrototype.create(self.place_1.persons[0])
        self.building._model.integrity = 0.5
        self.building.save()

    def use_attributes(self, hero_id, building_id=None, step=None, storage=None, highlevel=None):
        return {'data': {'hero_id': hero_id,
                         'building_id': self.building.id if building_id is None else building_id},
                'step': step,
                'main_task_id': 0,
                'storage': storage,
                'highlevel': highlevel}

    @mock.patch('game.heroes.prototypes.HeroPrototype.can_repair_building', True)
    def test_use(self):

        result, step, postsave_actions = self.ability_1.use(**self.use_attributes(hero_id=self.hero_1.id, storage=self.storage))

        self.assertEqual((result, step), (None, ABILITY_TASK_STEP.HIGHLEVEL))
        self.assertEqual(len(postsave_actions), 1)

        with mock.patch('game.workers.highlevel.Worker.cmd_logic_task') as highlevel_logic_task_counter:
            postsave_actions[0]()

        self.assertEqual(highlevel_logic_task_counter.call_count, 1)

        self.assertEqual(self.building.integrity, 0.5)

        result, step, postsave_actions = self.ability_1.use(**self.use_attributes(hero_id=self.hero_1.id,
                                                                                  step=step,
                                                                                  highlevel=self.highlevel))

        self.assertEqual((result, step, postsave_actions), (True, ABILITY_TASK_STEP.SUCCESS, ()))

        self.assertTrue(self.building.integrity > 0.5)

    def test_use_for_fast_account(self):
        self.assertEqual(self.building.integrity, 0.5)
        self.assertEqual(self.ability_2.use(**self.use_attributes(hero_id=self.hero_2.id, storage=self.storage)), (False, ABILITY_TASK_STEP.ERROR, ()))
        self.assertEqual(self.building.integrity, 0.5)

    def test_use_for_not_allowed_account(self):
        self.assertEqual(self.building.integrity, 0.5)
        self.assertEqual(self.ability_2.use(**self.use_attributes(hero_id=self.hero_2.id, storage=self.storage)), (False, ABILITY_TASK_STEP.ERROR, ()))
        self.assertEqual(self.building.integrity, 0.5)


    def test_use_for_wrong_building_id(self):
        self.assertEqual(self.building.integrity, 0.5)
        self.assertEqual(self.ability_1.use(**self.use_attributes(hero_id=self.hero_1.id, building_id=666, storage=self.storage)), (False, ABILITY_TASK_STEP.ERROR, ()))
        self.assertEqual(self.building.integrity, 0.5)

    def test_use_without_building(self):
        self.assertEqual(self.building.integrity, 0.5)
        arguments = self.use_attributes(hero_id=self.hero_1.id, storage=self.storage)
        del arguments['data']['building_id']
        self.assertEqual(self.ability_1.use(**arguments), (False, ABILITY_TASK_STEP.ERROR, ()))
        self.assertEqual(self.building.integrity, 0.5)
