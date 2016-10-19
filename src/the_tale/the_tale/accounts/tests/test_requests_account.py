# coding: utf-8
from unittest import mock
import random

from django.core.urlresolvers import reverse
from django.conf import settings as project_settings

from dext.common.utils.urls import url

from the_tale.common.utils.testcase import TestCase
from the_tale.common.utils.permissions import sync_group
from the_tale.common.postponed_tasks.prototypes import PostponedTaskPrototype

from the_tale.game.logic import create_test_map

from the_tale.finances.bank import prototypes as bank_prototypes
from the_tale.finances.bank import relations as bank_relations

from the_tale.accounts.friends.prototypes import FriendshipPrototype
from the_tale.accounts.personal_messages.prototypes import MessagePrototype

from ..models import Award
from ..prototypes import AccountPrototype, ChangeCredentialsTaskPrototype
from ..relations import AWARD_TYPE, BAN_TYPE, BAN_TIME
from .. import logic
from .. import conf
from .. import meta_relations

from the_tale.accounts.clans.prototypes import ClanPrototype
from the_tale.accounts.clans.conf import clans_settings

from the_tale.forum.prototypes import CategoryPrototype

from the_tale.game.heroes import logic as heroes_logic


class AccountRequestsTests(TestCase):

    def setUp(self):
        super(AccountRequestsTests, self).setUp()
        self.place1, self.place2, self.place3 = create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()
        self.account_3 = self.accounts_factory.create_account()
        self.account_4 = self.accounts_factory.create_account(is_fast=True)
        self.account_bot = self.accounts_factory.create_account(is_bot=True)

        CategoryPrototype.create(caption='category-1', slug=clans_settings.FORUM_CATEGORY_SLUG, order=0)

        self.clan_2 = ClanPrototype.create(self.account_2, abbr='abbr2', name='name2', motto='motto', description='description')
        self.clan_3 = ClanPrototype.create(self.account_3, abbr='abbr3', name='name3', motto='motto', description='description')


