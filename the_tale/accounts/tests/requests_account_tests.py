# coding: utf-8

from django.core.urlresolvers import reverse

from common.utils.testcase import TestCase
from common.utils.permissions import sync_group
from common.postponed_tasks import PostponedTaskPrototype

from game.logic import create_test_map

from accounts.friends.prototypes import FriendshipPrototype

from accounts.models import Award
from accounts.prototypes import AccountPrototype, ChangeCredentialsTaskPrototype
from accounts.relations import AWARD_TYPE
from accounts.logic import register_user
from accounts.conf import accounts_settings

from game.heroes.prototypes import HeroPrototype

class AccountRequestsTests(TestCase):

    def setUp(self):
        super(AccountRequestsTests, self).setUp()
        self.place1, self.place2, self.place3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user1', 'test_user1@test.com', '111111')
        self.account1 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user2', 'test_user2@test.com', '111111')
        self.account2 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user3', 'test_user3@test.com', '111111')
        self.account3 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user4')
        self.account4 = AccountPrototype.get_by_id(account_id)


class IndexRequestsTests(AccountRequestsTests):

    def test_index(self):
        self.check_html_ok(self.client.get(reverse('accounts:')), texts=(('pgf-account-record', 3),
                                                                         ('test_user1', 1),
                                                                         ('test_user2', 1),
                                                                         ('test_user3', 1),))

    def test_index_pagination(self):
        for i in xrange(accounts_settings.ACCOUNTS_ON_PAGE):
            register_user('test_user_%d' % i, 'test_user_%d@test.com' % i, '111111')
        self.check_html_ok(self.client.get(reverse('accounts:')), texts=(('pgf-account-record', accounts_settings.ACCOUNTS_ON_PAGE),))
        self.check_html_ok(self.client.get(reverse('accounts:')+'?page=2'), texts=(('pgf-account-record', 3),))

    def test_index_redirect_from_large_page(self):
        self.check_redirect(reverse('accounts:')+'?page=2', reverse('accounts:')+'?page=1')


class ShowRequestsTests(AccountRequestsTests):

    def test_show(self):
        texts = [('pgf-account-moderator-block', 0),
                 ('pgf-friends-request-friendship', 0),
                 ('pgf-friends-in-list', 0),
                 ('pgf-friends-request-from', 0),
                 ('pgf-friends-request-to', 0),
                 ('pgf-no-common-places-message', 1)]
        self.check_html_ok(self.client.get(reverse('accounts:show', args=[self.account1.id])), texts=texts)

    def test_show__places_history(self):
        texts = [(self.place1.name, 1),
                 (self.place2.name, 1),
                 (self.place3.name, 0),
                 ('pgf-no-common-places-message', 0)]

        hero = HeroPrototype.get_by_account_id(self.account1.id)
        hero.places_history.add_place(self.place1.id)
        hero.places_history.add_place(self.place2.id)
        hero.places_history.add_place(self.place1.id)
        hero.save()

        self.check_html_ok(self.client.get(reverse('accounts:show', args=[self.account1.id])), texts=texts)

    def test_show_friends_no_friendship(self):
        self.request_login('test_user2@test.com')
        texts = [('pgf-friends-request-friendship', 2), # +1 from javascript
                 ('pgf-friends-in-list', 0),
                 ('pgf-friends-request-from', 0),
                 ('pgf-friends-request-to', 0)]
        self.check_html_ok(self.client.get(reverse('accounts:show', args=[self.account1.id])), texts=texts)

    def test_show_friends_in_list_button(self):
        self.request_login('test_user2@test.com')
        texts = [('pgf-friends-request-friendship', 0),
                 ('pgf-friends-in-list', 1),
                 ('pgf-friends-request-from', 0),
                 ('pgf-friends-request-to', 0)]
        FriendshipPrototype.request_friendship(self.account2, self.account1, text=u'text')._confirm()
        self.check_html_ok(self.client.get(reverse('accounts:show', args=[self.account1.id])), texts=texts)

    def test_show_friends_request_from_button(self):
        self.request_login('test_user2@test.com')
        texts = [('pgf-friends-request-friendship', 0),
                 ('pgf-friends-in-list', 0),
                 ('pgf-friends-request-from', 1),
                 ('pgf-friends-request-to', 0)]
        FriendshipPrototype.request_friendship(self.account1, self.account2, text=u'text')
        self.check_html_ok(self.client.get(reverse('accounts:show', args=[self.account1.id])), texts=texts)

    def test_show_friends_request_to_button(self):
        self.request_login('test_user2@test.com')
        texts = [('pgf-friends-request-friendship', 0),
                 ('pgf-friends-in-list', 0),
                 ('pgf-friends-request-from', 0),
                 ('pgf-friends-request-to', 1)]
        FriendshipPrototype.request_friendship(self.account2, self.account1, text=u'text')
        self.check_html_ok(self.client.get(reverse('accounts:show', args=[self.account1.id])), texts=texts)

    def test_fast_account(self):
        self.check_html_ok(self.client.get(reverse('accounts:show', args=[self.account4.id])))

    def test_show_for_moderator(self):
        self.request_login('test_user3@test.com')

        group = sync_group('accounts moderators group', ['accounts.moderate_account'])
        group.account_set.add(self.account3._model)

        texts = [('pgf-account-moderator-block', 1)]
        self.check_html_ok(self.client.get(reverse('accounts:show', args=[self.account1.id])), texts=texts)

    def test_404(self):
        self.check_html_ok(self.client.get(reverse('accounts:show', args=['adasd'])), status_code=404)
        self.check_html_ok(self.client.get(reverse('accounts:show', args=[666])), status_code=404)


