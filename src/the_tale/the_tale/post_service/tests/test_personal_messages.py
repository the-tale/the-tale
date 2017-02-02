# coding: utf-8

from django.core import mail
from django.conf import settings as project_settings

from the_tale.common.utils import testcase

from the_tale.accounts.personal_messages import logic as pm_logic

from the_tale.game.logic import create_test_map

from the_tale.post_service.models import Message
from the_tale.post_service.prototypes import MessagePrototype


class PersonalMessagesTests(testcase.TestCase):

    def setUp(self):
        super(PersonalMessagesTests, self).setUp()

        create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        pm_logic.send_message(self.account_1.id, [self.account_2.id], 'test text')

        self.message = MessagePrototype.get_priority_message()


    def test_register_message(self):
        self.assertEqual(Message.objects.all().count(), 1)


    def test_no_subscription(self):
        self.account_2.personal_messages_subscription = False
        self.account_2.save()

        self.assertEqual(len(mail.outbox), 0)
        self.message.process()
        self.assertTrue(self.message.state.is_PROCESSED)
        self.assertEqual(len(mail.outbox), 0)


    def test_subscription(self):
        self.assertEqual(len(mail.outbox), 0)
        self.message.process()
        self.assertTrue(self.message.state.is_PROCESSED)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.account_2.email])

        self.assertTrue(self.account_1.nick in mail.outbox[0].body)
        self.assertFalse(self.account_2.nick in mail.outbox[0].body)
        self.assertTrue('test text' in mail.outbox[0].body)
        self.assertTrue(project_settings.SITE_URL in mail.outbox[0].body)

        self.assertTrue(self.account_1.nick in mail.outbox[0].alternatives[0][0])
        self.assertFalse(self.account_2.nick in mail.outbox[0].alternatives[0][0])
        self.assertTrue('test text' in mail.outbox[0].alternatives[0][0])
        self.assertTrue(project_settings.SITE_URL in mail.outbox[0].alternatives[0][0])


    def test_mail_send__to_system_user(self):
        from the_tale.accounts.logic import get_system_user

        Message.objects.all().delete()

        pm_logic.send_message(self.account_1.id, [get_system_user().id], 'test text')

        message = MessagePrototype.get_priority_message()

        self.assertEqual(len(mail.outbox), 0)
        message.process()
        self.assertTrue(message.state.is_PROCESSED)
        self.assertEqual(len(mail.outbox), 0)
