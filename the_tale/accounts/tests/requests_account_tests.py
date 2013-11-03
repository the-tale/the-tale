# coding: utf-8
import mock
import random

from django.core.urlresolvers import reverse

from dext.utils.urls import url

from the_tale.common.utils.testcase import TestCase
from the_tale.common.utils.permissions import sync_group
from the_tale.common.postponed_tasks import PostponedTaskPrototype

from the_tale.game.logic import create_test_map

from the_tale.accounts.friends.prototypes import FriendshipPrototype
from the_tale.accounts.personal_messages.prototypes import MessagePrototype

from the_tale.accounts.models import Award
from the_tale.accounts.prototypes import AccountPrototype, ChangeCredentialsTaskPrototype
from the_tale.accounts.relations import AWARD_TYPE, BAN_TYPE, BAN_TIME
from the_tale.accounts.logic import register_user, login_url
from the_tale.accounts.conf import accounts_settings

from the_tale.accounts.clans.prototypes import ClanPrototype
from the_tale.accounts.clans.conf import clans_settings

from the_tale.forum.prototypes import CategoryPrototype

from the_tale.game.heroes.prototypes import HeroPrototype

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

        result, account_id, bundle_id = register_user('test_user_bot', 'test_user_bot@test.com', '111111', is_bot=True)
        self.account_bot = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user4')
        self.account4 = AccountPrototype.get_by_id(account_id)

        CategoryPrototype.create(caption='category-1', slug=clans_settings.FORUM_CATEGORY_SLUG, order=0)

        self.clan_2 = ClanPrototype.create(self.account2, abbr=u'abbr2', name=u'name2', motto=u'motto', description=u'description')
        self.clan_3 = ClanPrototype.create(self.account3, abbr=u'abbr3', name=u'name3', motto=u'motto', description=u'description')


class IndexRequestsTests(AccountRequestsTests):

    def test_index(self):
        self.check_html_ok(self.request_html(reverse('accounts:')), texts=(('pgf-account-record', 3),
                                                                           ('test_user1', 1),
                                                                           ('test_user2', 1),
                                                                           ('test_user_bot', 0),
                                                                           ('test_user3', 1),
                                                                           ('abbr2', 1),
                                                                           ('abbr3', 1)))

    def test_index_pagination(self):
        for i in xrange(accounts_settings.ACCOUNTS_ON_PAGE):
            register_user('test_user_%d' % i, 'test_user_%d@test.com' % i, '111111')
        self.check_html_ok(self.request_html(reverse('accounts:')), texts=(('pgf-account-record', accounts_settings.ACCOUNTS_ON_PAGE),))
        self.check_html_ok(self.request_html(reverse('accounts:')+'?page=2'), texts=(('pgf-account-record', 3),))

    def test_index_redirect_from_large_page(self):
        self.check_redirect(url('accounts:', page=2), url('accounts:', page=1, prefix=''))

    def test_accounts_not_found_message(self):
        self.check_html_ok(self.request_html(url('accounts:', prefix='ac')), texts=(('pgf-account-record', 0),
                                                                                  ('pgf-no-accounts-message', 1),
                                                                                  ('test_user_bot', 0),
                                                                                  ('test_user1', 0),
                                                                                  ('test_user2', 0),
                                                                                  ('test_user3', 0),))

    def test_accounts_search_by_prefix(self):
        texts = [('pgf-account-record', 6),
                 ('pgf-no-accounts-message', 0),]
        for i in xrange(accounts_settings.ACCOUNTS_ON_PAGE):
            register_user('test_user_a_%d' % i, 'test_user_a_%d@test.com' % i, '111111')
            texts.append(('test_user_a_%d' % i, 0))
        for i in xrange(6):
            register_user('test_user_b_%d' % i, 'test_user_b_%d@test.com' % i, '111111')
            texts.append(('test_user_b_%d' % i, 1))

        self.check_html_ok(self.request_html(url('accounts:', prefix='test_user_b')), texts=texts)

    def test_accounts_search_by_prefix_second_page(self):
        texts = [('pgf-account-record', 6),
                 ('pgf-no-accounts-message', 0),]
        for i in xrange(accounts_settings.ACCOUNTS_ON_PAGE):
            register_user('test_user_a_%d' % i, 'test_user_a_%d@test.com' % i, '111111')
            texts.append(('test_user_a_%d' % i, 0))
        for i in xrange(6):
            register_user('test_user_b_%d' % i, 'test_user_b_%d@test.com' % i, '111111')
            texts.append(('test_user_b_%d' % i, 1))

        for i in xrange(accounts_settings.ACCOUNTS_ON_PAGE):
            register_user('test_user_b2_%d' % i, 'test_user_b2_%d@test.com' % i, '111111')
            texts.append(('test_user_b2_%d' % i, 0))

        self.check_html_ok(self.request_html(url('accounts:', prefix='test_user_b', page=2)), texts=texts)


