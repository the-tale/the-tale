# coding: utf-8
import datetime

from the_tale.common.utils import testcase

from the_tale.common.postponed_tasks import FakePostpondTaskPrototype, POSTPONED_TASK_LOGIC_RESULT

from the_tale.game.heroes.models import Hero
from the_tale.game.models import Bundle
from the_tale.game.logic import create_test_map

from the_tale.accounts.logic import block_expired_accounts, get_account_id_by_email, register_user
from the_tale.accounts.models import Account
from the_tale.accounts.postponed_tasks import RegistrationTask
from the_tale.accounts.achievements.prototypes import AccountAchievementsPrototype

class TestLogic(testcase.TestCase):

    def setUp(self):
        super(TestLogic, self).setUp()
        create_test_map()


    def test_block_expired_accounts(self):
        task = RegistrationTask(account_id=None, referer=None, referral_of_id=None, action_id=None)
        self.assertEqual(task.process(FakePostpondTaskPrototype()), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        task.account._model.created_at = datetime.datetime.fromtimestamp(0)
        task.account._model.save()

        self.assertEqual(AccountAchievementsPrototype._db_count(), 1)

        block_expired_accounts()

        self.assertEqual(Hero.objects.all().count(), 0)

        self.assertEqual(Bundle.objects.all().count(), 0)

        self.assertEqual(Account.objects.all().count(), 0)

        self.assertEqual(AccountAchievementsPrototype._db_count(), 0)

    def test_get_account_id_by_email(self):
        self.assertEqual(get_account_id_by_email('bla@bla.bla'), None)
        self.assertEqual(get_account_id_by_email('test_user@test.com'), None)

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.assertEqual(get_account_id_by_email('test_user@test.com'), account_id)
