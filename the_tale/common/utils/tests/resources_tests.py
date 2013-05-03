# coding: utf-8
import mock

from django.test import client

from common.utils.testcase import TestCase

from accounts.logic import register_user

from game.heroes.prototypes import HeroPrototype

from game.logic import create_test_map


class ResourceTest(TestCase):

    def setUp(self):
        super(ResourceTest, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.hero = HeroPrototype.get_by_account_id(account_id)

        self.client = client.Client()


    def tearDown(self):
        pass

    def test_hero_activate_unloginned(self):

        with mock.patch('accounts.prototypes.AccountPrototype.update_active_state') as fake_cmd:
            self.client.get('/')

        self.assertEqual(fake_cmd.call_count, 0)

    def test_hero_activate_loginned(self):
        with mock.patch('accounts.workers.accounts_manager.Worker.cmd_update_active_state') as fake_cmd:
            self.request_login('test_user@test.com')
            self.client.get('/')

        self.assertEqual(fake_cmd.call_count, 1)
