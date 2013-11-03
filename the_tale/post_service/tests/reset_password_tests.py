# coding: utf-8

from django.core import mail

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype, ResetPasswordTaskPrototype

from the_tale.game.logic import create_test_map

from the_tale.post_service.models import Message
from the_tale.post_service.prototypes import MessagePrototype


class ResetPasswordTests(testcase.TestCase):

    def setUp(self):
        super(ResetPasswordTests, self).setUp()
        create_test_map()

        register_user('user_1', 'user_1@test.com', '111111')
        self.account_1 = AccountPrototype.get_by_nick('user_1')

        self.reset_task = ResetPasswordTaskPrototype.create(self.account_1)
        self.message = MessagePrototype.get_priority_message()


    def test_register_message(self):
        self.assertEqual(Message.objects.all().count(), 1)

    def test_mail_send(self):
        self.assertEqual(len(mail.outbox), 0)
        self.message.process()
        self.assertTrue(self.message.state._is_PROCESSED)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.account_1.email])

        self.assertTrue(self.reset_task.uuid in mail.outbox[0].body)
        self.assertTrue(self.reset_task.uuid in mail.outbox[0].alternatives[0][0])

    def test_mail_send__to_system_user(self):
        from the_tale.accounts.logic import get_system_user

        Message.objects.all().delete()

        ResetPasswordTaskPrototype.create(get_system_user())
        message = MessagePrototype.get_priority_message()

        self.assertEqual(len(mail.outbox), 0)
        message.process()
        self.assertTrue(message.state._is_PROCESSED)
        self.assertEqual(len(mail.outbox), 0)
