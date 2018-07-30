
import smart_imports

smart_imports.all()


class ClanPrototypeTests(utils_testcase.TestCase):

    def setUp(self):
        super(ClanPrototypeTests, self).setUp()
        game_logic.create_test_map()

        self.forum_category = forum_prototypes.CategoryPrototype.create(caption='category-1', slug=conf.settings.FORUM_CATEGORY_SLUG, order=0)

        self.account = self.accounts_factory.create_account()
        self.clan = prototypes.ClanPrototype.create(self.account, abbr='abbr', name='clan-name', motto='clan-motto', description='clan-description')

    def test_create(self):
        self.assertEqual(self.clan.name, 'clan-name')
        self.assertEqual(self.clan.abbr, 'abbr')
        self.assertEqual(self.clan.motto, 'clan-motto')
        self.assertEqual(self.clan.description, 'clan-description')
        self.assertEqual(self.clan.members_number, 1)

        membership = prototypes.MembershipPrototype.get_by_account_id(self.account.id)

        self.assertEqual(membership.clan_id, self.clan.id)
        self.assertEqual(membership.account_id, self.account.id)
        self.assertTrue(membership.role.is_LEADER)

        self.account.reload()
        self.assertEqual(self.account.clan_id, self.clan.id)

        self.assertEqual(forum_prototypes.SubCategoryPrototype._db_count(), 1)
        self.assertTrue(forum_prototypes.SubCategoryPrototype.get_by_id(self.clan.forum_subcategory_id).restricted)
        self.assertEqual(forum_prototypes.PermissionPrototype._db_count(), 1)
        self.assertNotEqual(forum_prototypes.PermissionPrototype.get_for(self.account.id, self.clan.forum_subcategory_id), None)

    def test_remove(self):
        self.clan.remove()
        self.assertEqual(prototypes.ClanPrototype._db_count(), 0)
        self.assertEqual(prototypes.MembershipPrototype._db_count(), 0)
        self.assertEqual(forum_prototypes.SubCategoryPrototype._db_count(), 0)
        self.assertEqual(forum_prototypes.PermissionPrototype._db_count(), 0)
        self.assertEqual(forum_prototypes.PermissionPrototype.get_for(self.account.id, self.clan.forum_subcategory_id), None)

    def test_create_remove_multiple_clans(self):
        account_2 = self.accounts_factory.create_account()
        clan_2 = prototypes.ClanPrototype.create(account_2, abbr='abbr2', name='clan-name-2', motto='clan-2-motto', description='clan-2-description')

        self.assertEqual(forum_prototypes.SubCategoryPrototype._db_count(), 2)
        self.assertEqual(forum_prototypes.PermissionPrototype._db_count(), 2)
        self.assertNotEqual(forum_prototypes.PermissionPrototype.get_for(self.account.id, self.clan.forum_subcategory_id), None)
        self.assertNotEqual(forum_prototypes.PermissionPrototype.get_for(account_2.id, clan_2.forum_subcategory_id), None)

        clan_2.remove()

        self.assertEqual(forum_prototypes.SubCategoryPrototype._db_count(), 1)
        self.assertEqual(forum_prototypes.PermissionPrototype._db_count(), 1)

        self.assertNotEqual(forum_prototypes.PermissionPrototype.get_for(self.account.id, self.clan.forum_subcategory_id), None)
        self.assertEqual(forum_prototypes.PermissionPrototype.get_for(account_2.id, clan_2.forum_subcategory_id), None)


