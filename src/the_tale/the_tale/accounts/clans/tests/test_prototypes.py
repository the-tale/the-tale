# coding: utf-8

from django.db import IntegrityError

from the_tale.common.utils import testcase

from the_tale.game.logic import create_test_map

from the_tale.accounts.clans.prototypes import ClanPrototype, MembershipPrototype, MembershipRequestPrototype
from the_tale.accounts.clans.relations import MEMBERSHIP_REQUEST_TYPE, MEMBER_ROLE
from the_tale.accounts.clans import exceptions
from the_tale.accounts.clans.tests.helpers import ClansTestsMixin
from the_tale.accounts.clans.conf import clans_settings

from the_tale.forum.prototypes import CategoryPrototype, SubCategoryPrototype, PermissionPrototype as ForumPermissionPrototype


class ClanPrototypeTests(testcase.TestCase):

    def setUp(self):
        super(ClanPrototypeTests, self).setUp()
        create_test_map()

        self.forum_category = CategoryPrototype.create(caption='category-1', slug=clans_settings.FORUM_CATEGORY_SLUG, order=0)

        self.account = self.accounts_factory.create_account()
        self.clan = ClanPrototype.create(self.account, abbr='abbr', name='clan-name', motto='clan-motto', description='clan-description')

    def test_create(self):
        self.assertEqual(self.clan.name, 'clan-name')
        self.assertEqual(self.clan.abbr, 'abbr')
        self.assertEqual(self.clan.motto, 'clan-motto')
        self.assertEqual(self.clan.description, 'clan-description')
        self.assertEqual(self.clan.members_number, 1)

        membership = MembershipPrototype.get_by_account_id(self.account.id)

        self.assertEqual(membership.clan_id, self.clan.id)
        self.assertEqual(membership.account_id, self.account.id)
        self.assertTrue(membership.role.is_LEADER)

        self.account.reload()
        self.assertEqual(self.account.clan_id, self.clan.id)

        self.assertEqual(SubCategoryPrototype._db_count(), 1)
        self.assertTrue(SubCategoryPrototype.get_by_id(self.clan.forum_subcategory_id).restricted)
        self.assertEqual(ForumPermissionPrototype._db_count(), 1)
        self.assertNotEqual(ForumPermissionPrototype.get_for(self.account.id, self.clan.forum_subcategory_id), None)

    def test_remove(self):
        self.clan.remove()
        self.assertEqual(ClanPrototype._db_count(), 0)
        self.assertEqual(MembershipPrototype._db_count(), 0)
        self.assertEqual(SubCategoryPrototype._db_count(), 0)
        self.assertEqual(ForumPermissionPrototype._db_count(), 0)
        self.assertEqual(ForumPermissionPrototype.get_for(self.account.id, self.clan.forum_subcategory_id), None)

    def test_create_remove_multiple_clans(self):
        account_2 = self.accounts_factory.create_account()
        clan_2 = ClanPrototype.create(account_2, abbr='abbr2', name='clan-name-2', motto='clan-2-motto', description='clan-2-description')

        self.assertEqual(SubCategoryPrototype._db_count(), 2)
        self.assertEqual(ForumPermissionPrototype._db_count(), 2)
        self.assertNotEqual(ForumPermissionPrototype.get_for(self.account.id, self.clan.forum_subcategory_id), None)
        self.assertNotEqual(ForumPermissionPrototype.get_for(account_2.id, clan_2.forum_subcategory_id), None)

        clan_2.remove()

        self.assertEqual(SubCategoryPrototype._db_count(), 1)
        self.assertEqual(ForumPermissionPrototype._db_count(), 1)

        self.assertNotEqual(ForumPermissionPrototype.get_for(self.account.id, self.clan.forum_subcategory_id), None)
        self.assertEqual(ForumPermissionPrototype.get_for(account_2.id, clan_2.forum_subcategory_id), None)


