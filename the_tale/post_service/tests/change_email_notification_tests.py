# coding: utf-8

from django.core import mail

from common.utils import testcase

from accounts.logic import register_user
from accounts.prototypes import AccountPrototype, ChangeCredentialsTaskPrototype

from game.logic import create_test_map

from post_service.models import Message
from post_service.prototypes import MessagePrototype


class ChangeEmailNotificationTests(testcase.TestCase):

    def setUp(self):
        super(ChangeEmailNotificationTests, self).setUp()
        create_test_map()

        register_user('user_1', 'user_1@test.com', '111111')
        self.account = AccountPrototype.get_by_nick('user_1')

        self.task = ChangeCredentialsTaskPrototype.create(account=self.account,
                                                          new_email='user_2@test.com',
                                                          new_password='111111',
                                                          new_nick='user_2')
        self.task.request_email_confirmation()

        self.message = MessagePrototype.get_priority_message()

    def test_create_message(self):
        self.assertEqual(Message.objects.all().count(), 1)

    def test_mail_send(self):
        self.assertEqual(len(mail.outbox), 0)
        self.message.process()
        self.assertTrue(self.message.state._is_PROCESSED)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.account.email])

        self.assertTrue(self.task.uuid in mail.outbox[0].body)
        self.assertTrue(self.task.uuid in mail.outbox[0].alternatives[0][0])