class ClanPrototypeTransactionTests(utils_testcase.TransactionTestCase, helpers.ClansTestsMixin):

    def setUp(self):
        super(ClanPrototypeTransactionTests, self).setUp()
        game_logic.create_test_map()

        self.forum_category = forum_prototypes.CategoryPrototype.create(caption='category-1', slug=conf.settings.FORUM_CATEGORY_SLUG, order=0)

        self.account = self.accounts_factory.create_account()
        self.clan = prototypes.ClanPrototype.create(self.account, abbr='abbr', name='clan-name', motto='clan-motto', description='clan-description')

    def test_unique_name(self):
        self.assertRaises(django_db.IntegrityError,
                          prototypes.ClanPrototype.create,
                          self.accounts_factory.create_account(),
                          abbr='abr2',
                          name=self.clan.name,
                          motto='bla-motto',
                          description='bla-description')

        self.assertEqual(prototypes.ClanPrototype._db_count(), 1)
        self.assertEqual(prototypes.MembershipPrototype._db_count(), 1)
        self.assertEqual(forum_prototypes.PermissionPrototype._db_count(), 1)

    def test_unique_abbr(self):
        self.assertRaises(django_db.IntegrityError,
                          prototypes.ClanPrototype.create,
                          self.accounts_factory.create_account(),
                          abbr=self.clan.abbr,
                          name='bla-name',
                          motto='bla-motto',
                          description='bla-description')
        self.assertEqual(prototypes.ClanPrototype._db_count(), 1)
        self.assertEqual(prototypes.MembershipPrototype._db_count(), 1)
        self.assertEqual(forum_prototypes.PermissionPrototype._db_count(), 1)

    def test_unique_owner(self):
        self.assertRaises(django_db.IntegrityError,
                          prototypes.ClanPrototype.create,
                          self.account,
                          abbr='abr2',
                          name='bla-name',
                          motto='bla-motto',
                          description='bla-description')
        self.assertEqual(prototypes.ClanPrototype._db_count(), 1)
        self.assertEqual(prototypes.MembershipPrototype._db_count(), 1)
        self.assertEqual(forum_prototypes.PermissionPrototype._db_count(), 1)

    def test_add_member__already_member(self):
        account_2 = self.accounts_factory.create_account()
        self.create_clan(account_2, 0)

        self.assertRaises(exceptions.AddMemberFromClanError, self.clan.add_member, account_2)
        self.assertEqual(self.clan.members_number, 1)
        self.assertEqual(prototypes.MembershipPrototype._db_count(), 2)
        self.assertEqual(forum_prototypes.PermissionPrototype.get_for(account_2.id, self.clan.forum_subcategory_id), None)

    def test_add_member__success(self):
        account_2 = self.accounts_factory.create_account()
        self.clan.add_member(account_2)
        self.assertEqual(self.clan.members_number, 2)
        self.assertEqual(prototypes.MembershipPrototype._db_count(), 2)

        account_2.reload()
        self.assertEqual(account_2.clan_id, self.clan.id)
        self.assertNotEqual(forum_prototypes.PermissionPrototype.get_for(account_2.id, self.clan.forum_subcategory_id), None)

    def test_add_member__remove_membership_requests_when_created(self):
        account_2 = self.accounts_factory.create_account()
        account_3 = self.accounts_factory.create_account()
        account_4 = self.accounts_factory.create_account()
        account_5 = self.accounts_factory.create_account()

        clan_2 = self.create_clan(account_2, 2)
        clan_3 = self.create_clan(account_3, 3)

        prototypes.MembershipRequestPrototype.create(initiator=account_4,
                                                     account=account_4,
                                                     clan=clan_2,
                                                     text='request',
                                                     type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT)

        prototypes.MembershipRequestPrototype.create(initiator=account_3,
                                                     account=account_4,
                                                     clan=clan_3,
                                                     text='request',
                                                     type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_CLAN)

        request_1 = prototypes.MembershipRequestPrototype.create(initiator=account_5,
                                                                 account=account_5,
                                                                 clan=clan_2,
                                                                 text='request',
                                                                 type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT)

        request_2 = prototypes.MembershipRequestPrototype.create(initiator=account_3,
                                                                 account=account_5,
                                                                 clan=clan_3,
                                                                 text='request',
                                                                 type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_CLAN)

        self.assertEqual(prototypes.MembershipRequestPrototype._db_count(), 4)

        self.clan.add_member(account_4)

        self.assertEqual(prototypes.MembershipRequestPrototype._db_count(), 2)
        self.assertEqual(set(r.id for r in prototypes.MembershipRequestPrototype._db_all()),
                         set((request_1.id, request_2.id)))

    def test_remove_member_member__not_member(self):
        account_2 = self.accounts_factory.create_account()

        self.assertRaises(exceptions.RemoveNotMemberFromClanError, self.clan.remove_member, account_2)
        self.assertEqual(self.clan.members_number, 1)
        self.assertEqual(prototypes.MembershipPrototype._db_count(), 1)
        self.assertEqual(forum_prototypes.PermissionPrototype._db_count(), 1)

    def test_remove_member_member__wrong_clan(self):
        account_2 = self.accounts_factory.create_account()
        self.create_clan(account_2, 0)

        self.assertRaises(exceptions.RemoveMemberFromWrongClanError, self.clan.remove_member, account_2)
        self.assertEqual(self.clan.members_number, 1)
        self.assertEqual(prototypes.MembershipPrototype._db_count(), 2)
        self.assertEqual(forum_prototypes.PermissionPrototype._db_count(), 2)

    def test_remove_member_member__leader(self):
        self.assertRaises(exceptions.RemoveLeaderFromClanError, self.clan.remove_member, self.account)
        self.assertEqual(self.clan.members_number, 1)
        self.assertEqual(prototypes.MembershipPrototype._db_count(), 1)
        self.assertEqual(forum_prototypes.PermissionPrototype._db_count(), 1)

    def test_remove_member_member__success(self):
        account_2 = self.accounts_factory.create_account()

        self.clan.add_member(account_2)
        account_2.reload()
        self.assertEqual(account_2.clan_id, self.clan.id)

        self.clan.remove_member(account_2)
        account_2.reload()
        self.assertEqual(account_2.clan_id, None)

        self.assertEqual(self.clan.members_number, 1)
        self.assertEqual(prototypes.MembershipPrototype._db_count(), 1)

        self.assertEqual(forum_prototypes.PermissionPrototype.get_for(account_2.id, self.clan.forum_subcategory_id), None)

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

        self.assertTrue('updated_name' in forum_prototypes.SubCategoryPrototype.get_by_id(self.clan.forum_subcategory_id).caption)