class ClanPrototypeTransactionTests(testcase.TransactionTestCase, ClansTestsMixin):

    def setUp(self):
        super(ClanPrototypeTransactionTests, self).setUp()
        create_test_map()

        self.forum_category = CategoryPrototype.create(caption='category-1', slug=clans_settings.FORUM_CATEGORY_SLUG, order=0)

        self.account = self.accounts_factory.create_account()
        self.clan = ClanPrototype.create(self.account, abbr='abbr', name='clan-name', motto='clan-motto', description='clan-description')

    def test_unique_name(self):
        self.assertRaises(IntegrityError,
                          ClanPrototype.create,
                          self.accounts_factory.create_account(),
                          abbr='abr2',
                          name=self.clan.name,
                          motto='bla-motto',
                          description='bla-description')

        self.assertEqual(ClanPrototype._db_count(), 1)
        self.assertEqual(MembershipPrototype._db_count(), 1)
        self.assertEqual(ForumPermissionPrototype._db_count(), 1)

    def test_unique_abbr(self):
        self.assertRaises(IntegrityError,
                          ClanPrototype.create,
                          self.accounts_factory.create_account(),
                          abbr=self.clan.abbr,
                          name='bla-name',
                          motto='bla-motto',
                          description='bla-description')
        self.assertEqual(ClanPrototype._db_count(), 1)
        self.assertEqual(MembershipPrototype._db_count(), 1)
        self.assertEqual(ForumPermissionPrototype._db_count(), 1)

    def test_unique_owner(self):
        self.assertRaises(IntegrityError,
                          ClanPrototype.create,
                          self.account,
                          abbr='abr2',
                          name='bla-name',
                          motto='bla-motto',
                          description='bla-description')
        self.assertEqual(ClanPrototype._db_count(), 1)
        self.assertEqual(MembershipPrototype._db_count(), 1)
        self.assertEqual(ForumPermissionPrototype._db_count(), 1)

    def test_add_member__already_member(self):
        account_2 = self.accounts_factory.create_account()
        self.create_clan(account_2, 0)

        self.assertRaises(exceptions.AddMemberFromClanError, self.clan.add_member, account_2)
        self.assertEqual(self.clan.members_number, 1)
        self.assertEqual(MembershipPrototype._db_count(), 2)
        self.assertEqual(ForumPermissionPrototype.get_for(account_2.id, self.clan.forum_subcategory_id), None)

    def test_add_member__success(self):
        account_2 = self.accounts_factory.create_account()
        self.clan.add_member(account_2)
        self.assertEqual(self.clan.members_number, 2)
        self.assertEqual(MembershipPrototype._db_count(), 2)

        account_2.reload()
        self.assertEqual(account_2.clan_id, self.clan.id)
        self.assertNotEqual(ForumPermissionPrototype.get_for(account_2.id, self.clan.forum_subcategory_id), None)

    def test_add_member__remove_membership_requests_when_created(self):
        account_2 = self.accounts_factory.create_account()
        account_3 = self.accounts_factory.create_account()
        account_4 = self.accounts_factory.create_account()
        account_5 = self.accounts_factory.create_account()

        clan_2 = self.create_clan(account_2, 2)
        clan_3 = self.create_clan(account_3, 3)

        MembershipRequestPrototype.create(initiator=account_4,
                                          account=account_4,
                                          clan=clan_2,
                                          text='request',
                                          type=MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT)

        MembershipRequestPrototype.create(initiator=account_3,
                                          account=account_4,
                                          clan=clan_3,
                                          text='request',
                                          type=MEMBERSHIP_REQUEST_TYPE.FROM_CLAN)

        request_1 = MembershipRequestPrototype.create(initiator=account_5,
                                                      account=account_5,
                                                      clan=clan_2,
                                                      text='request',
                                                      type=MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT)

        request_2 = MembershipRequestPrototype.create(initiator=account_3,
                                                      account=account_5,
                                                      clan=clan_3,
                                                      text='request',
                                                      type=MEMBERSHIP_REQUEST_TYPE.FROM_CLAN)

        self.assertEqual(MembershipRequestPrototype._db_count(), 4)

        self.clan.add_member(account_4)

        self.assertEqual(MembershipRequestPrototype._db_count(), 2)
        self.assertEqual(set(r.id for r in MembershipRequestPrototype._db_all()),
                         set((request_1.id, request_2.id)))


    def test_remove_member_member__not_member(self):
        account_2 = self.accounts_factory.create_account()

        self.assertRaises(exceptions.RemoveNotMemberFromClanError, self.clan.remove_member, account_2)
        self.assertEqual(self.clan.members_number, 1)
        self.assertEqual(MembershipPrototype._db_count(), 1)
        self.assertEqual(ForumPermissionPrototype._db_count(), 1)

    def test_remove_member_member__wrong_clan(self):
        account_2 = self.accounts_factory.create_account()
        self.create_clan(account_2, 0)

        self.assertRaises(exceptions.RemoveMemberFromWrongClanError, self.clan.remove_member, account_2)
        self.assertEqual(self.clan.members_number, 1)
        self.assertEqual(MembershipPrototype._db_count(), 2)
        self.assertEqual(ForumPermissionPrototype._db_count(), 2)

    def test_remove_member_member__leader(self):
        self.assertRaises(exceptions.RemoveLeaderFromClanError, self.clan.remove_member, self.account)
        self.assertEqual(self.clan.members_number, 1)
        self.assertEqual(MembershipPrototype._db_count(), 1)
        self.assertEqual(ForumPermissionPrototype._db_count(), 1)

    def test_remove_member_member__success(self):
        account_2 = self.accounts_factory.create_account()

        self.clan.add_member(account_2)
        account_2.reload()
        self.assertEqual(account_2.clan_id, self.clan.id)

        self.clan.remove_member(account_2)
        account_2.reload()
        self.assertEqual(account_2.clan_id, None)

        self.assertEqual(self.clan.members_number, 1)
        self.assertEqual(MembershipPrototype._db_count(), 1)

        self.assertEqual(ForumPermissionPrototype.get_for(account_2.id, self.clan.forum_subcategory_id), None)

    def test_update(self):
        self.clan.update(abbr='abbr2',
                         name='updated_name',
                         motto='updated_motto',
                         description='updated_description')

        self.clan.reload()

        self.assertEqual(self.clan.abbr, 'abbr2')
        self.assertEqual(self.clan.name, 'updated_name')
        self.assertEqual(self.clan.motto, 'updated_motto')
        self.assertEqual(self.clan.description, 'updated_description')

        self.assertTrue('updated_name' in SubCategoryPrototype.get_by_id(self.clan.forum_subcategory_id).caption)


