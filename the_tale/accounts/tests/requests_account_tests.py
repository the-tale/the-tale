# coding: utf-8

from django.core.urlresolvers import reverse

from common.utils.testcase import TestCase
from common.utils.permissions import sync_group

from game.logic import create_test_map

from accounts.models import Award, AWARD_TYPE
from accounts.prototypes import AccountPrototype
from accounts.logic import register_user
from accounts.conf import accounts_settings


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
        texts = [('pgf-account-moderator-block', 0)]
        self.check_html_ok(self.client.get(reverse('accounts:show', args=[self.account1.id])), texts=texts)

    def test_fast_account(self):
        self.check_html_ok(self.client.get(reverse('accounts:show', args=[self.account4.id])))

    def test_show_for_moderator(self):
        self.request_login('test_user3@test.com')

        group = sync_group('accounts moderators group', ['accounts.moderate_account'])
        group.user_set.add(self.account3.user)

        texts = [('pgf-account-moderator-block', 1)]
        self.check_html_ok(self.client.get(reverse('accounts:show', args=[self.account1.id])), texts=texts)

    def test_404(self):
        self.check_html_ok(self.client.get(reverse('accounts:show', args=['adasd'])), status_code=404)
        self.check_html_ok(self.client.get(reverse('accounts:show', args=[666])), status_code=404)


class GiveAwardRequestsTests(AccountRequestsTests):

    def setUp(self):
        super(GiveAwardRequestsTests, self).setUp()

        group = sync_group('accounts moderators group', ['accounts.moderate_account'])
        group.user_set.add(self.account3.user)

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
        group.user_set.add(self.account3.user)

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
        self.check_ajax_ok(self.client.post(reverse('accounts:reset-nick', args=[self.account1.id])))
        self.assertNotEqual(old_nick, AccountPrototype.get_by_id(self.account1.id).nick)
