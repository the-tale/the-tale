# coding: utf-8

from unittest import mock

from the_tale.common.utils.testcase import TestCase

from the_tale.game.logic import create_test_map

from the_tale.finances.shop.relations import PERMANENT_PURCHASE_TYPE

from the_tale.accounts.clans.logic import ClanInfo
from the_tale.accounts.clans.relations import MEMBER_ROLE
from the_tale.accounts.clans.tests.helpers import ClansTestsMixin
from the_tale.accounts.clans.conf import clans_settings

from the_tale.forum.prototypes import CategoryPrototype

class ClanInfoTests(TestCase, ClansTestsMixin):

    def setUp(self):
        super(ClanInfoTests, self).setUp()
        create_test_map()

        CategoryPrototype.create(caption='category-1', slug=clans_settings.FORUM_CATEGORY_SLUG, order=0)

        self.account = self.accounts_factory.create_account()
        self.clan_info = ClanInfo(account=self.account)


    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_authenticated', lambda *argv: False)
    def test_membership__anonymous(self):
        self.assertEqual(self.clan_info.membership, None)

    def test_membership__no_membership(self):
        self.assertEqual(self.clan_info.membership, None)

    def test_membership__has_membership(self):
        self.create_clan(self.account, 0)
        self.assertEqual(self.clan_info.membership.account_id, self.account.id)

    def test_is_member_of__no_clan(self):
        self.assertFalse(self.clan_info.is_member_of(None))

    def test_is_member_of__no_membership(self):
        clan_2 = self.create_clan(self.accounts_factory.create_account(), 0)
        self.assertFalse(self.clan_info.is_member_of(clan_2))

    def test_is_member_of__is_member(self):
        self.assertTrue(self.clan_info.is_member_of(self.create_clan(self.account, 0)))

    @mock.patch('the_tale.accounts.clans.logic.ClanInfo.is_member_of', lambda info, clan: False)
    def test_is_owner_of___is_member_false(self):
        self.assertFalse(self.clan_info.is_owner_of(self.create_clan(self.account, 0)))

    def test_is_owner_of__is_member_true__wrong_clan(self):
        account_2 = self.accounts_factory.create_account()

        self.create_clan(self.account, 0)

        self.assertFalse(self.clan_info.is_owner_of(self.create_clan(account_2, 1)))

    def test_is_owner_of__is_owner(self):
        self.assertTrue(self.clan_info.is_owner_of(self.create_clan(self.account, 0)))

    @mock.patch('the_tale.accounts.clans.prototypes.MembershipPrototype.role', MEMBER_ROLE.MEMBER)
    def test_is_owner_of__not_leader(self):
        self.assertFalse(self.clan_info.is_owner_of(self.create_clan(self.account, 0)))

    def test_can_invite__not_member(self):
        self.assertFalse(self.clan_info.can_invite)

    @mock.patch('the_tale.accounts.clans.prototypes.MembershipPrototype.role', MEMBER_ROLE.MEMBER)
    def test_can_invite__no_rights(self):
        self.create_clan(self.account, 0)
        self.assertFalse(self.clan_info.can_invite)

    def test_can_invite__has_rights(self):
        self.create_clan(self.account, 0)
        self.assertTrue(self.clan_info.can_invite)

    def test_can_remove__not_member(self):
        self.assertFalse(self.clan_info.can_remove)

    @mock.patch('the_tale.accounts.clans.prototypes.MembershipPrototype.role', MEMBER_ROLE.MEMBER)
    def test_can_remove__no_rights(self):
        self.create_clan(self.account, 0)
        self.assertFalse(self.clan_info.can_remove)

    def test_can_remove__has_rights(self):
        self.create_clan(self.account, 0)
        self.assertTrue(self.clan_info.can_remove)
