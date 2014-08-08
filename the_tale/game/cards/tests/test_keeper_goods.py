# coding: utf-8

import mock

from the_tale.amqp_environment import environment

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user
from the_tale.game.logic_storage import LogicStorage

from the_tale.game.logic import create_test_map

from the_tale.game.cards import prototypes
from the_tale.game.cards.tests.helpers import CardsTestMixin

from the_tale.game.postponed_tasks import ComplexChangeTask


class KeepersGoodsMixin(CardsTestMixin):
    CARD = None

    def setUp(self):
        super(KeepersGoodsMixin, self).setUp()
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

        environment.deinitialize()
        environment.initialize()

        self.highlevel = environment.workers.highlevel
        self.highlevel.process_initialize(0, 'highlevel')


    def test_use(self):

        result, step, postsave_actions = self.card.use(**self.use_attributes(hero=self.hero, storage=self.storage, place_id=self.place_1.id))

        self.assertEqual((result, step), (ComplexChangeTask.RESULT.CONTINUE, ComplexChangeTask.STEP.HIGHLEVEL))
        self.assertEqual(len(postsave_actions), 1)

        with mock.patch('the_tale.game.workers.highlevel.Worker.cmd_logic_task') as highlevel_logic_task_counter:
            postsave_actions[0]()

        self.assertEqual(highlevel_logic_task_counter.call_count, 1)

        with self.check_delta(lambda: self.place_1.keepers_goods, self.CARD.GOODS):
            result, step, postsave_actions = self.card.use(**self.use_attributes(hero=self.hero,
                                                                                 step=step,
                                                                                 highlevel=self.highlevel,
                                                                                 place_id=self.place_1.id))

        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))


    def test_use_for_wrong_place_id(self):
        with self.check_not_changed(lambda: self.place_1.keepers_goods):
            self.assertEqual(self.card.use(**self.use_attributes(hero=self.hero, place_id=666, storage=self.storage)),
                             (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))


class KeepersGoodsCommonTests(KeepersGoodsMixin, testcase.TestCase):
    CARD = prototypes.KeepersGoodsCommon

class KeepersGoodsUncommonTests(KeepersGoodsMixin, testcase.TestCase):
    CARD = prototypes.KeepersGoodsUncommon

class KeepersGoodsRareTests(KeepersGoodsMixin, testcase.TestCase):
    CARD = prototypes.KeepersGoodsRare

class KeepersGoodsEpicTests(KeepersGoodsMixin, testcase.TestCase):
    CARD = prototypes.KeepersGoodsEpic

class KeepersGoodsLegendaryTests(KeepersGoodsMixin, testcase.TestCase):
    CARD = prototypes.KeepersGoodsLegendary