class ShowRequestsTests(AccountRequestsTests):

    def test_show(self):
        texts = [('pgf-account-admin-link', 0),
                 ('pgf-friends-request-friendship', 0),
                 ('pgf-friends-in-list', 0),
                 ('pgf-friends-request-from', 0),
                 ('pgf-friends-request-to', 0),
                 ('pgf-no-common-places-message', 1),
                 ('pgf-ban-forum-message', 0),
                 ('pgf-ban-game-message', 0)]
        self.check_html_ok(self.request_html(reverse('accounts:show', args=[self.account1.id])), texts=texts)

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_ban_game', True)
    def test_show__ban_game(self):
        texts = [('pgf-ban-forum-message', 0),
                 ('pgf-ban-game-message', 1)]
        self.check_html_ok(self.request_html(reverse('accounts:show', args=[self.account1.id])), texts=texts)

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_ban_forum', True)
    def test_show__ban_forum(self):
        texts = [('pgf-ban-forum-message', 1),
                 ('pgf-ban-game-message', 0)]
        self.check_html_ok(self.request_html(reverse('accounts:show', args=[self.account1.id])), texts=texts)

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

        self.check_html_ok(self.request_html(reverse('accounts:show', args=[self.account1.id])), texts=texts)

    def test_show_friends_no_friendship(self):
        self.request_login('test_user2@test.com')
        texts = [('pgf-friends-request-friendship', 2), # +1 from javascript
                 ('pgf-friends-in-list', 0),
                 ('pgf-friends-request-from', 0),
                 ('pgf-friends-request-to', 0)]
        self.check_html_ok(self.request_html(reverse('accounts:show', args=[self.account1.id])), texts=texts)

    def test_show_friends_in_list_button(self):
        self.request_login('test_user2@test.com')
        texts = [('pgf-friends-request-friendship', 0),
                 ('pgf-friends-in-list', 1),
                 ('pgf-friends-request-from', 0),
                 ('pgf-friends-request-to', 0)]
        FriendshipPrototype.request_friendship(self.account2, self.account1, text=u'text')._confirm()
        self.check_html_ok(self.request_html(reverse('accounts:show', args=[self.account1.id])), texts=texts)

    def test_show_friends_request_from_button(self):
        self.request_login('test_user2@test.com')
        texts = [('pgf-friends-request-friendship', 0),
                 ('pgf-friends-in-list', 0),
                 ('pgf-friends-request-from', 1),
                 ('pgf-friends-request-to', 0)]
        FriendshipPrototype.request_friendship(self.account1, self.account2, text=u'text')
        self.check_html_ok(self.request_html(reverse('accounts:show', args=[self.account1.id])), texts=texts)

    def test_show_friends_request_to_button(self):
        self.request_login('test_user2@test.com')
        texts = [('pgf-friends-request-friendship', 0),
                 ('pgf-friends-in-list', 0),
                 ('pgf-friends-request-from', 0),
                 ('pgf-friends-request-to', 1)]
        FriendshipPrototype.request_friendship(self.account2, self.account1, text=u'text')
        self.check_html_ok(self.request_html(reverse('accounts:show', args=[self.account1.id])), texts=texts)

    def test_fast_account(self):
        self.check_html_ok(self.request_html(reverse('accounts:show', args=[self.account4.id])))

    def test_show_for_moderator(self):
        self.request_login('test_user3@test.com')

        group = sync_group('accounts moderators group', ['accounts.moderate_account'])
        group.account_set.add(self.account3._model)

        texts = [('pgf-account-admin-link', 1)]
        self.check_html_ok(self.request_html(reverse('accounts:show', args=[self.account1.id])), texts=texts)

    def test_404(self):
        self.check_html_ok(self.request_html(reverse('accounts:show', args=['adasd'])), texts=['accounts.account.account.wrong_format'])
        self.check_html_ok(self.request_html(reverse('accounts:show', args=[666])), status_code=404, texts=['accounts.account.account.not_found'])


