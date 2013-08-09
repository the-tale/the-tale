# coding: utf-8

import mock

from common.utils.testcase import TestCase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.logic import create_test_map

from accounts.clans.logic import ClanInfo
from accounts.clans.relations import MEMBER_ROLE
from accounts.clans.tests.helpers import ClansTestsMixin


class ClanInfoTests(TestCase, ClansTestsMixin):

    def setUp(self):
        super(ClanInfoTests, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)
        self.clan_info = ClanInfo(account=self.account)


    @mock.patch('accounts.prototypes.AccountPrototype.is_authenticated', lambda *argv: False)
    def test_can_create_clan__anonymous(self):
        self.assertFalse(self.clan_info.can_create_clan)

    def test_can_create_clan__already_member(self):
        self.create_clan(self.account, 0)
        self.assertFalse(self.clan_info.can_create_clan)

    def test_can_create_clan__is_fast(self):
        self.account.is_fast = True
        self.assertFalse(self.clan_info.can_create_clan)

    def test_can_create_clan__can(self):
        self.assertTrue(self.clan_info.can_create_clan)


    @mock.patch('accounts.prototypes.AccountPrototype.is_authenticated', lambda *argv: False)
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
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        clan_2 = self.create_clan(AccountPrototype.get_by_id(account_id), 0)
        self.assertFalse(self.clan_info.is_member_of(clan_2))

    def test_is_member_of__is_member(self):
        self.assertTrue(self.clan_info.is_member_of(self.create_clan(self.account, 0)))

    @mock.patch('accounts.clans.logic.ClanInfo.is_member_of', lambda info, clan: False)
    def test_is_owner_of___is_member_false(self):
        self.assertFalse(self.clan_info.is_owner_of(self.create_clan(self.account, 0)))

    def test_is_owner_of__is_member_true__wrong_clan(self):
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        account_2 = AccountPrototype.get_by_id(account_id)

        self.create_clan(self.account, 0)

        self.assertFalse(self.clan_info.is_owner_of(self.create_clan(account_2, 1)))

    def test_is_owner_of__is_owner(self):
        self.assertTrue(self.clan_info.is_owner_of(self.create_clan(self.account, 0)))

    @mock.patch('accounts.clans.prototypes.MembershipPrototype.role', MEMBER_ROLE.MEMBER)
    def test_is_owner_of__not_leader(self):
        self.assertFalse(self.clan_info.is_owner_of(self.create_clan(self.account, 0)))

    def test_can_invite__not_member(self):
        self.assertFalse(self.clan_info.can_invite)

    @mock.patch('accounts.clans.prototypes.MembershipPrototype.role', MEMBER_ROLE.MEMBER)
    def test_can_invite__no_rights(self):
        self.create_clan(self.account, 0)
        self.assertFalse(self.clan_info.can_invite)

    def test_can_invite__has_rights(self):
        self.create_clan(self.account, 0)
        self.assertTrue(self.clan_info.can_invite)

    def test_can_remove__not_member(self):
        self.assertFalse(self.clan_info.can_remove)

    @mock.patch('accounts.clans.prototypes.MembershipPrototype.role', MEMBER_ROLE.MEMBER)
    def test_can_remove__no_rights(self):
        self.create_clan(self.account, 0)
        self.assertFalse(self.clan_info.can_remove)

    def test_can_remove__has_rights(self):
        self.create_clan(self.account, 0)
        self.assertTrue(self.clan_info.can_remove)
