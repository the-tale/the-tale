# coding: utf-8

import mock

from the_tale.common.utils import testcase
from the_tale.common.postponed_tasks import FakePostpondTaskPrototype, POSTPONED_TASK_LOGIC_RESULT

from the_tale.accounts.logic import register_user, REGISTER_USER_RESULT
from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.postponed_tasks import RegistrationTask, REGISTRATION_TASK_STATE
from the_tale.accounts.models import Account
from the_tale.accounts import exceptions
from the_tale.accounts.achievements.prototypes import AccountAchievementsPrototype

from the_tale.collections.prototypes import AccountItemsPrototype

from the_tale.finances.market import models as market_models

from the_tale.game.heroes.relations import EQUIPMENT_SLOT
from the_tale.game.heroes import logic as heroes_logic
from the_tale.game.heroes import models as heroes_models
from the_tale.game.logic import create_test_map

def raise_exception(*argv, **kwargs): raise Exception('unknown error')

class TestRegistration(testcase.TestCase):

    def setUp(self):
        super(TestRegistration, self).setUp()
        create_test_map()

    def test_successfull_result(self):

        self.assertEqual(AccountAchievementsPrototype._db_count(), 0)
        self.assertEqual(AccountItemsPrototype._db_count(), 0)

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        # test result
        self.assertEqual(result, REGISTER_USER_RESULT.OK)
        self.assertTrue(bundle_id is not None)


        #test basic structure
        account = AccountPrototype.get_by_id(account_id)

        self.assertEqual(account.nick, 'test_user')
        self.assertEqual(account.email, 'test_user@test.com')

        self.assertTrue(not account.is_fast)

        hero = heroes_logic.load_hero(account_id=account.id)

        # test hero equipment
        self.assertEqual(hero.equipment.get(EQUIPMENT_SLOT.PANTS).id, 'default_pants')
        self.assertEqual(hero.equipment.get(EQUIPMENT_SLOT.BOOTS).id, 'default_boots')
        self.assertEqual(hero.equipment.get(EQUIPMENT_SLOT.PLATE).id, 'default_plate')
        self.assertEqual(hero.equipment.get(EQUIPMENT_SLOT.GLOVES).id, 'default_gloves')
        self.assertEqual(hero.equipment.get(EQUIPMENT_SLOT.HAND_PRIMARY).id, 'default_weapon')

        self.assertTrue(hero.equipment.get(EQUIPMENT_SLOT.HAND_SECONDARY) is None)
        self.assertTrue(hero.equipment.get(EQUIPMENT_SLOT.HELMET) is None)
        self.assertTrue(hero.equipment.get(EQUIPMENT_SLOT.SHOULDERS) is None)
        self.assertTrue(hero.equipment.get(EQUIPMENT_SLOT.CLOAK) is None)
        self.assertTrue(hero.equipment.get(EQUIPMENT_SLOT.AMULET) is None)
        self.assertTrue(hero.equipment.get(EQUIPMENT_SLOT.RING) is None)

        self.assertEqual(heroes_models.HeroPreferences.objects.all().count(), 1)
        self.assertEqual(heroes_models.HeroPreferences.objects.get(hero_id=hero.id).energy_regeneration_type,
                         hero.preferences.energy_regeneration_type)

        self.assertEqual(account.referer, None)
        self.assertEqual(account.referer_domain, None)
        self.assertEqual(account.referral_of_id, None)
        self.assertEqual(account.action_id, None)

        self.assertEqual(account.is_bot, False)

        self.assertEqual(AccountAchievementsPrototype._db_count(), 1)
        self.assertEqual(AccountItemsPrototype._db_count(), 1)
        self.assertEqual(market_models.Goods.objects.count(), 1)


    def test_successfull_result__referer(self):
        referer = 'http://example.com/forum/post/1/'

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111', referer=referer)

        account = AccountPrototype.get_by_id(account_id)

        self.assertEqual(account.nick, 'test_user')
        self.assertEqual(account.email, 'test_user@test.com')
        self.assertEqual(account.referer, referer)
        self.assertEqual(account.referer_domain, 'example.com')

    def test_successfull_result__referral(self):
        result, owner_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111', referral_of_id=owner_id)

        account = AccountPrototype.get_by_id(account_id)

        self.assertEqual(account.referral_of_id, owner_id)

    def test_successfull_result__unexisted_referral(self):
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111', referral_of_id=666)

        account = AccountPrototype.get_by_id(account_id)

        self.assertEqual(account.referral_of_id, None)

    def test_successfull_result__wrong_referral(self):
        result, owner_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111', referral_of_id='%dxxx' % owner_id)

        account = AccountPrototype.get_by_id(account_id)

        self.assertEqual(account.referral_of_id, None)


    def test_successfull_result__action(self):
        result, owner_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111', action_id='action')

        account = AccountPrototype.get_by_id(account_id)

        self.assertEqual(account.action_id, 'action')

    def test_successfull_result__unexisted_action(self):
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111', action_id=None)

        account = AccountPrototype.get_by_id(account_id)

        self.assertEqual(account.action_id, None)

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

    def test_successfull_result__is_bot(self):
        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111', is_bot=True)
        account = AccountPrototype.get_by_id(account_id)
        self.assertEqual(account.is_bot, True)

    def test_successfull_result__is_bot_and_fast(self):
        self.assertRaises(exceptions.BotIsFastError, register_user, 'test_user', is_bot=True)


class TestRegistrationTask(testcase.TestCase):

    def setUp(self):
        super(TestRegistrationTask, self).setUp()
        create_test_map()
        self.task = RegistrationTask(account_id=None, referer=None, referral_of_id=None, action_id=None)

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
        task = RegistrationTask(account_id=None, referer=referer, referral_of_id=None, action_id=None)
        self.assertEqual(task.process(FakePostpondTaskPrototype()), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, REGISTRATION_TASK_STATE.PROCESSED)
        self.assertTrue(task.account)
        self.assertEqual(task.account.referer, referer)
        self.assertEqual(task.account.referer_domain, 'example.com')

    def test_process_success__with_referral(self):
        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        task = RegistrationTask(account_id=None, referer=None, referral_of_id=account_id, action_id=None)
        self.assertEqual(task.process(FakePostpondTaskPrototype()), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, REGISTRATION_TASK_STATE.PROCESSED)
        self.assertTrue(task.account)
        self.assertEqual(task.account.referral_of_id, account_id)

    def test_process_success__with_action(self):
        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        task = RegistrationTask(account_id=None, referer=None, referral_of_id=None, action_id='action')
        self.assertEqual(task.process(FakePostpondTaskPrototype()), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, REGISTRATION_TASK_STATE.PROCESSED)
        self.assertTrue(task.account)
        self.assertEqual(task.account.action_id, 'action')

    @mock.patch('the_tale.accounts.logic.register_user', lambda *argv, **kwargs: (REGISTER_USER_RESULT.OK+1, None, None))
    def test_process_unknown_error(self):
        self.assertEqual(self.task.process(FakePostpondTaskPrototype()), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(self.task.state, REGISTRATION_TASK_STATE.UNKNOWN_ERROR)
        self.assertEqual(Account.objects.all().count(), 0)

    @mock.patch('the_tale.accounts.logic.register_user', lambda *argv, **kwargs: raise_exception())
    def test_process_exceptin(self):
        self.assertRaises(Exception, self.task.process, FakePostpondTaskPrototype())
        self.assertEqual(Account.objects.all().count(), 0)