class MembershipPrototypeTests(utils_testcase.TestCase, helpers.ClansTestsMixin):

    def setUp(self):
        super(MembershipPrototypeTests, self).setUp()

        self.forum_category = forum_prototypes.CategoryPrototype.create(caption='category-1', slug=conf.settings.FORUM_CATEGORY_SLUG, order=0)

        game_logic.create_test_map()
        self.account = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        self.clan = self.create_clan(self.account, 0)

    def test_create(self):
        prototypes.MembershipPrototype.create(account=self.account_2, clan=self.clan, role=relations.MEMBER_ROLE.MEMBER)
        self.assertEqual(forum_prototypes.PermissionPrototype._db_count(), 2)
        permission = forum_prototypes.PermissionPrototype._db_get_object(1)
        self.assertEqual(permission.account_id, self.account_2.id)
        self.assertEqual(permission.subcategory_id, self.clan.forum_subcategory_id)

    def test_remove(self):
        prototypes.MembershipPrototype.create(account=self.account_2, clan=self.clan, role=relations.MEMBER_ROLE.MEMBER).remove()
        self.assertEqual(forum_prototypes.PermissionPrototype._db_count(), 1)
        permission = forum_prototypes.PermissionPrototype._db_get_object(0)
        self.assertEqual(permission.account_id, self.account.id)
        self.assertEqual(permission.subcategory_id, self.clan.forum_subcategory_id)


class MembershipRequestPrototypeTests(utils_testcase.TestCase, helpers.ClansTestsMixin):

    def setUp(self):
        super(MembershipRequestPrototypeTests, self).setUp()

        self.forum_category = forum_prototypes.CategoryPrototype.create(caption='category-1', slug=conf.settings.FORUM_CATEGORY_SLUG, order=0)

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

    def test_invite_message(self):
        account_2 = self.accounts_factory.create_account()

        clan_1 = self.create_clan(self.account, 0)

        prototypes.MembershipRequestPrototype.create(initiator=self.account,
                                                     account=account_2,
                                                     clan=clan_1,
                                                     text='invite-1',
                                                     type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_CLAN)

    def test_request_message(self):
        account_2 = self.accounts_factory.create_account()

        clan_1 = self.create_clan(self.account, 0)

        prototypes.MembershipRequestPrototype.create(initiator=account_2,
                                                     account=account_2,
                                                     clan=clan_1,
                                                     text='request-1',
                                                     type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT)

    def test_get_for_clan(self):
        account_2 = self.accounts_factory.create_account()
        account_3 = self.accounts_factory.create_account()
        account_4 = self.accounts_factory.create_account()
        account_5 = self.accounts_factory.create_account()
        account_6 = self.accounts_factory.create_account()

        clan_1 = self.create_clan(self.account, 0)
        clan_2 = self.create_clan(account_4, 1)

        prototypes.MembershipRequestPrototype.create(initiator=self.account,
                                                     account=account_2,
                                                     clan=clan_1,
                                                     text='invite-1',
                                                     type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_CLAN)

        request = prototypes.MembershipRequestPrototype.create(initiator=account_3,
                                                               account=account_3,
                                                               clan=clan_1,
                                                               text='invite-2',
                                                               type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT)

        prototypes.MembershipRequestPrototype.create(initiator=account_5,
                                                     account=account_5,
                                                     clan=clan_2,
                                                     text='invite-3',
                                                     type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT)

        prototypes.MembershipRequestPrototype.create(initiator=account_4,
                                                     account=account_6,
                                                     clan=clan_2,
                                                     text='invite-4',
                                                     type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_CLAN)

        self.assertEqual(set(request.id for request in prototypes.MembershipRequestPrototype.get_for_clan(clan_1.id)),
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

        request = prototypes.MembershipRequestPrototype.create(initiator=self.account,
                                                               account=self.account,
                                                               clan=clan_1,
                                                               text='invite-1',
                                                               type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_CLAN)

        prototypes.MembershipRequestPrototype.create(initiator=self.account,
                                                     account=self.account,
                                                     clan=clan_3,
                                                     text='invite-2',
                                                     type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT)

        prototypes.MembershipRequestPrototype.create(initiator=account_3,
                                                     account=account_3,
                                                     clan=clan_2,
                                                     text='invite-3',
                                                     type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT)

        prototypes.MembershipRequestPrototype.create(initiator=account_4,
                                                     account=account_5,
                                                     clan=clan_2,
                                                     text='invite-4',
                                                     type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_CLAN)

        self.assertEqual(set(request.id for request in prototypes.MembershipRequestPrototype.get_for_account(self.account.id)),
                         set([request.id]))
