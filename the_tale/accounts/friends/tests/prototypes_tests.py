# coding: utf-8

from common.utils import testcase

from game.logic import create_test_map

from accounts.personal_messages.models import Message

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from accounts.friends.models import Friendship
from accounts.friends.prototypes import FriendshipPrototype



class FriendshipPrototypeTests(testcase.TestCase):

    def setUp(self):
        super(FriendshipPrototypeTests, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')
        self.account_1 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        self.account_2 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_3', 'test_user_3@test.com', '111111')
        self.account_3 = AccountPrototype.get_by_id(account_id)

    def test_request_friendship__own_request_exists(self):
        own_request_1 = FriendshipPrototype.request_friendship(self.account_1, self.account_2, u'text 1')
        own_request_2 = FriendshipPrototype.request_friendship(self.account_1, self.account_2, u'text 2')
        self.assertEqual(own_request_1.id, own_request_2.id)
        self.assertFalse(own_request_2.is_confirmed)
        self.assertEqual(own_request_2.text_html, u'text 2')
        self.assertEqual(Friendship.objects.all().count(), 1)
        self.assertEqual(Message.objects.all().count(), 1)
        self.assertEqual(Message.objects.all()[0].recipient_id, self.account_2.id)

    def test_request_friendship__his_request_exists(self):
        his_request = FriendshipPrototype.request_friendship(self.account_2, self.account_1, u'text 1')
        own_request = FriendshipPrototype.request_friendship(self.account_1, self.account_2, u'text 2')
        self.assertEqual(his_request.id, own_request.id)
        self.assertTrue(own_request.is_confirmed)
        self.assertEqual(own_request.text_html, u'text 1')
        self.assertEqual(Friendship.objects.all().count(), 1)
        self.assertEqual(Message.objects.all().count(), 2)
        self.assertEqual(Message.objects.all()[0].recipient_id, self.account_1.id)
        self.assertEqual(Message.objects.all()[1].recipient_id, self.account_2.id)

    def test_request_friendship__new_request(self):
        own_request = FriendshipPrototype.request_friendship(self.account_1, self.account_2, u'text 1')
        self.assertFalse(own_request.is_confirmed)
        self.assertEqual(own_request.text_html, u'text 1')
        self.assertEqual(Friendship.objects.all().count(), 1)
        self.assertEqual(Message.objects.all().count(), 1)
        self.assertEqual(Message.objects.all()[0].recipient_id, self.account_2.id)

    def test_remove_friendship__own_request_exists(self):
        FriendshipPrototype.request_friendship(self.account_1, self.account_2, u'text 1')
        FriendshipPrototype.remove_friendship(self.account_1, self.account_2)
        self.assertEqual(Friendship.objects.all().count(), 0)
        self.assertEqual(Message.objects.all().count(), 2)
        self.assertEqual(Message.objects.all().order_by('id')[1].recipient_id, self.account_2.id)

    def test_remove_friendship__his_request_exists(self):
        FriendshipPrototype.request_friendship(self.account_2, self.account_1, u'text 1')
        FriendshipPrototype.remove_friendship(self.account_1, self.account_2)
        self.assertEqual(Friendship.objects.all().count(), 0)
        self.assertEqual(Message.objects.all().count(), 2)
        self.assertEqual(Message.objects.all().order_by('id')[1].recipient_id, self.account_2.id)

    def test_remove_friendship__no_requests(self):
        FriendshipPrototype.remove_friendship(self.account_1, self.account_2)
        self.assertEqual(Friendship.objects.all().count(), 0)
        self.assertEqual(Message.objects.all().count(), 0)

    def test_get_friends_for__no_friendship(self):
        self.assertEqual(FriendshipPrototype.get_friends_for(self.account_1), [])

    def test_get_friends_for__only_candidates(self):
        FriendshipPrototype.request_friendship(self.account_1, self.account_2, u'text 1')
        FriendshipPrototype.request_friendship(self.account_3, self.account_1, u'text 2')
        self.assertEqual(FriendshipPrototype.get_friends_for(self.account_1), [])

    def test_get_friends_for__friends_exists(self):
        FriendshipPrototype.request_friendship(self.account_1, self.account_2, u'text 1')._confirm()
        FriendshipPrototype.request_friendship(self.account_3, self.account_1, u'text 2')._confirm()
        self.assertEqual(set(account.id for account in FriendshipPrototype.get_friends_for(self.account_1)), set([self.account_2.id, self.account_3.id]))

    def test_get_candidates_for__no_friendship(self):
        self.assertEqual(FriendshipPrototype.get_candidates_for(self.account_1), [])

    def test_get_candidates_for__only_friends(self):
        FriendshipPrototype.request_friendship(self.account_1, self.account_2, u'text 1')._confirm()
        FriendshipPrototype.request_friendship(self.account_3, self.account_1, u'text 2')._confirm()
        self.assertEqual(FriendshipPrototype.get_candidates_for(self.account_1), [])

    def test_get_candidates_for__candidates_exists(self):
        FriendshipPrototype.request_friendship(self.account_1, self.account_2, u'text 1')
        FriendshipPrototype.request_friendship(self.account_3, self.account_1, u'text 2')
        self.assertEqual([account.id for account in FriendshipPrototype.get_candidates_for(self.account_1)], [self.account_3.id])
