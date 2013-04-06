# coding: utf-8

from common.utils import testcase

from game.logic import create_test_map

from post_service.models import Message as PostServiceMessage

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from accounts.personal_messages.prototypes import MessagePrototype
from accounts.personal_messages.models import Message


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