class AdminRequestsTests(AccountRequestsTests):

    def setUp(self):
        super(AdminRequestsTests, self).setUp()

        self.request_login('test_user3@test.com')
        group = sync_group('accounts moderators group', ['accounts.moderate_account'])
        group.account_set.add(self.account3._model)


    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_ban_game', True)
    def test_ban_game(self):
        texts = [('pgf-ban-forum-message', 0),
                 ('pgf-ban-game-message', 1)]
        self.check_html_ok(self.request_html(reverse('accounts:admin', args=[self.account1.id])), texts=texts)

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_ban_forum', True)
    def test_ban_forum(self):
        texts = [('pgf-ban-forum-message', 1),
                 ('pgf-ban-game-message', 0)]
        self.check_html_ok(self.request_html(reverse('accounts:admin', args=[self.account1.id])), texts=texts)

    def test_unlogined(self):
        self.request_logout()
        requested_url = url('accounts:admin', self.account1.id)
        self.check_redirect(requested_url, login_url(requested_url))

    def test_no_rights(self):
        self.request_login('test_user2@test.com')
        self.check_html_ok(self.request_html(reverse('accounts:admin', args=[self.account1.id])), texts=[('accounts.account.moderator_rights_required', 1)])

    def test_moderator(self):
        self.check_html_ok(self.request_html(reverse('accounts:admin', args=[self.account1.id])), texts=[('accounts.account.moderator_rights_required', 0)])

    def test_404(self):
        self.check_html_ok(self.request_html(reverse('accounts:admin', args=['adasd'])), texts=['accounts.account.account.wrong_format'])
        self.check_html_ok(self.request_html(reverse('accounts:admin', args=[666])), status_code=404, texts=['accounts.account.account.not_found'])


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


class ResetNickRequestsTests(AccountRequestsTests):

    def setUp(self):
        super(ResetNickRequestsTests, self).setUp()

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


class BanRequestsTests(AccountRequestsTests):

    def setUp(self):
        super(BanRequestsTests, self).setUp()

        group = sync_group('accounts moderators group', ['accounts.moderate_account'])
        group.account_set.add(self.account3._model)

        self.request_login('test_user3@test.com')

    def form_data(self, ban_type, description=u'ban-description'):
        return {'ban_type': ban_type,
                'ban_time': random.choice(BAN_TIME._records),
                'description': description}

    def test_no_rights(self):
        self.request_logout()
        self.request_login('test_user2@test.com')

        self.check_ajax_error(self.client.post(reverse('accounts:ban', args=[self.account1.id]), self.form_data(BAN_TYPE.FORUM)),
                              'accounts.account.moderator_rights_required')

        self.account1.reload()
        self.assertFalse(self.account1.is_ban_forum)
        self.assertFalse(self.account1.is_ban_game)
        self.assertEqual(MessagePrototype._db_count(), 0)

    def test_form_errors(self):
        self.check_ajax_error(self.client.post(reverse('accounts:ban', args=[self.account1.id]), self.form_data(BAN_TYPE.FORUM, description=u'')),
                              'accounts.account.ban.form_errors')

        self.account1.reload()
        self.assertFalse(self.account1.is_ban_forum)
        self.assertFalse(self.account1.is_ban_game)
        self.assertEqual(MessagePrototype._db_count(), 0)

    def test_success__ban_forum(self):
        self.check_ajax_ok(self.client.post(reverse('accounts:ban', args=[self.account1.id]), self.form_data(BAN_TYPE.FORUM)))

        self.account1.reload()
        self.assertTrue(self.account1.is_ban_forum)
        self.assertFalse(self.account1.is_ban_game)
        self.assertEqual(MessagePrototype._db_count(), 1)

    def test_success__ban_game(self):
        self.check_ajax_ok(self.client.post(reverse('accounts:ban', args=[self.account1.id]), self.form_data(BAN_TYPE.GAME)))

        self.account1.reload()
        self.assertFalse(self.account1.is_ban_forum)
        self.assertTrue(self.account1.is_ban_game)
        self.assertEqual(MessagePrototype._db_count(), 1)

    def test_success__ban_total(self):
        self.check_ajax_ok(self.client.post(reverse('accounts:ban', args=[self.account1.id]), self.form_data(BAN_TYPE.TOTAL)))

        self.account1.reload()
        self.assertTrue(self.account1.is_ban_forum)
        self.assertTrue(self.account1.is_ban_game)
        self.assertEqual(MessagePrototype._db_count(), 1)


class ResetBansRequestsTests(AccountRequestsTests):

    def setUp(self):
        super(ResetBansRequestsTests, self).setUp()

        group = sync_group('accounts moderators group', ['accounts.moderate_account'])
        group.account_set.add(self.account3._model)

        self.request_login('test_user3@test.com')

        self.account1.ban_game(1)
        self.account1.ban_forum(1)

    def test_no_rights(self):
        self.request_logout()
        self.request_login('test_user2@test.com')

        self.check_ajax_error(self.client.post(reverse('accounts:reset-bans', args=[self.account1.id])),
                              'accounts.account.moderator_rights_required')

        self.account1.reload()
        self.assertTrue(self.account1.is_ban_forum)
        self.assertTrue(self.account1.is_ban_game)

    def test_success(self):
        self.check_ajax_ok(self.client.post(reverse('accounts:reset-bans', args=[self.account1.id])))

        self.account1.reload()
        self.assertFalse(self.account1.is_ban_forum)
        self.assertFalse(self.account1.is_ban_game)
