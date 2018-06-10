
from unittest import mock

from the_tale.common.utils.testcase import TestCase

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map
from the_tale.game import tt_api_energy

from the_tale.game.postponed_tasks import ComplexChangeTask
from the_tale.common.postponed_tasks.tests.helpers import FakePostpondTaskPrototype

from the_tale.game.abilities.relations import ABILITY_TYPE
from the_tale.game.abilities.deck import ABILITIES

ABILITY_TASK_STATE = ComplexChangeTask


class PrototypesTests(TestCase):

    def setUp(self):
        super(PrototypesTests, self).setUp()
        create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.ability = ABILITIES[ABILITY_TYPE.HELP]()

        self.task_data = {}

    def test_activate__no_energy(self):
        energy = tt_api_energy.energy_balance(self.account.id)
        tt_api_energy.change_energy_balance(account_id=self.account.id,
                                          type='test',
                                          energy=-energy,
                                          autocommit=True)

        task = self.ability.activate(self.hero, self.task_data)
        self.assertEqual(task, None)

    def test_activate__has_energy(self):
        task = self.ability.activate(self.hero, self.task_data)
        self.assertNotEqual(task.internal_logic.data['transaction_id'], None)

    @mock.patch('the_tale.game.abilities.relations.ABILITY_TYPE.HELP.cost', 0)
    def test_activate_and_complete__zero_cost(self):
        energy = tt_api_energy.energy_balance(self.account.id)
        tt_api_energy.change_energy_balance(account_id=self.account.id,
                                          type='test',
                                          energy=-energy,
                                          autocommit=True)

        task = self.ability.activate(self.hero, self.task_data)
        self.assertEqual(task.internal_logic.data['transaction_id'], None)

        task.process(FakePostpondTaskPrototype(), storage=self.storage)

        self.assertTrue(task.state.is_processed)

        self.assertEqual(tt_api_energy.energy_balance(self.account.id), 0)

    def test_activate_and_complete(self):
        energy = tt_api_energy.energy_balance(self.account.id)

        task = self.ability.activate(self.hero, self.task_data)
        self.assertNotEqual(task.internal_logic.data['transaction_id'], None)

        self.assertEqual(tt_api_energy.energy_balance(self.account.id), energy - self.ability.TYPE.cost)

        task.process(FakePostpondTaskPrototype(), storage=self.storage)

        self.assertTrue(task.state.is_processed)

        self.assertEqual(tt_api_energy.energy_balance(self.account.id), energy - self.ability.TYPE.cost)
