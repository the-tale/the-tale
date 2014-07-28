# coding: utf-8

import mock

from textgen.words import Noun

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user
from the_tale.game.logic_storage import LogicStorage

from the_tale.game.workers.environment import workers_environment

from the_tale.game.logic import create_test_map

from the_tale.game.cards import prototypes
from the_tale.game.cards.tests.helpers import CardsTestMixin

from the_tale.game.postponed_tasks import ComplexChangeTask
from the_tale.game.balance import constants as c

from the_tale.game.map.places.prototypes import BuildingPrototype


class RepairBuildingTests(CardsTestMixin, testcase.TestCase):
    CARD = prototypes.RepairBuilding

    def setUp(self):
        super(RepairBuildingTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        result, account_2_id, bundle_id = register_user('test_user_2')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)
        self.account_2 = AccountPrototype.get_by_id(account_2_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)
        self.storage.load_account_data(self.account_2)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        self.card = self.CARD()

        workers_environment.deinitialize()
        workers_environment.initialize()

        self.highlevel = workers_environment.highlevel
        self.highlevel.process_initialize(0, 'highlevel')

        self.building_1 = BuildingPrototype.create(person=self.place_1.persons[0], name_forms=Noun.fast_construct('building-1-name'))
        self.building_2 = BuildingPrototype.create(person=self.place_2.persons[0], name_forms=Noun.fast_construct('building-1-name'))

        self.building_1.amortize(c.TURNS_IN_HOUR*24)
        self.building_2.amortize(c.TURNS_IN_HOUR*24)

    def test_use(self):

        self.assertTrue(self.building_1.need_repair)
        self.assertTrue(self.building_2.need_repair)

        result, step, postsave_actions = self.card.use(**self.use_attributes(hero=self.hero, storage=self.storage, building_id=self.building_2.id))

        self.assertEqual((result, step), (ComplexChangeTask.RESULT.CONTINUE, ComplexChangeTask.STEP.HIGHLEVEL))
        self.assertEqual(len(postsave_actions), 1)

        with mock.patch('the_tale.game.workers.highlevel.Worker.cmd_logic_task') as highlevel_logic_task_counter:
            postsave_actions[0]()

        self.assertEqual(highlevel_logic_task_counter.call_count, 1)

        result, step, postsave_actions = self.card.use(**self.use_attributes(hero=self.hero,
                                                                             step=step,
                                                                             highlevel=self.highlevel,
                                                                             building_id=self.building_2.id))

        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertTrue(self.building_1.need_repair)
        self.assertFalse(self.building_2.need_repair)


    def test_use_for_wrong_place_id(self):
        self.assertEqual(self.card.use(**self.use_attributes(hero=self.hero, building_id=666, storage=self.storage)),
                        (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))
