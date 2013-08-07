# coding: utf-8

from django.db import IntegrityError

from common.utils import testcase

from game.logic import create_test_map

from accounts.logic import register_user
from accounts.prototypes import AccountPrototype

from accounts.clans.prototypes import ClanPrototype, MembershipPrototype, MembershipRequestPrototype
from accounts.clans.relations import MEMBERSHIP_REQUEST_TYPE
from accounts.clans import exceptions
from accounts.clans.tests.helpers import ClansTestsMixin



class ClanPrototypeTests(testcase.TestCase):

    def setUp(self):
        super(ClanPrototypeTests, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account = AccountPrototype.get_by_id(account_id)
        self.clan = ClanPrototype.create(self.account, abbr=u'abbr', name=u'clan-name', motto='clan-motto', description=u'clan-description')

    def test_create(self):
        self.assertEqual(self.clan.name, u'clan-name')
        self.assertEqual(self.clan.abbr, u'abbr')
        self.assertEqual(self.clan.motto, u'clan-motto')
        self.assertEqual(self.clan.description, u'clan-description')
        self.assertEqual(self.clan.members_number, 1)

        membership = MembershipPrototype.get_by_account_id(self.account.id)

        self.assertEqual(membership.clan_id, self.clan.id)
        self.assertEqual(membership.account_id, self.account.id)
        self.assertTrue(membership.role._is_LEADER)

    def test_remove(self):
        self.clan.remove()
        self.assertEqual(ClanPrototype._db_count(), 0)
        self.assertEqual(MembershipPrototype._db_count(), 0
                         )

class ClanPrototypeTransactionTests(testcase.TransactionTestCase, ClansTestsMixin):

    def setUp(self):
        super(ClanPrototypeTransactionTests, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account = AccountPrototype.get_by_id(account_id)
        self.clan = ClanPrototype.create(self.account, abbr=u'abbr', name=u'clan-name', motto='clan-motto', description=u'clan-description')

    def test_unique_name(self):
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        self.assertRaises(IntegrityError,
                          ClanPrototype.create,
                          AccountPrototype.get_by_id(account_id),
                          abbr=u'abr2',
                          name=self.clan.name,
                          motto='bla-motto',
                          description=u'bla-description')

        self.assertEqual(ClanPrototype._db_count(), 1)
        self.assertEqual(MembershipPrototype._db_count(), 1)

    def test_unique_abbr(self):
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        self.assertRaises(IntegrityError,
                          ClanPrototype.create,
                          AccountPrototype.get_by_id(account_id),
                          abbr=self.clan.abbr,
                          name='bla-name',
                          motto='bla-motto',
                          description=u'bla-description')
        self.assertEqual(ClanPrototype._db_count(), 1)
        self.assertEqual(MembershipPrototype._db_count(), 1)


    def test_unique_owner(self):
        self.assertRaises(IntegrityError,
                          ClanPrototype.create,
                          self.account,
                          abbr='abr2',
                          name='bla-name',
                          motto='bla-motto',
                          description=u'bla-description')
        self.assertEqual(ClanPrototype._db_count(), 1)
        self.assertEqual(MembershipPrototype._db_count(), 1)


    def test_add_member_member__already_member(self):
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        account_2 = AccountPrototype.get_by_id(account_id)
        self.create_clan(account_2, 0)

        self.assertRaises(exceptions.AddMemberFromClanError, self.clan.add_member, account_2)
        self.assertEqual(self.clan.members_number, 1)
        self.assertEqual(MembershipPrototype._db_count(), 2)


    def test_add_member_member__success(self):
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        account_2 = AccountPrototype.get_by_id(account_id)
        self.clan.add_member(account_2)
        self.assertEqual(self.clan.members_number, 1)
        self.assertEqual(MembershipPrototype._db_count(), 2)

    def test_remove_member_member__not_member(self):
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        account_2 = AccountPrototype.get_by_id(account_id)

        self.assertRaises(exceptions.RemoveNotMemberFromClanError, self.clan.remove_member, account_2)
        self.assertEqual(self.clan.members_number, 1)
        self.assertEqual(MembershipPrototype._db_count(), 1)

    def test_remove_member_member__wrong_clan(self):
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        account_2 = AccountPrototype.get_by_id(account_id)
        self.create_clan(account_2, 0)

        self.assertRaises(exceptions.RemoveMemberFromWrongClanError, self.clan.remove_member, account_2)
        self.assertEqual(self.clan.members_number, 1)
        self.assertEqual(MembershipPrototype._db_count(), 2)

    def test_remove_member_member__leader(self):
        self.assertRaises(exceptions.RemoveLeaderFromClanError, self.clan.remove_member, self.account)
        self.assertEqual(self.clan.members_number, 1)
        self.assertEqual(MembershipPrototype._db_count(), 1)

    def test_remove_member_member__success(self):
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        account_2 = AccountPrototype.get_by_id(account_id)

        self.clan.add_member(account_2)
        self.clan.remove_member(account_2)

        self.assertEqual(self.clan.members_number, 1)
        self.assertEqual(MembershipPrototype._db_count(), 1)


class MembershipRequestPrototypeTests(testcase.TestCase, ClansTestsMixin):

    def setUp(self):
        super(MembershipRequestPrototypeTests, self).setUp()
        create_test_map()
        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)

    def test_get_for_clan(self):
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        account_2 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_3', 'test_user_3@test.com', '111111')
        account_3 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_4', 'test_user_4@test.com', '111111')
        account_4 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_5', 'test_user_5@test.com', '111111')
        account_5 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_6', 'test_user_6@test.com', '111111')
        account_6 = AccountPrototype.get_by_id(account_id)

        clan_1 = self.create_clan(self.account, 0)
        clan_2 = self.create_clan(account_4, 1)

        MembershipRequestPrototype.create(account=account_2,
                                          clan=clan_1,
                                          text=u'invite-1',
                                          type=MEMBERSHIP_REQUEST_TYPE.FROM_CLAN)

        request = MembershipRequestPrototype.create(account=account_3,
                                                    clan=clan_1,
                                                    text=u'invite-2',
                                                    type=MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT)

        MembershipRequestPrototype.create(account=account_5,
                                          clan=clan_2,
                                          text=u'invite-3',
                                          type=MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT)

        MembershipRequestPrototype.create(account=account_6,
                                          clan=clan_2,
                                          text=u'invite-4',
                                          type=MEMBERSHIP_REQUEST_TYPE.FROM_CLAN)

        self.assertEqual(set(request.id for request in MembershipRequestPrototype.get_for_clan(clan_1.id)),
                         set([request.id]))


    def test_get_for_account(self):
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        account_2 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_3', 'test_user_3@test.com', '111111')
        account_3 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_4', 'test_user_4@test.com', '111111')
        account_4 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_5', 'test_user_5@test.com', '111111')
        account_5 = AccountPrototype.get_by_id(account_id)

        clan_1 = self.create_clan(account_2, 0)
        clan_2 = self.create_clan(account_4, 1)

        request = MembershipRequestPrototype.create(account=self.account,
                                          clan=clan_1,
                                          text=u'invite-1',
                                          type=MEMBERSHIP_REQUEST_TYPE.FROM_CLAN)

        MembershipRequestPrototype.create(account=self.account,
                                          clan=clan_1,
                                          text=u'invite-2',
                                          type=MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT)

        MembershipRequestPrototype.create(account=account_3,
                                          clan=clan_2,
                                          text=u'invite-3',
                                          type=MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT)

        MembershipRequestPrototype.create(account=account_5,
                                          clan=clan_2,
                                          text=u'invite-4',
                                          type=MEMBERSHIP_REQUEST_TYPE.FROM_CLAN)

        self.assertEqual(set(request.id for request in MembershipRequestPrototype.get_for_account(self.account.id)),
                         set([request.id]))
