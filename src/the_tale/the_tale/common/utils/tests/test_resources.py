# coding: utf-8

import datetime

from unittest import mock

from django.test import client

from the_tale.common.utils.testcase import TestCase

from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.logic import create_test_map


class ResourceTest(TestCase):

    def setUp(self):
        super(ResourceTest, self).setUp()

        create_test_map()

        self.account = self.accounts_factory.create_account()

        self.client = client.Client()


    def tearDown(self):
        pass

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.active_end_at', datetime.datetime.now() -datetime.timedelta(seconds=1))
    def test_account_activate_unloginned(self):

        with mock.patch('the_tale.accounts.workers.accounts_manager.Worker.cmd_run_account_method') as fake_cmd:
            self.client.get('/')

        self.assertEqual(fake_cmd.call_count, 0)

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.active_end_at', datetime.datetime.now() - datetime.timedelta(seconds=1))
    def test_account_activate_loginned(self):
        with mock.patch('the_tale.accounts.workers.accounts_manager.Worker.cmd_run_account_method') as fake_cmd:
            self.request_login(self.account.email)
            self.client.get('/')

        self.assertEqual(fake_cmd.call_count, 1)
        self.assertEqual(fake_cmd.call_args, mock.call(account_id=self.account.id,
                                                       method_name=AccountPrototype.update_active_state.__name__,
                                                       data={}))