class IndexRequestsTests(AccountRequestsTests):

    def test_index(self):
        self.check_html_ok(self.request_html(reverse('accounts:')), texts=(('pgf-account-record', 3),
                                                                           (self.account_1.nick, 1),
                                                                           (self.account_2.nick, 1),
                                                                           (self.account_bot.nick, 0),
                                                                           (self.account_3.nick, 1),
                                                                           ('abbr2', 1),
                                                                           ('abbr3', 1)))

    def test_index_pagination(self):
        for i in range(conf.accounts_settings.ACCOUNTS_ON_PAGE):
            self.accounts_factory.create_account()
        self.check_html_ok(self.request_html(reverse('accounts:')), texts=(('pgf-account-record', conf.accounts_settings.ACCOUNTS_ON_PAGE),))
        self.check_html_ok(self.request_html(reverse('accounts:')+'?page=2'), texts=(('pgf-account-record', 3),))

    def test_index_redirect_from_large_page(self):
        self.check_redirect(url('accounts:', page=2), url('accounts:', page=1))

    def test_accounts_not_found_message(self):
        self.check_html_ok(self.request_html(url('accounts:', prefix='ac')), texts=(('pgf-account-record', 0),
                                                                                    ('pgf-no-accounts-message', 1),
                                                                                    (self.account_bot.nick, 0),
                                                                                    (self.account_1.nick, 0),
                                                                                    (self.account_2.nick, 0),
                                                                                    (self.account_3.nick, 0),))

    def test_accounts_search_by_prefix(self):
        texts = [('pgf-account-record', 6),
                 ('pgf-no-accounts-message', 0),]

        for i in range(conf.accounts_settings.ACCOUNTS_ON_PAGE):
            account = self.accounts_factory.create_account(nick='test_user_a_%d' % i)
            texts.append((account.nick, 0))

        for i in range(6):
            account = self.accounts_factory.create_account(nick='test_user_b_%d' % i)
            texts.append((account.nick, 1))

        self.check_html_ok(self.request_html(url('accounts:', prefix='test_user_b')), texts=texts)

    def test_accounts_search_by_prefix_second_page(self):
        texts = [('pgf-account-record', 6),
                 ('pgf-no-accounts-message', 0),]

        for i in range(conf.accounts_settings.ACCOUNTS_ON_PAGE):
            account = self.accounts_factory.create_account(nick='test_user_a_%d' % i)
            texts.append((account.nick, 0))

        for i in range(6):
            account = self.accounts_factory.create_account(nick='test_user_b_%d' % i)
            texts.append((account.nick, 1))

        for i in range(conf.accounts_settings.ACCOUNTS_ON_PAGE):
            account = self.accounts_factory.create_account(nick='test_user_b2_%d' % i)
            texts.append((account.nick, 0))

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
        self.check_html_ok(self.request_html(reverse('accounts:show', args=[self.account_1.id])), texts=texts)

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_ban_game', True)
    def test_show__ban_game(self):
        texts = [('pgf-ban-forum-message', 0),
                 ('pgf-ban-game-message', 1)]
        self.check_html_ok(self.request_html(reverse('accounts:show', args=[self.account_1.id])), texts=texts)

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_ban_forum', True)
    def test_show__ban_forum(self):
        texts = [('pgf-ban-forum-message', 1),
                 ('pgf-ban-game-message', 0)]
        self.check_html_ok(self.request_html(reverse('accounts:show', args=[self.account_1.id])), texts=texts)

    def test_show__places_history(self):
        texts = [(self.place1.name, 1),
                 (self.place2.name, 1),
                 (self.place3.name, 0),
                 ('pgf-no-common-places-message', 0)]

        hero = heroes_logic.load_hero(account_id=self.account_1.id)
        hero.places_history.add_place(self.place1.id)
        hero.places_history.add_place(self.place2.id)
        hero.places_history.add_place(self.place1.id)
        heroes_logic.save_hero(hero)

        self.check_html_ok(self.request_html(reverse('accounts:show', args=[self.account_1.id])), texts=texts)

    def test_show_friends_no_friendship(self):
        self.request_login(self.account_2.email)
        texts = [('pgf-friends-request-friendship', 2), # +1 from javascript
                 ('pgf-friends-in-list', 0),
                 ('pgf-friends-request-from', 0),
                 ('pgf-friends-request-to', 0)]
        self.check_html_ok(self.request_html(reverse('accounts:show', args=[self.account_1.id])), texts=texts)

    def test_show_friends_in_list_button(self):
        self.request_login(self.account_2.email)
        texts = [('pgf-friends-request-friendship', 0),
                 ('pgf-friends-in-list', 1),
                 ('pgf-friends-request-from', 0),
                 ('pgf-friends-request-to', 0)]
        FriendshipPrototype.request_friendship(self.account_2, self.account_1, text='text')._confirm()
        self.check_html_ok(self.request_html(reverse('accounts:show', args=[self.account_1.id])), texts=texts)

    def test_show_friends_request_from_button(self):
        self.request_login(self.account_2.email)
        texts = [('pgf-friends-request-friendship', 0),
                 ('pgf-friends-in-list', 0),
                 ('pgf-friends-request-from', 1),
                 ('pgf-friends-request-to', 0)]
        FriendshipPrototype.request_friendship(self.account_1, self.account_2, text='text')
        self.check_html_ok(self.request_html(reverse('accounts:show', args=[self.account_1.id])), texts=texts)

    def test_show_friends_request_to_button(self):
        self.request_login(self.account_2.email)
        texts = [('pgf-friends-request-friendship', 0),
                 ('pgf-friends-in-list', 0),
                 ('pgf-friends-request-from', 0),
                 ('pgf-friends-request-to', 1)]
        FriendshipPrototype.request_friendship(self.account_2, self.account_1, text='text')
        self.check_html_ok(self.request_html(reverse('accounts:show', args=[self.account_1.id])), texts=texts)

    def test_show_folclor(self):
        from the_tale.blogs.tests import helpers as blogs_helpers

        blogs_helpers.prepair_forum()

        blogs_helpers.create_post_for_meta_object(self.account_2, 'folclor-1-caption', 'folclor-1-text',
                                                  meta_relations.Account.create_from_object(self.account_1), vote_by=self.account_1)
        blogs_helpers.create_post_for_meta_object(self.account_3, 'folclor-2-caption', 'folclor-2-text',
                                                  meta_relations.Account.create_from_object(self.account_1), vote_by=self.account_1)
        blogs_helpers.create_post_for_meta_object(self.account_3, 'folclor-3-caption', 'folclor-3-text', meta_relations.Account.create_from_object(self.account_1))

        self.request_login(self.account_2.email)

        self.check_html_ok(self.request_html(reverse('accounts:show', args=[self.account_1.id])),
                           texts=[('pgf-no-folclor', 0), 'folclor-1-caption', 'folclor-2-caption', ('folclor-3-caption', 0)])

    def test_show_no_folclor(self):
        from the_tale.blogs.tests import helpers as blogs_helpers

        blogs_helpers.prepair_forum()

        blogs_helpers.create_post_for_meta_object(self.account_2, 'folclor-1-caption', 'folclor-1-text',
                                                  meta_relations.Account.create_from_object(self.account_1), vote_by=self.account_1)
        blogs_helpers.create_post_for_meta_object(self.account_3, 'folclor-2-caption', 'folclor-2-text',
                                                  meta_relations.Account.create_from_object(self.account_1), vote_by=self.account_1)
        blogs_helpers.create_post_for_meta_object(self.account_3, 'folclor-3-caption', 'folclor-3-text', meta_relations.Account.create_from_object(self.account_1))

        self.request_login(self.account_2.email)

        self.check_html_ok(self.request_html(reverse('accounts:show', args=[self.account_2.id])),
                           texts=['pgf-no-folclor', ('folclor-1-caption', 0), ('folclor-2-caption', 0), ('folclor-3-caption', 0)])

    def test_fast_account(self):
        self.check_html_ok(self.request_html(reverse('accounts:show', args=[self.account_4.id])))

    def test_show_for_moderator(self):
        self.request_login(self.account_3.email)

        group = sync_group('accounts moderators group', ['accounts.moderate_account'])
        group.user_set.add(self.account_3._model)

        texts = [('pgf-account-admin-link', 1)]
        self.check_html_ok(self.request_html(reverse('accounts:show', args=[self.account_1.id])), texts=texts)

    def test_404(self):
        self.check_html_ok(self.request_html(reverse('accounts:show', args=['adasd'])), texts=['pgf-error-account.wrong_format'])
        self.check_html_ok(self.request_html(reverse('accounts:show', args=[666])), texts=['pgf-error-account.wrong_value'])


