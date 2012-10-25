# coding: utf-8
import datetime

import mock

from django.contrib.auth.models import User
from django.test import TestCase

from common.utils.fake import FakeLogger

from accounts.logic import register_user, REGISTER_USER_RESULT
from accounts.prototypes import RegistrationTaskPrototype, AccountPrototype
from accounts.models import Account, RegistrationTask, REGISTRATION_TASK_STATE

from game.heroes.bag import SLOTS
from game.logic import create_test_map

def raise_exception(*argv, **kwargs): raise Exception('unknown error')

class TestRegistration(TestCase):

    def setUp(self):
        create_test_map()

    def test_successfull_result(self):
        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        # test result
        self.assertEqual(result, REGISTER_USER_RESULT.OK)
        self.assertTrue(bundle_id is not None)

        #test basic structure
        user = User.objects.get(username='test_user')

        self.assertEqual(user.username, 'test_user')
        self.assertEqual(user.get_profile().nick, 'test_user')
        self.assertEqual(user.email, 'test_user@test.com')
        self.assertEqual(user.get_profile().email, 'test_user@test.com')

        account = AccountPrototype(user.get_profile())

        self.assertTrue(not account.is_fast)

        self.assertTrue(account.angel.get_hero())

        hero = account.angel.get_hero()

        # test hero equipment
        self.assertEqual(hero.equipment.get(SLOTS.PANTS).id, 'default_pants')
        self.assertEqual(hero.equipment.get(SLOTS.BOOTS).id, 'default_boots')
        self.assertEqual(hero.equipment.get(SLOTS.PLATE).id, 'default_plate')
        self.assertEqual(hero.equipment.get(SLOTS.GLOVES).id, 'default_gloves')
        self.assertEqual(hero.equipment.get(SLOTS.HAND_PRIMARY).id, 'default_weapon')

        self.assertTrue(hero.equipment.get(SLOTS.HAND_SECONDARY) is None)
        self.assertTrue(hero.equipment.get(SLOTS.HELMET) is None)
        self.assertTrue(hero.equipment.get(SLOTS.SHOULDERS) is None)
        self.assertTrue(hero.equipment.get(SLOTS.CLOAK) is None)
        self.assertTrue(hero.equipment.get(SLOTS.AMULET) is None)
        self.assertTrue(hero.equipment.get(SLOTS.RINGS) is None)

    def test_duplicate_username(self):
        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.assertEqual(result, REGISTER_USER_RESULT.OK)
        self.assertTrue(bundle_id is not None)
        result, account_id, bundle_id = register_user('test_user', 'test_user2@test.com', '111111')
        self.assertEqual(result, REGISTER_USER_RESULT.DUPLICATE_USERNAME)
        self.assertTrue(bundle_id is None)

    def test_duplicate_email(self):
        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.assertEqual(result, REGISTER_USER_RESULT.OK)
        self.assertTrue(bundle_id is not None)
        result, account_id, bundle_id = register_user('test_user2', 'test_user@test.com', '111111')
        self.assertEqual(result, REGISTER_USER_RESULT.DUPLICATE_EMAIL)
        self.assertTrue(bundle_id is None)


class TestRegistrationTask(TestCase):

    def setUp(self):
        create_test_map()
        self.task = RegistrationTaskPrototype.create()

    def test_create(self):
        self.assertEqual(self.task.state, REGISTRATION_TASK_STATE.WAITING)
        self.assertEqual(RegistrationTask.objects.all().count(), 1)

        task = RegistrationTaskPrototype.create()
        self.assertEqual(task.state, REGISTRATION_TASK_STATE.WAITING)
        self.assertEqual(RegistrationTask.objects.all().count(), 2)

    def test_get_by_id(self):
        self.assertEqual(self.task.id, RegistrationTaskPrototype.get_by_id(self.task.id).id)

    def test_get_unique_nick(self):
        self.assertTrue(self.task.get_unique_nick() != self.task.get_unique_nick())

    def test_process_success(self):
        self.task.process(FakeLogger())
        self.assertEqual(self.task.state, REGISTRATION_TASK_STATE.PROCESSED)
        self.assertTrue(self.task.account)

        self.assertTrue(self.task.account.is_fast)

        self.assertEqual(Account.objects.all().count(), 1)

    def test_process_processed(self):
        self.task.process(FakeLogger())
        self.task.process(FakeLogger())
        self.assertEqual(self.task.state, REGISTRATION_TASK_STATE.PROCESSED)
        self.assertEqual(Account.objects.all().count(), 1)

    def test_process_timeout(self):
        self.task.model.created_at = datetime.datetime.fromtimestamp(0)
        self.task.process(FakeLogger())
        self.assertEqual(self.task.state, REGISTRATION_TASK_STATE.UNPROCESSED)
        self.assertEqual(self.task.model.comment, 'timeout')
        self.assertEqual(Account.objects.all().count(), 0)

    @mock.patch('accounts.logic.register_user', lambda nick: (REGISTER_USER_RESULT.OK+1, None, None))
    def test_process_unknown_error(self):
        self.task.process(FakeLogger())
        self.assertEqual(self.task.state, REGISTRATION_TASK_STATE.ERROR)
        self.assertEqual(self.task.model.comment, 'unknown error')
        self.assertEqual(Account.objects.all().count(), 0)

    @mock.patch('accounts.logic.register_user', lambda nick: (REGISTER_USER_RESULT.OK, 1, 1))
    def test_process_bundle_not_foud(self):
        self.task.process(FakeLogger())
        self.assertEqual(self.task.state, REGISTRATION_TASK_STATE.ERROR)
        self.assertEqual(self.task.model.comment, 'bundle 1 does not found')
        self.assertEqual(Account.objects.all().count(), 0)

    @mock.patch('accounts.logic.register_user', lambda nick, password: raise_exception())
    def test_process_exceptin(self):
        self.task.process(FakeLogger())
        self.assertEqual(self.task.state, REGISTRATION_TASK_STATE.ERROR)
        self.assertTrue(self.task.model.comment)
        self.assertEqual(Account.objects.all().count(), 0)
