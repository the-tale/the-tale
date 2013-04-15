# coding: utf-8

from django.core import mail
from django.conf import settings as project_settings

from common.utils import testcase

from accounts.logic import register_user
from accounts.prototypes import AccountPrototype
from accounts.personal_messages.prototypes import MessagePrototype as PersonalMessagePrototype

from game.logic import create_test_map

from post_service.models import Message
from post_service.prototypes import MessagePrototype


class PersonalMessagesTests(testcase.TestCase):

    def setUp(self):
        super(PersonalMessagesTests, self).setUp()
        create_test_map()

        register_user('user_1', 'user_1@test.com', '111111')
        self.account_1 = AccountPrototype.get_by_nick('user_1')

        register_user('user_2', 'user_2n@test.com', '111111')
        self.account_2 = AccountPrototype.get_by_nick('user_2')

        self.personal_message = PersonalMessagePrototype.create(self.account_1, self.account_2, 'test text')

        self.message = MessagePrototype.get_priority_message()


    def test_register_message(self):
        self.assertEqual(Message.objects.all().count(), 1)

    def test_no_subscription(self):
        self.account_2.personal_messages_subscription = False
        self.account_2.save()

        self.assertEqual(len(mail.outbox), 0)
        self.message.process()
        self.assertTrue(self.message.state._is_PROCESSED)
        self.assertEqual(len(mail.outbox), 0)

    def test_subscription(self):
        self.assertEqual(len(mail.outbox), 0)
        self.message.process()
        self.assertTrue(self.message.state._is_PROCESSED)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.account_2.email])

        self.assertTrue(self.account_1.nick in mail.outbox[0].body)
        self.assertFalse(self.account_2.nick in mail.outbox[0].body)
        self.assertTrue(self.personal_message.text in mail.outbox[0].body)
        self.assertTrue(project_settings.SITE_URL in mail.outbox[0].body)

        self.assertTrue(self.account_1.nick in mail.outbox[0].alternatives[0][0])
        self.assertFalse(self.account_2.nick in mail.outbox[0].alternatives[0][0])
        self.assertTrue(self.personal_message.text in mail.outbox[0].alternatives[0][0])
        self.assertTrue(project_settings.SITE_URL in mail.outbox[0].alternatives[0][0])

    def test_mail_send__to_system_user(self):
        from accounts.logic import get_system_user

        Message.objects.all().delete()

        PersonalMessagePrototype.create(self.account_1, get_system_user(), 'test text')

        message = MessagePrototype.get_priority_message()

        self.assertEqual(len(mail.outbox), 0)
        message.process()
        self.assertTrue(message.state._is_PROCESSED)
        self.assertEqual(len(mail.outbox), 0)