class ShowApiRequestsTests(AccountRequestsTests):

    def test_show(self):
        hero = heroes_logic.load_hero(account_id=self.account_1.id)
        self.check_ajax_ok(self.request_ajax_json(url('accounts:api-show', self.account_1.id, api_version='1.0', api_client=project_settings.API_CLIENT)),
                                                  data=logic.get_account_info(self.account_1, hero))

    def test_404(self):
        self.check_ajax_error(self.request_ajax_json(url('accounts:api-show', 666, api_version='1.0', api_client=project_settings.API_CLIENT)),
                              'account.wrong_value')


class AdminRequestsTests(AccountRequestsTests):

    def setUp(self):
        super(AdminRequestsTests, self).setUp()

        self.request_login(self.account_3.email)
        group = sync_group('accounts moderators group', ['accounts.moderate_account'])
        group.user_set.add(self.account_3._model)


    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_ban_game', True)
    def test_ban_game(self):
        texts = [('pgf-ban-forum-message', 0),
                 ('pgf-ban-game-message', 1)]
        self.check_html_ok(self.request_html(reverse('accounts:admin', args=[self.account_1.id])), texts=texts)

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_ban_forum', True)
    def test_ban_forum(self):
        texts = [('pgf-ban-forum-message', 1),
                 ('pgf-ban-game-message', 0)]
        self.check_html_ok(self.request_html(reverse('accounts:admin', args=[self.account_1.id])), texts=texts)

    def test_unlogined(self):
        self.request_logout()
        requested_url = url('accounts:admin', self.account_1.id)
        self.check_redirect(requested_url, logic.login_page_url(requested_url))

    def test_no_rights(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(reverse('accounts:admin', args=[self.account_1.id])), texts=[('accounts.no_moderation_rights', 1)])

    def test_moderator(self):
        self.check_html_ok(self.request_html(reverse('accounts:admin', args=[self.account_1.id])), texts=[('accounts.no_moderation_rights', 0)])

    def test_404(self):
        self.check_html_ok(self.request_html(reverse('accounts:admin', args=['adasd'])), texts=['pgf-error-account.wrong_format'])
        self.check_html_ok(self.request_html(reverse('accounts:admin', args=[666])), texts=['pgf-error-account.wrong_value'])


