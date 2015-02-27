# coding: utf-8

import mock

from the_tale.common.postponed_tasks import PostponedTaskPrototype
from the_tale.common.utils import testcase
from the_tale.common.postponed_tasks import POSTPONED_TASK_LOGIC_RESULT

from the_tale.accounts import logic as accounts_logic
from the_tale.accounts import conf as accounts_conf

from the_tale.accounts.personal_messages import prototypes as personal_messages_prototypes


from the_tale.game.logic import create_test_map

from the_tale.accounts.personal_messages import models
from the_tale.accounts.personal_messages import prototypes
from the_tale.accounts.personal_messages import forms
from the_tale.accounts.personal_messages import conf
from the_tale.accounts.personal_messages import postponed_tasks


class TaskTests(testcase.TestCase):

    def setUp(self):
        super(TaskTests, self).setUp()

        create_test_map()

        self.good_1_uid = 'good-1'

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()
        self.account_3 = self.accounts_factory.create_account()

        self.task = postponed_tasks.SendMessagesTask(account_id=self.account_2.id,
                                                     recipients=[self.account_1.id, self.account_3.id],
                                                     message=u'test-message')

        self.main_task = mock.Mock(comment=None, id=777)


    def test_serialization(self):
        self.assertEqual(self.task.serialize(), postponed_tasks.SendMessagesTask.deserialize(self.task.serialize()).serialize())


    def test_initialization(self):
        self.assertTrue(self.task.state.is_UNPROCESSED)
        self.assertTrue(self.task.step.is_UNPROCESSED)
        self.assertEqual(self.task.account_id, self.account_2.id)
        self.assertEqual(self.task.message, u'test-message')
        self.assertEqual(self.task.recipients, [self.account_1.id, self.account_3.id])


    def test_success(self):
        with self.check_delta(prototypes.MessagePrototype._db_count, 2):
            self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        message_1, message_2 = prototypes.MessagePrototype.from_query(prototypes.MessagePrototype._db_all())

        self.assertEqual(message_1.recipient_id, self.account_1.id)
        self.assertEqual(message_1.sender_id, self.account_2.id)
        self.assertEqual(message_1.text, 'test-message')

        self.assertEqual(message_2.recipient_id, self.account_3.id)
        self.assertEqual(message_2.sender_id, self.account_2.id)
        self.assertEqual(message_2.text, 'test-message')


    def test__system_user(self):
        self.account_3.nick = accounts_conf.accounts_settings.SYSTEM_USER_NICK
        self.account_3.save()

        with self.check_not_changed(prototypes.MessagePrototype._db_count):
            self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.ERROR)

        self.assertTrue(self.task.state.is_SYSTEM_USER)


    def test__banned(self):
        self.account_2.ban_forum(30)
        self.account_2.save()

        with self.check_not_changed(prototypes.MessagePrototype._db_count):
            self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.ERROR)

        self.assertTrue(self.task.state.is_BANNED)


    def test__fast_user(self):
        self.account_1.is_fast = True
        self.account_1.save()

        with self.check_not_changed(prototypes.MessagePrototype._db_count):
            self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.ERROR)

        self.assertTrue(self.task.state.is_FAST_USER)
