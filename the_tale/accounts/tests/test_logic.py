# coding: utf-8
import mock
import datetime

from the_tale.common.utils import testcase

from the_tale.common.postponed_tasks import FakePostpondTaskPrototype, POSTPONED_TASK_LOGIC_RESULT, PostponedTaskPrototype

from the_tale.game.heroes.models import Hero
from the_tale.game.logic import create_test_map

from the_tale.accounts import logic
from the_tale.accounts import conf
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

        logic.block_expired_accounts()

        self.assertEqual(Hero.objects.all().count(), 0)

        self.assertEqual(Account.objects.all().count(), 0)

        self.assertEqual(AccountAchievementsPrototype._db_count(), 0)

    def test_get_account_id_by_email(self):
        self.assertEqual(logic.get_account_id_by_email('bla@bla.bla'), None)
        self.assertEqual(logic.get_account_id_by_email('test_user@test.com'), None)

        result, account_id, bundle_id = logic.register_user('test_user', 'test_user@test.com', '111111')

        self.assertEqual(logic.get_account_id_by_email('test_user@test.com'), account_id)

    def test_initiate_transfer_money(self):
        sender = self.accounts_factory.create_account()
        recipient = self.accounts_factory.create_account()

        with mock.patch('the_tale.common.postponed_tasks.workers.refrigerator.Worker.cmd_wait_task') as cmd_wait_task:
            with self.check_delta(PostponedTaskPrototype._db_count, 1):
                task = logic.initiate_transfer_money(sender_id=sender.id,
                                                     recipient_id=recipient.id,
                                                     amount=1000,
                                                     comment=u'some comment')

        self.assertTrue(task.internal_logic.state.is_UNPROCESSED)
        self.assertTrue(task.internal_logic.step.is_INITIALIZE)
        self.assertEqual(task.internal_logic.sender_id, sender.id)
        self.assertEqual(task.internal_logic.recipient_id, recipient.id)
        self.assertEqual(task.internal_logic.transfer_transaction, None)
        self.assertEqual(task.internal_logic.commission_transaction, None)
        self.assertEqual(task.internal_logic.comment, u'some comment')
        self.assertEqual(task.internal_logic.amount, int(1000 * (1 - conf.accounts_settings.MONEY_SEND_COMMISSION)))
        self.assertEqual(task.internal_logic.commission, 1000 * conf.accounts_settings.MONEY_SEND_COMMISSION)
