# coding: utf-8

import datetime

import mock

from django.test import client

from common.utils.testcase import TestCase

from accounts.logic import register_user
from accounts.prototypes import AccountPrototype

from game.logic import create_test_map


class ResourceTest(TestCase):

    def setUp(self):
        super(ResourceTest, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account = AccountPrototype.get_by_id(account_id)

        self.client = client.Client()


    def tearDown(self):
        pass

    @mock.patch('accounts.prototypes.AccountPrototype.active_end_at', datetime.datetime.now() -datetime.timedelta(seconds=1))
    def test_account_activate_unloginned(self):

        with mock.patch('accounts.workers.accounts_manager.Worker.cmd_run_account_method') as fake_cmd:
            self.client.get('/')

        self.assertEqual(fake_cmd.call_count, 0)

    @mock.patch('accounts.prototypes.AccountPrototype.active_end_at', datetime.datetime.now() - datetime.timedelta(seconds=1))
    def test_account_activate_loginned(self):
        with mock.patch('accounts.workers.accounts_manager.Worker.cmd_run_account_method') as fake_cmd:
            self.request_login('test_user@test.com')
            self.client.get('/')

        self.assertEqual(fake_cmd.call_count, 1)
        self.assertEqual(fake_cmd.call_args, mock.call(account_id=self.account.id,
                                                       method_name=AccountPrototype.update_active_state.__name__,
                                                       data={}))
