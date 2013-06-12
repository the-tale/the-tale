# coding: utf-8

import mock

from common.utils import testcase
from common.postponed_tasks import FakePostpondTaskPrototype, POSTPONED_TASK_LOGIC_RESULT

from accounts.logic import register_user, REGISTER_USER_RESULT
from accounts.prototypes import AccountPrototype
from accounts.postponed_tasks import RegistrationTask, REGISTRATION_TASK_STATE
from accounts.models import Account

from game.heroes.prototypes import HeroPrototype

from game.heroes.bag import SLOTS
from game.logic import create_test_map

def raise_exception(*argv, **kwargs): raise Exception('unknown error')

class TestRegistration(testcase.TestCase):

    def setUp(self):
        super(TestRegistration, self).setUp()
        create_test_map()

    def test_successfull_result(self):
        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        # test result
        self.assertEqual(result, REGISTER_USER_RESULT.OK)
        self.assertTrue(bundle_id is not None)

        #test basic structure
        account = AccountPrototype.get_by_id(account_id)

        self.assertEqual(account.nick, 'test_user')
        self.assertEqual(account.email, 'test_user@test.com')

        self.assertTrue(not account.is_fast)

        hero = HeroPrototype.get_by_account_id(account.id)

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
        self.assertTrue(hero.equipment.get(SLOTS.RING) is None)


    def test_successfull_result__with_referer(self):
        referer = 'http://example.com/forum/post/1/'

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111', referer=referer)

        account = AccountPrototype.get_by_id(account_id)

        self.assertEqual(account.nick, 'test_user')
        self.assertEqual(account.email, 'test_user@test.com')
        self.assertEqual(account.referer, referer)
        self.assertEqual(account.referer_domain, 'example.com')

    def test_duplicate_nick(self):
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


class TestRegistrationTask(testcase.TestCase):

    def setUp(self):
        super(TestRegistrationTask, self).setUp()
        create_test_map()
        self.task = RegistrationTask(account_id=None, referer=None)

    def test_create(self):
        self.assertEqual(self.task.state, REGISTRATION_TASK_STATE.UNPROCESSED)

    def test_get_unique_nick(self):
        self.assertTrue(self.task.get_unique_nick() != self.task.get_unique_nick())

    def test_process_success(self):
        self.assertEqual(self.task.process(FakePostpondTaskPrototype()), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(self.task.state, REGISTRATION_TASK_STATE.PROCESSED)
        self.assertTrue(self.task.account)
        self.assertTrue(self.task.account.is_fast)
        self.assertEqual(Account.objects.all().count(), 1)

    def test_process_success__with_referer(self):
        referer = 'http://example.com/forum/post/1/'
        task = RegistrationTask(account_id=None, referer=referer)
        self.assertEqual(task.process(FakePostpondTaskPrototype()), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, REGISTRATION_TASK_STATE.PROCESSED)
        self.assertTrue(task.account)
        self.assertEqual(task.account.referer, referer)
        self.assertEqual(task.account.referer_domain, 'example.com')

    @mock.patch('accounts.logic.register_user', lambda *argv, **kwargs: (REGISTER_USER_RESULT.OK+1, None, None))
    def test_process_unknown_error(self):
        self.assertEqual(self.task.process(FakePostpondTaskPrototype()), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(self.task.state, REGISTRATION_TASK_STATE.UNKNOWN_ERROR)
        self.assertEqual(Account.objects.all().count(), 0)

    @mock.patch('accounts.logic.register_user', lambda *argv, **kwargs: (REGISTER_USER_RESULT.OK, 1, 1))
    def test_process_bundle_not_foud(self):
        self.assertEqual(self.task.process(FakePostpondTaskPrototype()), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(self.task.state, REGISTRATION_TASK_STATE.BUNDLE_NOT_FOUND)
        self.assertEqual(Account.objects.all().count(), 0)

    @mock.patch('accounts.logic.register_user', lambda *argv, **kwargs: raise_exception())
    def test_process_exceptin(self):
        self.assertRaises(Exception, self.task.process, FakePostpondTaskPrototype())
        self.assertEqual(Account.objects.all().count(), 0)
