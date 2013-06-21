# coding: utf-8
import datetime

from common.utils import testcase

from common.postponed_tasks import FakePostpondTaskPrototype, POSTPONED_TASK_LOGIC_RESULT

from game.heroes.models import Hero
from game.quests.models import Quest
from game.models import Bundle
from game.logic import create_test_map

from accounts.logic import block_expired_accounts
from accounts.models import Account
from accounts.postponed_tasks import RegistrationTask

class TestLogic(testcase.TestCase):

    def setUp(self):
        super(TestLogic, self).setUp()
        create_test_map()


    def test_block_expired_accounts(self):
        task = RegistrationTask(account_id=None, referer=None)
        self.assertEqual(task.process(FakePostpondTaskPrototype()), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        task.account._model.created_at = datetime.datetime.fromtimestamp(0)
        task.account._model.save()

        block_expired_accounts()

        self.assertEqual(Hero.objects.all().count(), 0)
        self.assertEqual(Quest.objects.all().count(), 0)

        self.assertEqual(Bundle.objects.all().count(), 0)

        self.assertEqual(Account.objects.all().count(), 0)