class GiveAwardRequestsTests(AccountRequestsTests):

    def setUp(self):
        super(GiveAwardRequestsTests, self).setUp()

        group = sync_group('accounts moderators group', ['accounts.moderate_account'])
        group.user_set.add(self.account_3._model)

        self.request_login(self.account_3.email)


    def test_no_rights(self):
        self.request_logout()
        self.request_login(self.account_2.email)

        self.check_ajax_error(self.client.post(reverse('accounts:give-award', args=[self.account_1.id]), {'type': AWARD_TYPE.BUG_MINOR}),
                              'accounts.no_moderation_rights')

        self.assertEqual(Award.objects.all().count(), 0)


    def test_form_errors(self):
        self.check_ajax_error(self.client.post(reverse('accounts:give-award', args=[self.account_1.id]), {'type': '666'}),
                              'form_errors')
        self.assertEqual(Award.objects.all().count(), 0)

    def test_success(self):
        self.check_ajax_ok(self.client.post(reverse('accounts:give-award', args=[self.account_1.id]), {'type': AWARD_TYPE.BUG_MINOR}))
        self.assertEqual(Award.objects.all().count(), 1)

        award = Award.objects.all()[0]

        self.assertEqual(award.type, AWARD_TYPE.BUG_MINOR)
        self.assertEqual(award.account_id, self.account_1.id)


class ResetNickRequestsTests(AccountRequestsTests):

    def setUp(self):
        super(ResetNickRequestsTests, self).setUp()

        group = sync_group('accounts moderators group', ['accounts.moderate_account'])
        group.user_set.add(self.account_3._model)

        self.request_login(self.account_3.email)


    def test_no_rights(self):
        self.request_logout()
        self.request_login(self.account_2.email)

        old_nick = self.account_1.nick

        self.check_ajax_error(self.client.post(reverse('accounts:reset-nick', args=[self.account_1.id])),
                              'accounts.no_moderation_rights')

        self.assertEqual(old_nick, AccountPrototype.get_by_id(self.account_1.id).nick)

    def test_success(self):
        old_nick = self.account_1.nick

        response = self.client.post(reverse('accounts:reset-nick', args=[self.account_1.id]))

        postponed_task = PostponedTaskPrototype._db_get_object(0)

        self.check_ajax_processing(response, reverse('postponed-tasks:status', args=[postponed_task.id]))

        task = ChangeCredentialsTaskPrototype._db_get_object(0)

        self.assertFalse(task.relogin_required)
        self.assertEqual(self.account_1.id, task.account.id)
        self.assertNotEqual(self.account_1.nick, task.new_nick)

        self.assertEqual(old_nick, AccountPrototype.get_by_id(self.account_1.id).nick)


