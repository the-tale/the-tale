
from unittest import mock

from the_tale.amqp_environment import environment

from the_tale.common.utils import testcase

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.logic import create_test_map

from the_tale.game import names

from the_tale.game.cards import cards
from the_tale.game.cards.tests.helpers import CardsTestMixin

from the_tale.game.postponed_tasks import ComplexChangeTask
from the_tale.game.balance import constants as c

from the_tale.game.places import logic as places_logic


class RepairBuildingMixin(CardsTestMixin):
    CARD = None

    def setUp(self):
        super(RepairBuildingMixin, self).setUp()

        self.place_1, self.place_2, self.place_3 = create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account(is_fast=True)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)
        self.storage.load_account_data(self.account_2)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        environment.deinitialize()
        environment.initialize()

        self.highlevel = environment.workers.highlevel
        self.highlevel.process_initialize(0, 'highlevel')

        self.building_1 = places_logic.create_building(person=self.place_1.persons[0], utg_name=names.generator().get_test_name('building-1-name'))
        self.building_2 = places_logic.create_building(person=self.place_2.persons[0], utg_name=names.generator().get_test_name('building-1-name'))

        self.building_1.integrity = 0
        self.building_2.integrity = 0

    def test_use(self):

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(hero=self.hero, storage=self.storage, value=self.building_2.id))

        self.assertEqual((result, step), (ComplexChangeTask.RESULT.CONTINUE, ComplexChangeTask.STEP.HIGHLEVEL))
        self.assertEqual(len(postsave_actions), 1)

        with mock.patch('the_tale.game.workers.highlevel.Worker.cmd_logic_task') as highlevel_logic_task_counter:
            postsave_actions[0]()

        self.assertEqual(highlevel_logic_task_counter.call_count, 1)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(hero=self.hero,
                                                                             step=step,
                                                                             highlevel=self.highlevel,
                                                                             value=self.building_2.id))

        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(self.building_1.integrity, 0)
        self.assertEqual(self.building_2.integrity, self.CARD.effect.modificator)


    def test_use_for_wrong_building_id(self):
        self.assertEqual(self.CARD.effect.use(**self.use_attributes(hero=self.hero, value=666, storage=self.storage)),
                        (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))



class RepairBuildingCommonTests(RepairBuildingMixin, testcase.TestCase):
    CARD = cards.CARD.REPAIR_BUILDING_COMMON


class RepairBuildingUncommonTests(RepairBuildingMixin, testcase.TestCase):
    CARD = cards.CARD.REPAIR_BUILDING_UNCOMMON


class RepairBuildingRareTests(RepairBuildingMixin, testcase.TestCase):
    CARD = cards.CARD.REPAIR_BUILDING_RARE
