# coding: utf-8

from django.core import mail

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import ChangeCredentialsTaskPrototype

from the_tale.game.logic import create_test_map

from the_tale.post_service.models import Message
from the_tale.post_service.prototypes import MessagePrototype


class ChangeEmailNotificationTests(testcase.TestCase):

    def setUp(self):
        super(ChangeEmailNotificationTests, self).setUp()

        create_test_map()

        self.account = self.accounts_factory.create_account()


    def create_task_and_message(self, account, new_nick):
        task = ChangeCredentialsTaskPrototype.create(account=account,
                                                     new_email='%s@test.com' % new_nick,
                                                     new_password='111111',
                                                     new_nick=new_nick)
        task.request_email_confirmation()

        return task, MessagePrototype.get_priority_message()

    def test_create_message(self):
        self.create_task_and_message(self.account, 'user_1_new')
        self.assertEqual(Message.objects.all().count(), 1)

    def test_mail_send(self):
        task, message = self.create_task_and_message(self.account, 'user_1_new')
        self.assertEqual(len(mail.outbox), 0)
        message.process()
        self.assertTrue(message.state.is_PROCESSED)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['user_1_new@test.com'])

        self.assertTrue(task.uuid in mail.outbox[0].body)
        self.assertTrue(task.uuid in mail.outbox[0].alternatives[0][0])

    def test_mail_send__to_system_user(self):
        from the_tale.accounts.logic import get_system_user
        task, message = self.create_task_and_message(get_system_user(), 'user_1_new')
        self.assertEqual(len(mail.outbox), 0)
        message.process()
        self.assertTrue(message.state.is_PROCESSED)
        self.assertEqual(len(mail.outbox), 0)

    def test_mail_send_for_fast_account(self):
        account_2 = self.accounts_factory.create_account()

        task, message = self.create_task_and_message(account_2, 'user_2_new')

        self.assertEqual(len(mail.outbox), 0)

        message = MessagePrototype.get_priority_message()
        message.process()

        self.assertTrue(message.state.is_PROCESSED)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['user_2_new@test.com'])

        self.assertTrue(task.uuid in mail.outbox[0].body)
        self.assertTrue(task.uuid in mail.outbox[0].alternatives[0][0])
