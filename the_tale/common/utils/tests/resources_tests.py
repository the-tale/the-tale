# coding: utf-8
import mock
import time

from django.test import client

from common.utils.testcase import TestCase
from common.utils.fake import FakeWorkerCommand

from accounts.logic import register_user

from game.heroes.prototypes import HeroPrototype

from game.logic import create_test_map
from game.conf import game_settings

class ResourceTest(TestCase):

    def setUp(self):
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.hero = HeroPrototype.get_by_account_id(account_id)

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
            self.request_login('test_user@test.com')
            self.client.get('/')

        self.assertEqual(len(fake_cmd.commands), 1)

    def test_hero_activate_loginned_duplicate(self):
        fake_cmd = FakeWorkerCommand()

        with mock.patch('game.workers.environment.workers_environment.supervisor.cmd_mark_hero_as_active', fake_cmd):
            self.request_login('test_user@test.com')
            self.client.get('/')
            self.client.get('/')

        self.assertEqual(len(fake_cmd.commands), 1)

    def test_hero_activate_loginned_and_expired(self):
        fake_cmd = FakeWorkerCommand()

        with mock.patch('game.workers.environment.workers_environment.supervisor.cmd_mark_hero_as_active', fake_cmd):
            self.request_login('test_user@test.com')
            self.client.get('/')

            session = self.client.session
            session[game_settings.SESSION_REFRESH_TIME_KEY] = time.time() - game_settings.SESSION_REFRESH_PERIOD - 1
            session.save()

            self.client.get('/')

        self.assertEqual(len(fake_cmd.commands), 2)