class BanRequestsTests(AccountRequestsTests):

    def setUp(self):
        super(BanRequestsTests, self).setUp()

        group = sync_group('accounts moderators group', ['accounts.moderate_account'])
        group.user_set.add(self.account_3._model)

        self.request_login(self.account_3.email)

    def form_data(self, ban_type, description='ban-description'):
        return {'ban_type': ban_type,
                'ban_time': random.choice(BAN_TIME.records),
                'description': description}

    def test_no_rights(self):
        self.request_logout()
        self.request_login(self.account_2.email)

        self.check_ajax_error(self.client.post(reverse('accounts:ban', args=[self.account_1.id]), self.form_data(BAN_TYPE.FORUM)),
                              'accounts.no_moderation_rights')

        self.account_1.reload()
        self.assertFalse(self.account_1.is_ban_forum)
        self.assertFalse(self.account_1.is_ban_game)
        self.assertEqual(MessagePrototype._db_count(), 0)

    def test_form_errors(self):
        self.check_ajax_error(self.client.post(reverse('accounts:ban', args=[self.account_1.id]), self.form_data(BAN_TYPE.FORUM, description='')),
                              'form_errors')

        self.account_1.reload()
        self.assertFalse(self.account_1.is_ban_forum)
        self.assertFalse(self.account_1.is_ban_game)
        self.assertEqual(MessagePrototype._db_count(), 0)

    def test_success__ban_forum(self):
        self.check_ajax_ok(self.client.post(reverse('accounts:ban', args=[self.account_1.id]), self.form_data(BAN_TYPE.FORUM)))

        self.account_1.reload()
        self.assertTrue(self.account_1.is_ban_forum)
        self.assertFalse(self.account_1.is_ban_game)
        self.assertEqual(MessagePrototype._db_count(), 1)

    def test_success__ban_game(self):
        self.check_ajax_ok(self.client.post(reverse('accounts:ban', args=[self.account_1.id]), self.form_data(BAN_TYPE.GAME)))

        self.account_1.reload()
        self.assertFalse(self.account_1.is_ban_forum)
        self.assertTrue(self.account_1.is_ban_game)
        self.assertEqual(MessagePrototype._db_count(), 1)

    def test_success__ban_total(self):
        self.check_ajax_ok(self.client.post(reverse('accounts:ban', args=[self.account_1.id]), self.form_data(BAN_TYPE.TOTAL)))

        self.account_1.reload()
        self.assertTrue(self.account_1.is_ban_forum)
        self.assertTrue(self.account_1.is_ban_game)
        self.assertEqual(MessagePrototype._db_count(), 1)


class ResetBansRequestsTests(AccountRequestsTests):

    def setUp(self):
        super(ResetBansRequestsTests, self).setUp()

        group = sync_group('accounts moderators group', ['accounts.moderate_account'])
        group.user_set.add(self.account_3._model)

        self.request_login(self.account_3.email)

        self.account_1.ban_game(1)
        self.account_1.ban_forum(1)

    def test_no_rights(self):
        self.request_logout()
        self.request_login(self.account_2.email)

        self.check_ajax_error(self.client.post(reverse('accounts:reset-bans', args=[self.account_1.id])),
                              'accounts.no_moderation_rights')

        self.account_1.reload()
        self.assertTrue(self.account_1.is_ban_forum)
        self.assertTrue(self.account_1.is_ban_game)

    def test_success(self):
        self.check_ajax_ok(self.client.post(reverse('accounts:reset-bans', args=[self.account_1.id])))

        self.account_1.reload()
        self.assertFalse(self.account_1.is_ban_forum)
        self.assertFalse(self.account_1.is_ban_game)


class TransferMoneyDialogTests(AccountRequestsTests):

    def setUp(self):
        super(TransferMoneyDialogTests, self).setUp()

        self.request_login(self.account_1.email)

    def test_login_required(self):
        self.request_logout()
        self.check_html_ok(self.request_ajax_html(url('accounts:transfer-money-dialog', self.account_2.id)), texts=['pgf-error-common.login_required'])

    def test_full_sender_required(self):
        self.account_1.is_fast = True
        self.account_1.save()
        self.check_html_ok(self.request_ajax_html(url('accounts:transfer-money-dialog', self.account_2.id)), texts=['pgf-error-common.fast_account'])

    def test_full_receiver_required(self):
        self.account_2.is_fast = True
        self.account_2.save()
        self.check_html_ok(self.request_ajax_html(url('accounts:transfer-money-dialog', self.account_2.id)), texts=['pgf-error-receiver_is_fast'])

    def test_no_ban_sender_required(self):
        self.account_1.ban_game(1)
        self.account_1.save()
        self.check_html_ok(self.request_ajax_html(url('accounts:transfer-money-dialog', self.account_2.id)), texts=['pgf-error-common.ban_any'])

    def test_no_ban_receiver_required(self):
        self.account_2.ban_game(1)
        self.account_2.save()
        self.check_html_ok(self.request_ajax_html(url('accounts:transfer-money-dialog', self.account_2.id)), texts=['pgf-error-receiver_banned'])

    def test_same_accounts(self):
        self.check_html_ok(self.request_ajax_html(url('accounts:transfer-money-dialog', self.account_1.id)), texts=['pgf-error-own_account'])

    def test_show(self):
        self.check_html_ok(self.request_ajax_html(url('accounts:transfer-money-dialog', self.account_2.id)))

    def test_404(self):
        self.check_html_ok(self.request_ajax_html(url('accounts:transfer-money-dialog', 666)), texts=['pgf-error-account.wrong_value'])


