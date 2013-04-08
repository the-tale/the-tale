# coding: utf-8

from dext.utils.urls import url

from common.utils import testcase

from game.logic import create_test_map

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from accounts.friends.models import Friendship
from accounts.friends.prototypes import FriendshipPrototype


class FriendshipRequestsTests(testcase.TestCase):

    def setUp(self):
        super(FriendshipRequestsTests, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')
        self.account_1 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        self.account_2 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_3', 'test_user_3@test.com', '111111')
        self.account_3 = AccountPrototype.get_by_id(account_id)

        self.request_login('test_user_1@test.com')

    def test_index__no_friends(self):
        self.check_html_ok(self.client.get(url('accounts:friends:')), texts=['pgf-no-friends-message'])

    def test_index(self):
        FriendshipPrototype.request_friendship(self.account_1, self.account_2, 'text 1')._confirm()
        FriendshipPrototype.request_friendship(self.account_1, self.account_3, 'text 2')._confirm()
        self.check_html_ok(self.client.get(url('accounts:friends:')), texts=[('pgf-no-friends-message', 0),
                                                                             (self.account_2.nick, 1),
                                                                             (self.account_3.nick, 1)])

    def test_candidates__friends_only(self):
        FriendshipPrototype.request_friendship(self.account_1, self.account_2, 'text 1')._confirm()
        FriendshipPrototype.request_friendship(self.account_1, self.account_3, 'text 2')._confirm()
        self.check_html_ok(self.client.get(url('accounts:friends:candidates')), texts=[('pgf-no-candidates-message', 1),
                                                                                       (self.account_2.nick, 0),
                                                                                       (self.account_3.nick, 0)])

    def test_candidates__no_candidates(self):
        self.check_html_ok(self.client.get(url('accounts:friends:candidates')), texts=['pgf-no-candidates-message'])

    def test_candidates(self):
        FriendshipPrototype.request_friendship(self.account_1, self.account_2, 'text 1')
        FriendshipPrototype.request_friendship(self.account_3, self.account_1, 'text 2')
        self.check_html_ok(self.client.get(url('accounts:friends:candidates')), texts=[('pgf-no-candidates-message', 0),
                                                                                       (self.account_2.nick, 0),
                                                                                       (self.account_3.nick, 1)])

    def test_friends__candidates_only(self):
        FriendshipPrototype.request_friendship(self.account_1, self.account_2, 'text 1')
        FriendshipPrototype.request_friendship(self.account_1, self.account_3, 'text 2')
        self.check_html_ok(self.client.get(url('accounts:friends:')), texts=[('pgf-no-friends-message', 1),
                                                                             (self.account_2.nick, 0),
                                                                             (self.account_3.nick, 0)])

    def test_request_dialog(self):
        self.check_html_ok(self.client.get(url('accounts:friends:request', friend=self.account_2.id)))

    def test_request_friendship_form_error(self):
        self.check_ajax_error(self.client.post(url('accounts:friends:request', friend=self.account_2.id), {}),
                              'friends.request_friendship.form_errors')
        self.assertEqual(Friendship.objects.all().count(), 0)

    def test_request_friendship(self):
        self.check_ajax_ok(self.client.post(url('accounts:friends:request', friend=self.account_2.id), {'text': 'text 1'}))
        self.assertEqual(Friendship.objects.all().count(), 1)
        self.assertFalse(Friendship.objects.all()[0].is_confirmed)

    def test_request_friendship__fast_friend(self):
        self.account_2.is_fast = True
        self.account_2.save()

        self.check_ajax_error(self.client.post(url('accounts:friends:request', friend=self.account_2.id), {'text': 'text 1'}),
                              'friends.request_friendship.fast_friend')
        self.assertEqual(Friendship.objects.all().count(), 0)

    def test_remove_friendship(self):
        FriendshipPrototype.request_friendship(self.account_1, self.account_2, 'text 1')._confirm()
        self.check_ajax_ok(self.client.post(url('accounts:friends:remove', friend=self.account_2.id)))
        self.assertEqual(Friendship.objects.all().count(), 0)
