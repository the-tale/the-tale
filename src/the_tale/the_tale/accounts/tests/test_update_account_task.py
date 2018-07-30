
import smart_imports

smart_imports.all()


class PostponedUpdateAccountTaskTests(utils_testcase.TestCase):

    def setUp(self):
        super(PostponedUpdateAccountTaskTests, self).setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()
        self.postponed_task = postponed_tasks.UpdateAccount(account_id=self.account.id,
                                                            method=prototypes.AccountPrototype.prolong_premium,
                                                            data={'days': 17})

    def test_create(self):
        self.assertEqual(self.postponed_task.account_id, self.account.id)
        self.assertEqual(self.postponed_task.method, 'prolong_premium')
        self.assertEqual(self.postponed_task.data, {'days': 17})
        self.assertTrue(self.postponed_task.state.is_UNPROCESSED)

    def test_serialization(self):
        self.assertEqual(self.postponed_task.serialize(), postponed_tasks.UpdateAccount.deserialize(self.postponed_task.serialize()).serialize())

    def test_processed__success(self):
        self.assertFalse(self.account.is_premium)
        self.postponed_task.process(main_task=mock.Mock())
        self.account.reload()
        self.assertTrue(self.account.is_premium)

    def test_processed__wrong_state(self):
        for state in postponed_tasks.UPDATE_ACCOUNT_STATE.records:
            if state.is_UNPROCESSED:
                continue
            self.postponed_task.state = state
            self.postponed_task.process(main_task=mock.Mock())
            self.account.reload()
            self.assertFalse(self.account.is_premium)