class GiveAwardRequestsTests(AccountRequestsTests):

    def setUp(self):
        super(GiveAwardRequestsTests, self).setUp()

        group = sync_group('accounts moderators group', ['accounts.moderate_account'])
        group.account_set.add(self.account3._model)

        self.request_login('test_user3@test.com')


    def test_no_rights(self):
        self.request_logout()
        self.request_login('test_user2@test.com')

        self.check_ajax_error(self.client.post(reverse('accounts:give-award', args=[self.account1.id]), {'type': AWARD_TYPE.BUG_MINOR}),
                              'accounts.account.moderator_rights_required')

        self.assertEqual(Award.objects.all().count(), 0)


    def test_form_errors(self):
        self.check_ajax_error(self.client.post(reverse('accounts:give-award', args=[self.account1.id]), {'type': '666'}),
                              'accounts.account.give_award.form_errors')
        self.assertEqual(Award.objects.all().count(), 0)

    def test_success(self):
        self.check_ajax_ok(self.client.post(reverse('accounts:give-award', args=[self.account1.id]), {'type': AWARD_TYPE.BUG_MINOR}))
        self.assertEqual(Award.objects.all().count(), 1)

        award = Award.objects.all()[0]

        self.assertEqual(award.type, AWARD_TYPE.BUG_MINOR)
        self.assertEqual(award.account_id, self.account1.id)


class ResetNickdRequestsTests(AccountRequestsTests):

    def setUp(self):
        super(ResetNickdRequestsTests, self).setUp()

        group = sync_group('accounts moderators group', ['accounts.moderate_account'])
        group.account_set.add(self.account3._model)

        self.request_login('test_user3@test.com')


    def test_no_rights(self):
        self.request_logout()
        self.request_login('test_user2@test.com')

        old_nick = self.account1.nick

        self.check_ajax_error(self.client.post(reverse('accounts:reset-nick', args=[self.account1.id])),
                              'accounts.account.moderator_rights_required')

        self.assertEqual(old_nick, AccountPrototype.get_by_id(self.account1.id).nick)

    def test_success(self):
        old_nick = self.account1.nick

        response = self.client.post(reverse('accounts:reset-nick', args=[self.account1.id]))

        postponed_task = PostponedTaskPrototype._db_get_object(0)

        self.check_ajax_processing(response, reverse('postponed-tasks:status', args=[postponed_task.id]))

        task = ChangeCredentialsTaskPrototype._db_get_object(0)

        self.assertFalse(task.relogin_required)
        self.assertEqual(self.account1.id, task.account.id)
        self.assertNotEqual(self.account1.nick, task.new_nick)

        self.assertEqual(old_nick, AccountPrototype.get_by_id(self.account1.id).nick)
