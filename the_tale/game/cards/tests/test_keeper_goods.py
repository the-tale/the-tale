# coding: utf-8

import mock

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user
from the_tale.game.logic_storage import LogicStorage

from the_tale.game.workers.environment import workers_environment

from the_tale.game.logic import create_test_map

from the_tale.game.cards.prototypes import KeepersGoods

from the_tale.game.postponed_tasks import ComplexChangeTask


class KeepersGoodsTest(testcase.TestCase):

    def setUp(self):
        super(KeepersGoodsTest, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        result, account_2_id, bundle_id = register_user('test_user_2')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)
        self.account_2 = AccountPrototype.get_by_id(account_2_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)
        self.storage.load_account_data(self.account_2)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        self.card = KeepersGoods()

        workers_environment.deinitialize()
        workers_environment.initialize()

        self.highlevel = workers_environment.highlevel
        self.highlevel.process_initialize(0, 'highlevel')


    def use_attributes(self, hero_id, place_id=None, step=ComplexChangeTask.STEP.LOGIC, storage=None, highlevel=None, critical=False):
        return {'data': {'hero_id': hero_id,
                         'place_id': self.place_1.id if place_id is None else place_id},
                'step': step,
                'main_task_id': 0,
                'storage': storage,
                'highlevel': highlevel}

    def test_use(self):

        result, step, postsave_actions = self.card.use(**self.use_attributes(hero_id=self.hero.id, storage=self.storage))

        self.assertEqual((result, step), (ComplexChangeTask.RESULT.CONTINUE, ComplexChangeTask.STEP.HIGHLEVEL))
        self.assertEqual(len(postsave_actions), 1)

        with mock.patch('the_tale.game.workers.highlevel.Worker.cmd_logic_task') as highlevel_logic_task_counter:
            postsave_actions[0]()

        self.assertEqual(highlevel_logic_task_counter.call_count, 1)

        with self.check_delta(lambda: self.place_1.keepers_goods, KeepersGoods.GOODS):
            result, step, postsave_actions = self.card.use(**self.use_attributes(hero_id=self.hero.id,
                                                                                      step=step,
                                                                                      highlevel=self.highlevel))

        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))


    def test_use_for_wrong_place_id(self):
        with self.check_not_changed(lambda: self.place_1.keepers_goods):
            self.assertEqual(self.card.use(**self.use_attributes(hero_id=self.hero.id, place_id=666, storage=self.storage)),
                             (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))

    def test_use_without_place(self):
        with self.check_not_changed(lambda: self.place_1.keepers_goods):
            arguments = self.use_attributes(hero_id=self.hero.id, storage=self.storage)
            del arguments['data']['place_id']
            self.assertEqual(self.card.use(**arguments), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))
