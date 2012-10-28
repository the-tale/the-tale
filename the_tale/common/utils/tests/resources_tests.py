# coding: utf-8
import mock
import time

from django.test import TestCase, client
from django.core.urlresolvers import reverse

from common.utils.fake import FakeWorkerCommand

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.logic import create_test_map
from game.bundles import BundlePrototype
from game.conf import game_settings

class ResourceTest(TestCase):

    def setUp(self):
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.bundle = BundlePrototype.get_by_id(bundle_id)
        self.account = AccountPrototype.get_by_id(account_id)
        self.hero = self.bundle.tests_get_hero()

        self.client = client.Client()


    def tearDown(self):
        pass

    def test_hero_activate_unloginned(self):

        fake_cmd = FakeWorkerCommand()

        with mock.patch('game.workers.environment.workers_environment.supervisor.cmd_mark_hero_as_active', fake_cmd):
            self.client.get('/')

        self.assertFalse(fake_cmd.commands)

    def test_hero_activate_loginned(self):
        fake_cmd = FakeWorkerCommand()

        with mock.patch('game.workers.environment.workers_environment.supervisor.cmd_mark_hero_as_active', fake_cmd):
            self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
            self.client.get('/')

        self.assertEqual(len(fake_cmd.commands), 1)

    def test_hero_activate_loginned_duplicate(self):
        fake_cmd = FakeWorkerCommand()

        with mock.patch('game.workers.environment.workers_environment.supervisor.cmd_mark_hero_as_active', fake_cmd):
            self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
            self.client.get('/')
            self.client.get('/')

        self.assertEqual(len(fake_cmd.commands), 1)

    def test_hero_activate_loginned_and_expired(self):
        fake_cmd = FakeWorkerCommand()

        with mock.patch('game.workers.environment.workers_environment.supervisor.cmd_mark_hero_as_active', fake_cmd):
            self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
            self.client.get('/')

            session = self.client.session
            session[game_settings.SESSION_REFRESH_TIME_KEY] = time.time() - game_settings.SESSION_REFRESH_PERIOD - 1
            session.save()

            self.client.get('/')

        self.assertEqual(len(fake_cmd.commands), 2)
