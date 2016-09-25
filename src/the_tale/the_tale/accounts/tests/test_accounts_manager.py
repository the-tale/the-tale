# coding: utf-8

import datetime

import mock

from the_tale.common.utils import testcase

from the_tale.amqp_environment import environment

from the_tale.accounts.prototypes import AccountPrototype, RandomPremiumRequestPrototype
from the_tale.accounts.conf import accounts_settings

from the_tale.game.logic import create_test_map



class AccountsManagerTest(testcase.TestCase):

    def setUp(self):
        super(AccountsManagerTest, self).setUp()

        create_test_map()

        self.account = self.accounts_factory.create_account()

        environment.deinitialize()
        environment.initialize()

        self.worker = environment.workers.accounts_manager
        self.worker.initialize()

    def tearDown(self):
        pass

    def test_process_initialize(self):
        self.assertTrue(self.worker.initialized)

    def test_process_run_account_method__boundmethod(self):
        self.assertFalse(self.account.is_premium)
        self.worker.process_run_account_method(account_id=self.account.id,
                                               method_name=AccountPrototype.prolong_premium.__name__,
                                               data={'days': 1})
        self.account.reload()
        self.assertTrue(self.account.is_premium)


    def test_run_random_premium_requests_processing__no_requests(self):

        with mock.patch('the_tale.accounts.prototypes.RandomPremiumRequestPrototype.process') as process:
            self.worker.run_random_premium_requests_processing()

        self.assertEqual(process.call_count, 0)


    def test_run_random_premium_requests_processing__has_requests_can_not_process(self):

        request = RandomPremiumRequestPrototype.create(self.account.id, days=30)

        self.worker.run_random_premium_requests_processing()

        request.reload()
        self.assertTrue(request.state.is_WAITING)

    def test_run_random_premium_requests_processing__has_requests_can_process(self):
        account_2 = self.accounts_factory.create_account()
        AccountPrototype._db_all().update(active_end_at=datetime.datetime.now() + datetime.timedelta(days=1),
                                          created_at=datetime.datetime.now() - accounts_settings.RANDOM_PREMIUM_CREATED_AT_BARRIER)

        request = RandomPremiumRequestPrototype.create(self.account.id, days=30)

        self.worker.run_random_premium_requests_processing()

        request.reload()
        self.assertTrue(request.state.is_PROCESSED)
        self.assertEqual(request.receiver_id, account_2.id)
