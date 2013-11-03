# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.postponed_tasks import UpdateAccount, UPDATE_ACCOUNT_STATE
from the_tale.accounts.logic import register_user

from the_tale.game.logic import create_test_map


class PostponedUpdateAccountTaskTests(testcase.TestCase):

    def setUp(self):
        super(PostponedUpdateAccountTaskTests, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)

        self.postponed_task = UpdateAccount(account_id=self.account.id,
                                            method=AccountPrototype.prolong_premium,
                                            data={'days': 17})

    def test_create(self):
        self.assertEqual(self.postponed_task.account_id, self.account.id)
        self.assertEqual(self.postponed_task.method, 'prolong_premium')
        self.assertEqual(self.postponed_task.data, {'days': 17})
        self.assertTrue(self.postponed_task.state._is_UNPROCESSED)

    def test_serialization(self):
        self.assertEqual(self.postponed_task.serialize(), UpdateAccount.deserialize(self.postponed_task.serialize()).serialize())

    def test_processed__success(self):
        self.assertFalse(self.account.is_premium)
        self.postponed_task.process(main_task=mock.Mock())
        self.account.reload()
        self.assertTrue(self.account.is_premium)

    def test_processed__wrong_state(self):
        for state in UPDATE_ACCOUNT_STATE._records:
            if state._is_UNPROCESSED:
                continue
            self.postponed_task.state = state
            self.postponed_task.process(main_task=mock.Mock())
            self.account.reload()
            self.assertFalse(self.account.is_premium)
