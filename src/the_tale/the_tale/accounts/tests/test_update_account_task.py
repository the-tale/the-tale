# coding: utf-8
from unittest import mock

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.postponed_tasks import UpdateAccount, UPDATE_ACCOUNT_STATE

from the_tale.game.logic import create_test_map


class PostponedUpdateAccountTaskTests(testcase.TestCase):

    def setUp(self):
        super(PostponedUpdateAccountTaskTests, self).setUp()

        create_test_map()

        self.account = self.accounts_factory.create_account()
        self.postponed_task = UpdateAccount(account_id=self.account.id,
                                            method=AccountPrototype.prolong_premium,
                                            data={'days': 17})

    def test_create(self):
        self.assertEqual(self.postponed_task.account_id, self.account.id)
        self.assertEqual(self.postponed_task.method, 'prolong_premium')
        self.assertEqual(self.postponed_task.data, {'days': 17})
        self.assertTrue(self.postponed_task.state.is_UNPROCESSED)

    def test_serialization(self):
        self.assertEqual(self.postponed_task.serialize(), UpdateAccount.deserialize(self.postponed_task.serialize()).serialize())

    def test_processed__success(self):
        self.assertFalse(self.account.is_premium)
        self.postponed_task.process(main_task=mock.Mock())
        self.account.reload()
        self.assertTrue(self.account.is_premium)

    def test_processed__wrong_state(self):
        for state in UPDATE_ACCOUNT_STATE.records:
            if state.is_UNPROCESSED:
                continue
            self.postponed_task.state = state
            self.postponed_task.process(main_task=mock.Mock())
            self.account.reload()
            self.assertFalse(self.account.is_premium)
