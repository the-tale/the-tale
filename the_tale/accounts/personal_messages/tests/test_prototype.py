# coding: utf-8

import datetime

from the_tale.common.utils import testcase

from the_tale.game.logic import create_test_map

from the_tale.post_service.models import Message as PostServiceMessage

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user, get_system_user

from the_tale.accounts.personal_messages.prototypes import MessagePrototype
from the_tale.accounts.personal_messages.models import Message
from the_tale.accounts.personal_messages import conf


class PrototypeTests(testcase.TestCase):

    def setUp(self):
        super(PrototypeTests, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user1', 'test_user1@test.com', '111111')
        self.account1 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user2', 'test_user2@test.com', '111111')
        self.account2 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user3', 'test_user3@test.com', '111111')
        self.account3 = AccountPrototype.get_by_id(account_id)

        self.message = MessagePrototype.create(self.account1, self.account2, 'message 1')
        self.message_2 = MessagePrototype.create(self.account1, self.account2, 'message 2')

    def test_initialize(self):
        self.assertEqual(Message.objects.all().count(), 2)
        self.assertEqual(self.account1.new_messages_number, 0)
        self.assertEqual(self.account2.new_messages_number, 2)
        self.assertEqual(PostServiceMessage.objects.all().count(), 2)

    def test_reset_new_messages_number(self):
        self.account2.reset_new_messages_number()
        self.assertEqual(self.account2.new_messages_number, 0)
        self.assertEqual(AccountPrototype.get_by_id(self.account2.id).new_messages_number, 0)

    def test_increment_new_messages_number(self):
        self.account1.increment_new_messages_number()
        self.account1.increment_new_messages_number()
        self.account1.increment_new_messages_number()
        self.assertEqual(self.account1.new_messages_number, 3)
        self.assertEqual(AccountPrototype.get_by_id(self.account1.id).new_messages_number, 3)

    def test_hide_from_sender(self):
        self.message.hide_from(sender=True)
        self.assertEqual(Message.objects.all().count(), 2)
        self.assertEqual(Message.objects.filter(hide_from_sender=True).count(), 1)

    def test_hide_from_recipient(self):
        self.message.hide_from(recipient=True)
        self.assertEqual(Message.objects.all().count(), 2)
        self.assertEqual(Message.objects.filter(hide_from_recipient=True).count(), 1)

    def test_hide_from_both(self):
        self.message.hide_from(sender=True, recipient=True)
        self.assertEqual(Message.objects.all().count(), 2)
        self.assertEqual(Message.objects.filter(hide_from_sender=True).count(), 1)
        self.assertEqual(Message.objects.filter(hide_from_recipient=True).count(), 1)

    def test_hide_all__sender(self):
        MessagePrototype.hide_all(account_id=self.account1.id)
        self.assertEqual(MessagePrototype._db_filter(hide_from_sender=True, hide_from_recipient=False).count(), 2)

    def test_hide_all__recipient(self):
        MessagePrototype.hide_all(account_id=self.account2.id)
        self.assertEqual(MessagePrototype._db_filter(hide_from_sender=False, hide_from_recipient=True).count(), 2)

    def test_remove_old_messages__hiden_by_recipients(self):
        message_3 = MessagePrototype.create(self.account1, self.account2, 'message 3')
        MessagePrototype.create(self.account1, self.account2, 'message 3')

        self.message.hide_from(sender=True)
        self.message_2.hide_from(recipient=True)
        message_3.hide_from(sender=True, recipient=True)

        with self.check_delta(MessagePrototype._db_count, -1):
            MessagePrototype.remove_old_messages()

        self.assertEqual(MessagePrototype.get_by_id(message_3.id), None)


    def test_remove_old_messages__system_user(self):

        system_user = get_system_user()

        messages = [ MessagePrototype.create(self.account1, self.account2, 'message 1'),
                     MessagePrototype.create(system_user, self.account2, 'message 2'),
                     MessagePrototype.create(self.account1, system_user, 'message 3'),
                     MessagePrototype.create(system_user, system_user, 'message 4'),

                     MessagePrototype.create(self.account1, self.account2, 'message 5'),
                     MessagePrototype.create(system_user, self.account2, 'message 6'),
                     MessagePrototype.create(self.account1, system_user, 'message 7'),
                     MessagePrototype.create(system_user, system_user, 'message 8') ]

        for message in messages[-4:]:
            message._model.created_at = datetime.datetime.now() - conf.settings.SYSTEM_MESSAGES_LEAVE_TIME
            message.save()

        with self.check_delta(MessagePrototype._db_count, -3):
            MessagePrototype.remove_old_messages()

        for message in messages[:5]:
            self.assertNotEqual(MessagePrototype.get_by_id(message.id), None)