class MembershipPrototypeTests(testcase.TestCase, ClansTestsMixin):

    def setUp(self):
        super(MembershipPrototypeTests, self).setUp()

        self.forum_category = CategoryPrototype.create(caption='category-1', slug=clans_settings.FORUM_CATEGORY_SLUG, order=0)

        create_test_map()
        self.account = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        self.clan = self.create_clan(self.account, 0)

    def test_create(self):
        MembershipPrototype.create(account=self.account_2, clan=self.clan, role=MEMBER_ROLE.MEMBER)
        self.assertEqual(ForumPermissionPrototype._db_count(), 2)
        permission = ForumPermissionPrototype._db_get_object(1)
        self.assertEqual(permission.account_id, self.account_2.id)
        self.assertEqual(permission.subcategory_id, self.clan.forum_subcategory_id)

    def test_remove(self):
        MembershipPrototype.create(account=self.account_2, clan=self.clan, role=MEMBER_ROLE.MEMBER).remove()
        self.assertEqual(ForumPermissionPrototype._db_count(), 1)
        permission = ForumPermissionPrototype._db_get_object(0)
        self.assertEqual(permission.account_id, self.account.id)
        self.assertEqual(permission.subcategory_id, self.clan.forum_subcategory_id)


class MembershipRequestPrototypeTests(testcase.TestCase, ClansTestsMixin):

    def setUp(self):
        super(MembershipRequestPrototypeTests, self).setUp()

        self.forum_category = CategoryPrototype.create(caption='category-1', slug=clans_settings.FORUM_CATEGORY_SLUG, order=0)

        create_test_map()

        self.account = self.accounts_factory.create_account()

    def test_invite_message(self):
        account_2 = self.accounts_factory.create_account()

        clan_1 = self.create_clan(self.account, 0)

        MembershipRequestPrototype.create(initiator=self.account,
                                          account=account_2,
                                          clan=clan_1,
                                          text='invite-1',
                                          type=MEMBERSHIP_REQUEST_TYPE.FROM_CLAN)


    def test_request_message(self):
        account_2 = self.accounts_factory.create_account()

        clan_1 = self.create_clan(self.account, 0)

        MembershipRequestPrototype.create(initiator=account_2,
                                          account=account_2,
                                          clan=clan_1,
                                          text='request-1',
                                          type=MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT)

    def test_get_for_clan(self):
        account_2 = self.accounts_factory.create_account()
        account_3 = self.accounts_factory.create_account()
        account_4 = self.accounts_factory.create_account()
        account_5 = self.accounts_factory.create_account()
        account_6 = self.accounts_factory.create_account()

        clan_1 = self.create_clan(self.account, 0)
        clan_2 = self.create_clan(account_4, 1)

        MembershipRequestPrototype.create(initiator=self.account,
                                          account=account_2,
                                          clan=clan_1,
                                          text='invite-1',
                                          type=MEMBERSHIP_REQUEST_TYPE.FROM_CLAN)

        request = MembershipRequestPrototype.create(initiator=account_3,
                                                    account=account_3,
                                                    clan=clan_1,
                                                    text='invite-2',
                                                    type=MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT)

        MembershipRequestPrototype.create(initiator=account_5,
                                          account=account_5,
                                          clan=clan_2,
                                          text='invite-3',
                                          type=MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT)

        MembershipRequestPrototype.create(initiator=account_4,
                                          account=account_6,
                                          clan=clan_2,
                                          text='invite-4',
                                          type=MEMBERSHIP_REQUEST_TYPE.FROM_CLAN)

        self.assertEqual(set(request.id for request in MembershipRequestPrototype.get_for_clan(clan_1.id)),
                         set([request.id]))


    def test_get_for_account(self):
        account_2 = self.accounts_factory.create_account()
        account_3 = self.accounts_factory.create_account()
        account_4 = self.accounts_factory.create_account()
        account_5 = self.accounts_factory.create_account()
        account_6 = self.accounts_factory.create_account()

        clan_1 = self.create_clan(account_2, 0)
        clan_2 = self.create_clan(account_4, 1)
        clan_3 = self.create_clan(account_6, 2)

        request = MembershipRequestPrototype.create(initiator=self.account,
                                                    account=self.account,
                                                    clan=clan_1,
                                                    text='invite-1',
                                                    type=MEMBERSHIP_REQUEST_TYPE.FROM_CLAN)

        MembershipRequestPrototype.create(initiator=self.account,
                                          account=self.account,
                                          clan=clan_3,
                                          text='invite-2',
                                          type=MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT)

        MembershipRequestPrototype.create(initiator=account_3,
                                          account=account_3,
                                          clan=clan_2,
                                          text='invite-3',
                                          type=MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT)

        MembershipRequestPrototype.create(initiator=account_4,
                                          account=account_5,
                                          clan=clan_2,
                                          text='invite-4',
                                          type=MEMBERSHIP_REQUEST_TYPE.FROM_CLAN)

        self.assertEqual(set(request.id for request in MembershipRequestPrototype.get_for_account(self.account.id)),
                         set([request.id]))