class TransferMoneyTests(AccountRequestsTests):

    def setUp(self):
        super(TransferMoneyTests, self).setUp()

        bank_account = bank_prototypes.AccountPrototype.create(entity_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                                                               entity_id=self.account_1.id,
                                                               currency=bank_relations.CURRENCY_TYPE.PREMIUM)
        bank_account.amount = 1000
        bank_account.save()

        self.request_login(self.account_1.email)

    def post_data(self, money=600):
        return {'money': money,
                'comment': 'some comment'}

    def test_login_required(self):
        self.request_logout()
        with self.check_not_changed(PostponedTaskPrototype._db_count):
            self.check_ajax_error(self.post_ajax_json(url('accounts:transfer-money', self.account_2.id), self.post_data()), 'common.login_required')

    def test_full_sender_required(self):
        self.account_1.is_fast = True
        self.account_1.save()
        with self.check_not_changed(PostponedTaskPrototype._db_count):
            self.check_ajax_error(self.post_ajax_json(url('accounts:transfer-money', self.account_2.id), self.post_data()), 'common.fast_account')

    def test_full_receiver_required(self):
        self.account_2.is_fast = True
        self.account_2.save()
        with self.check_not_changed(PostponedTaskPrototype._db_count):
            self.check_ajax_error(self.post_ajax_json(url('accounts:transfer-money', self.account_2.id), self.post_data()), 'receiver_is_fast')

    def test_no_ban_sender_required(self):
        self.account_1.ban_game(1)
        self.account_1.save()
        with self.check_not_changed(PostponedTaskPrototype._db_count):
            self.check_ajax_error(self.post_ajax_json(url('accounts:transfer-money', self.account_2.id), self.post_data()), 'common.ban_any')

    def test_no_ban_receiver_required(self):
        self.account_2.ban_game(1)
        self.account_2.save()
        with self.check_not_changed(PostponedTaskPrototype._db_count):
            self.check_ajax_error(self.post_ajax_json(url('accounts:transfer-money', self.account_2.id), self.post_data()), 'receiver_banned')

    def test_same_accounts(self):
        with self.check_not_changed(PostponedTaskPrototype._db_count):
            self.check_ajax_error(self.post_ajax_json(url('accounts:transfer-money', self.account_1.id), self.post_data()), 'own_account')

    def test_success(self):
        with self.check_delta(PostponedTaskPrototype._db_count, 1):
            response = self.post_ajax_json(url('accounts:transfer-money', self.account_2.id), self.post_data())
        task = PostponedTaskPrototype._db_latest()
        self.check_ajax_processing(response, task.status_url)

    def test_404(self):
        self.check_ajax_error(self.post_ajax_json(url('accounts:transfer-money', 666), self.post_data()), 'account.wrong_value')

    def test_no_money(self):
        with self.check_not_changed(PostponedTaskPrototype._db_count):
            self.check_ajax_error(self.post_ajax_json(url('accounts:transfer-money', self.account_2.id), self.post_data(money=1001)), 'not_enough_money')

    def test_low_sum(self):
        with self.check_not_changed(PostponedTaskPrototype._db_count):
            self.check_ajax_error(self.post_ajax_json(url('accounts:transfer-money', self.account_2.id), self.post_data(money=1)), 'form_errors')
