
import smart_imports

smart_imports.all()


class BaseClanTests(utils_testcase.TestCase,
                    helpers.ClansTestsMixin,
                    personal_messages_helpers.Mixin):

    def setUp(self):
        super().setUp()

        game_logic.create_test_map()

        tt_services.chronicle.cmd_debug_clear_service()

        self.forum_category = forum_prototypes.CategoryPrototype.create(caption='category-1',
                                                                        slug=conf.settings.FORUM_CATEGORY_SLUG,
                                                                        order=0)

        self.account = self.accounts_factory.create_account()
        self.clan = self.create_clan(owner=self.account, uid=1)


class SyncClanStatisitcsTests(BaseClanTests):

    def setUp(self):
        super().setUp()
        self.account_2 = self.accounts_factory.create_account()
        self.account_3 = self.accounts_factory.create_account()
        self.account_4 = self.accounts_factory.create_account()

        logic._add_member(clan=self.clan,
                          account=self.account_2,
                          role=relations.MEMBER_ROLE.RECRUIT)

        logic._add_member(clan=self.clan,
                          account=self.account_3,
                          role=relations.MEMBER_ROLE.RECRUIT)

        self.past = datetime.datetime.now() - datetime.timedelta(days=1)
        self.future = datetime.datetime.now() + datetime.timedelta(days=1)

    def test_statistics_refreshed_at(self):
        old_data = self.clan.statistics_refreshed_at

        logic.sync_clan_statistics(self.clan)

        self.assertTrue(old_data < self.clan.statistics_refreshed_at)

    def test_members_number(self):
        logic.sync_clan_statistics(self.clan)

        self.assertEqual(self.clan.members_number, 3)

        loaded_clan = logic.load_clan(clan_id=self.clan.id)

        self.assertEqual(loaded_clan.members_number, 3)

    def test_active_members_number(self):
        accounts_models.Account.objects.filter(id=self.account.id).update(active_end_at=self.future)
        accounts_models.Account.objects.filter(id=self.account_2.id).update(active_end_at=self.future)
        accounts_models.Account.objects.filter(id=self.account_3.id).update(active_end_at=self.past)
        accounts_models.Account.objects.filter(id=self.account_4.id).update(active_end_at=self.future)

        logic.sync_clan_statistics(self.clan)

        self.assertEqual(self.clan.active_members_number, 2)

        loaded_clan = logic.load_clan(clan_id=self.clan.id)

        self.assertEqual(loaded_clan.active_members_number, 2)

    def test_premium_members_number(self):
        accounts_models.Account.objects.filter(id=self.account.id).update(premium_end_at=self.future)
        accounts_models.Account.objects.filter(id=self.account_2.id).update(premium_end_at=self.future)
        accounts_models.Account.objects.filter(id=self.account_3.id).update(premium_end_at=self.past)
        accounts_models.Account.objects.filter(id=self.account_4.id).update(premium_end_at=self.future)

        logic.sync_clan_statistics(self.clan)

        self.assertEqual(self.clan.premium_members_number, 2)

        loaded_clan = logic.load_clan(clan_id=self.clan.id)

        self.assertEqual(loaded_clan.premium_members_number, 2)

    def test_might(self):
        accounts_models.Account.objects.filter(id=self.account.id).update(might=0)
        accounts_models.Account.objects.filter(id=self.account_2.id).update(might=1)
        accounts_models.Account.objects.filter(id=self.account_3.id).update(might=10)
        accounts_models.Account.objects.filter(id=self.account_4.id).update(might=100)

        logic.sync_clan_statistics(self.clan)

        self.assertEqual(self.clan.might, 11)

        loaded_clan = logic.load_clan(clan_id=self.clan.id)

        self.assertEqual(loaded_clan.might, 11)


class AddMemberTests(BaseClanTests):

    def test_already_member(self):
        account_2 = self.accounts_factory.create_account()

        clan_2 = self.create_clan(owner=account_2, uid=2)

        with self.assertRaises(exceptions.AddMemberFromClanError):
            logic._add_member(clan=self.clan,
                              account=account_2,
                              role=relations.MEMBER_ROLE.RECRUIT)

        # members number not changed
        self.assertEqual(self.clan.members_number, 1)
        loaded_clan = logic.load_clan(clan_id=self.clan.id)
        self.assertEqual(loaded_clan.members_number, 1)

        # membership not created
        self.assertFalse(models.Membership.objects.filter(clan_id=self.clan.id,
                                                         account_id=account_2.id).exists())

        self.assertTrue(models.Membership.objects.filter(clan_id=clan_2.id,
                                                         account_id=account_2.id,
                                                         role=relations.MEMBER_ROLE.MASTER).exists())

        # account not changed
        loaded_account = accounts_prototypes.AccountPrototype.get_by_id(account_2.id)
        self.assertEqual(loaded_account.clan_id, clan_2.id)

        # forum permissions not changed granted
        self.assertTrue(forum_prototypes.PermissionPrototype._db_filter(account_id=account_2.id,
                                                                        subcategory_id=clan_2.forum_subcategory_id).exists())
        self.assertFalse(forum_prototypes.PermissionPrototype._db_filter(account_id=account_2.id,
                                                                         subcategory_id=self.clan.forum_subcategory_id).exists())

    def test(self):
        account_2 = self.accounts_factory.create_account()

        expected_role = relations.MEMBER_ROLE.random()

        logic._add_member(clan=self.clan,
                          account=account_2,
                          role=expected_role)

        # members number changed
        self.assertEqual(self.clan.members_number, 2)
        loaded_clan = logic.load_clan(clan_id=self.clan.id)
        self.assertEqual(loaded_clan.members_number, 2)

        # membership created
        self.assertTrue(models.Membership.objects.filter(clan_id=self.clan.id,
                                                         account_id=account_2.id,
                                                         role=expected_role).exists())

        # account changed
        loaded_account = accounts_prototypes.AccountPrototype.get_by_id(account_2.id)
        self.assertEqual(loaded_account.clan_id, self.clan.id)

        # forum permissions granted
        self.assertEqual(forum_prototypes.PermissionPrototype._db_filter(account_id=account_2.id).count(), 1)
        self.assertEqual(forum_prototypes.PermissionPrototype._db_filter(account_id=account_2.id,
                                                                         subcategory_id=self.clan.forum_subcategory_id).count(), 1)

    def test_remove_membership_requests(self):
        account_2 = self.accounts_factory.create_account()
        account_3 = self.accounts_factory.create_account()
        account_4 = self.accounts_factory.create_account()

        clan_2 = self.create_clan(owner=account_2, uid=2)

        for invited_account in (account_3, account_4):
            logic.create_request(initiator=invited_account, clan=self.clan, text='x')

            logic.create_invite(initiator=account_2,
                                clan=clan_2,
                                member=invited_account,
                                text='y')

        self.assertEqual(models.MembershipRequest.objects.count(), 4)

        with self.check_new_message(account_2.id, [account_3.id]):  # check if other inviters received rejected message
            logic._add_member(clan=self.clan,
                              account=account_3,
                              role=relations.MEMBER_ROLE.random())

        self.assertEqual(models.MembershipRequest.objects.count(), 2)
        self.assertEqual(models.MembershipRequest.objects.filter(account_id=account_4.id).count(), 2)


class TechnicalRemoveMemberTests(BaseClanTests):

    def setUp(self):
        super().setUp()

        self.account_2 = self.accounts_factory.create_account()
        self.account_3 = self.accounts_factory.create_account()

        logic._add_member(clan=self.clan,
                          account=self.account_2,
                          role=relations.MEMBER_ROLE.RECRUIT)

    def check_not_changed(self):
        self.assertEqual(set(models.Membership.objects.filter(clan_id=self.clan.id).values_list('clan_id', 'account_id', 'role')),
                         {(self.clan.id, self.account.id, relations.MEMBER_ROLE.MASTER),
                          (self.clan.id, self.account_2.id, relations.MEMBER_ROLE.RECRUIT)})

    def test_not_member(self):
        with self.assertRaises(exceptions.RemoveMemberFromWrongClanError):
            logic._remove_member(clan=self.clan, account=self.account_3)

        self.check_not_changed()

    def test_wrong_clan(self):
        clan_2 = self.create_clan(owner=self.account_3, uid=2)

        with self.assertRaises(exceptions.RemoveMemberFromWrongClanError):
            logic._remove_member(clan=self.clan, account=self.account_3)

        self.check_not_changed()

        self.assertEqual(set(models.Membership.objects.filter(clan_id=clan_2.id).values_list('clan_id', 'account_id', 'role')),
                         {(clan_2.id, self.account_3.id, relations.MEMBER_ROLE.MASTER)})

    def test_master(self):
        with self.assertRaises(exceptions.RemoveLeaderFromClanError):
            logic._remove_member(clan=self.clan, account=self.account)

        self.check_not_changed()

    def test_success(self):
        logic._remove_member(clan=self.clan, account=self.account_2)

        self.assertEqual(set(models.Membership.objects.filter(clan_id=self.clan.id).values_list('clan_id', 'account_id', 'role')),
                         {(self.clan.id, self.account.id, relations.MEMBER_ROLE.MASTER)})

        # members number changed
        self.assertEqual(self.clan.members_number, 1)
        loaded_clan = logic.load_clan(clan_id=self.clan.id)
        self.assertEqual(loaded_clan.members_number, 1)

        # membership removed
        self.assertFalse(models.Membership.objects.filter(clan_id=self.clan.id,
                                                         account_id=self.account_2.id).exists())

        # account changed
        loaded_account = accounts_prototypes.AccountPrototype.get_by_id(self.account_2.id)
        self.assertEqual(loaded_account.clan_id, None)

        # forum permissions removed
        self.assertFalse(forum_prototypes.PermissionPrototype._db_filter(account_id=self.account_2.id).exists())

    def test_remove_membership_requests(self):
        account_2 = self.accounts_factory.create_account()
        account_3 = self.accounts_factory.create_account()

        logic._add_member(clan=self.clan,
                          account=account_2,
                          role=relations.MEMBER_ROLE.COMANDOR)

        logic.create_invite(initiator=account_2,
                            clan=self.clan,
                            member=account_3,
                            text='y')

        self.assertEqual(models.MembershipRequest.objects.count(), 1)

        logic._remove_member(clan=self.clan,
                             account=account_2)

        self.assertEqual(models.MembershipRequest.objects.count(), 0)


class CreateClanTests(BaseClanTests):

    def test(self):
        # subcategory created
        subcategory = forum_prototypes.SubCategoryPrototype.get_by_id(self.clan.forum_subcategory_id)

        self.assertTrue(subcategory.restricted)
        self.assertEqual(subcategory.caption, logic.forum_subcategory_caption(self.clan.name))
        self.assertEqual(subcategory.category.slug, conf.settings.FORUM_CATEGORY_SLUG)

        # forum permissions granted
        self.assertEqual(forum_prototypes.PermissionPrototype._db_filter(account_id=self.account.id).count(), 1)
        self.assertEqual(forum_prototypes.PermissionPrototype._db_filter(account_id=self.account.id,
                                                                         subcategory_id=self.clan.forum_subcategory_id).count(), 1)

        # clan created
        self.assertEqual(self.clan.abbr, 'a-1')
        self.assertEqual(self.clan.name, 'name-1')
        self.assertEqual(self.clan.motto, 'motto-1')
        self.assertEqual(self.clan.description, '[b]description-1[/b]')

        loaded_clan = logic.load_clan(clan_id=self.clan.id)

        self.assertEqual(self.clan.abbr, loaded_clan.abbr)
        self.assertEqual(self.clan.name, loaded_clan.name)
        self.assertEqual(self.clan.motto, loaded_clan.motto)
        self.assertEqual(self.clan.description, loaded_clan.description)

        # members number calculated
        self.assertEqual(self.clan.members_number, 1)
        self.assertEqual(loaded_clan.members_number, 1)

        # membership created
        self.assertTrue(models.Membership.objects.filter(clan_id=self.clan.id,
                                                         account_id=self.account.id,
                                                         role=relations.MEMBER_ROLE.MASTER).exists())

        # chronicle logged
        total_events, events = tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(total_events, 1)
        self.assertEqual(set(events[0].tags),
                         {self.clan.meta_object().tag,
                          relations.EVENT.CREATED.meta_object().tag,
                          self.account.meta_object().tag})

    def test_unique_attributes(self):
        account_2 = self.accounts_factory.create_account()

        with self.assertRaises(django_db.IntegrityError):
            logic.create_clan(owner=account_2,
                              abbr='a-1',
                              name='name-2',
                              motto='motto-1',
                              description='[b]description-1[/b]')

        with self.assertRaises(django_db.IntegrityError):
            logic.create_clan(owner=account_2,
                              abbr='a-2',
                              name='name-1',
                              motto='motto-1',
                              description='[b]description-1[/b]')

        logic.create_clan(owner=account_2,
                          abbr='a-2',
                          name='name-2',
                          motto='motto-1',
                          description='[b]description-1[/b]')

    def test_unique_owner(self):
        with self.assertRaises(exceptions.AddMemberFromClanError):
            self.create_clan(self.account, uid=2)


class RemoveClanTests(BaseClanTests):

    def test(self):

        forum_subcategory_id = self.clan.forum_subcategory_id

        account_2 = self.accounts_factory.create_account()
        account_3 = self.accounts_factory.create_account()

        clan_2 = self.create_clan(account_2, uid=2)

        logic._add_member(clan=self.clan, account=account_3, role=relations.MEMBER_ROLE.RECRUIT)

        logic.remove_clan(self.clan)

        self.assertEqual(list(models.Clan.objects.all().values_list('id', flat=True)), [clan_2.id])

        self.assertEqual(models.Membership.objects.all().count(), 1)
        self.assertTrue(models.Membership.objects.filter(clan_id=clan_2.id).exists())

        self.assertEqual(set(accounts_prototypes.AccountPrototype._db_all().values_list('clan_id', flat=True)), {None, clan_2.id})

        self.assertFalse(forum_prototypes.SubCategoryPrototype._db_filter(id=forum_subcategory_id).exists())


class LoadClansTests(BaseClanTests):

    def test(self):
        account_2 = self.accounts_factory.create_account()
        account_3 = self.accounts_factory.create_account()

        self.create_clan(account_2, uid=2)

        clan_3 = self.create_clan(account_3, uid=3)

        clans = logic.load_clans([self.clan.id, clan_3.id])

        self.assertEqual({self.clan.name, clan_3.name},
                         {clan.name for clan in clans})


class SaveClanTests(BaseClanTests):

    def test(self):
        self.clan.abbr = 'a-x'
        self.clan.name = 'name-x'
        self.clan.motto = 'motto-x'
        self.clan.description = 'description-x'

        logic.save_clan(self.clan)

        subcategory = forum_prototypes.SubCategoryPrototype.get_by_id(self.clan.forum_subcategory_id)
        self.assertEqual(subcategory.caption, logic.forum_subcategory_caption('name-x'))

        loaded_clan = logic.load_clan(clan_id=self.clan.id)

        self.assertEqual(loaded_clan.abbr, 'a-x')
        self.assertEqual(loaded_clan.name, 'name-x')
        self.assertEqual(loaded_clan.motto, 'motto-x')
        self.assertEqual(loaded_clan.description, 'description-x')


class GetMemberRoleTests(BaseClanTests):

    def test_no_membership(self):
        account_2 = self.accounts_factory.create_account()
        self.assertEqual(logic.get_member_role(account_2, self.clan), None)

    def test_different_clan(self):
        account_2 = self.accounts_factory.create_account()
        clan_2 = self.create_clan(account_2, uid=2)

        self.assertEqual(logic.get_member_role(self.account, clan_2), None)

    def test_role(self):
        account_2 = self.accounts_factory.create_account()
        self.create_clan(account_2, uid=2)

        self.assertTrue(logic.get_member_role(self.account, self.clan).is_MASTER)


class GetMembershipTests(BaseClanTests):

    def test_no_membership(self):
        account_2 = self.accounts_factory.create_account()
        self.assertEqual(logic.get_membership(account_2.id), None)

    def test_has(self):
        account_2 = self.accounts_factory.create_account()
        self.create_clan(account_2, uid=2)

        membership = logic.get_membership(self.account.id)

        self.assertEqual(membership.clan_id, self.clan.id)
        self.assertEqual(membership.account_id, self.account.id)
        self.assertTrue(membership.role.is_MASTER)


class OperationsRightsTests(BaseClanTests):

    def check_disallowed_all(self, rights):
        for permission in relations.PERMISSION.records:
            if permission.on_member:
                self.assertFalse(rights._check_member_permission(permission=permission,
                                                                 member_clan_id=self.clan.id,
                                                                 member_role=relations.MEMBER_ROLE.RECRUIT))
            else:
                self.assertFalse(rights._check_static_permission(permission=permission))

    def check_allowed_all(self, rights):
        for permission in relations.PERMISSION.records:
            if permission.on_member:
                self.assertTrue(rights._check_member_permission(permission=permission,
                                                                member_clan_id=self.clan.id,
                                                                member_role=relations.MEMBER_ROLE.MASTER))
            else:
                self.assertTrue(rights._check_static_permission(permission=permission))

    def check_allowed_roles(self, rights, allowed_permissions):
        for permission in relations.PERMISSION.records:
            if permission.on_member:
                result = rights._check_member_permission(permission=permission,
                                                         member_clan_id=self.clan.id,
                                                         member_role=relations.MEMBER_ROLE.RECRUIT)
            else:
                result = rights._check_static_permission(permission=permission)

            self.assertEqual(result, permission in allowed_permissions)

    def check_member_permissions(self,
                                 initiator,
                                 clan,
                                 member_clan_id,
                                 member_role,
                                 expected_permissions,
                                 is_moderator=False):
        rights = logic.operations_rights(initiator=initiator,
                                         clan=clan,
                                         is_moderator=is_moderator)

        for permission in relations.PERMISSION.records:
            if not permission.on_member:
                continue

            self.assertEqual(rights._check_member_permission(permission=permission,
                                                             member_clan_id=member_clan_id,
                                                             member_role=member_role),
                             permission in expected_permissions)

    def test_no_initiator(self):
        for is_moderator in (True, False):
            with self.assertRaises(exceptions.CanNotDetermineRightsForUnknownInitiator):
                logic.operations_rights(initiator=None,
                                        clan=self.clan,
                                        is_moderator=is_moderator)

    def test_no_clan(self):
        for is_moderator in (True, False):
            with self.assertRaises(exceptions.CanNotDetermineRightsForUnknownClan):
                logic.operations_rights(initiator=self.account,
                                        clan=None,
                                        is_moderator=is_moderator)

    def test_not_member_and_not_moderator(self):
        account_2 = self.accounts_factory.create_account()

        rights = logic.operations_rights(initiator=account_2,
                                         clan=self.clan,
                                         is_moderator=False)

        self.check_disallowed_all(rights)

    def test_not_member_and_moderator(self):
        account_2 = self.accounts_factory.create_account()

        rights = logic.operations_rights(initiator=account_2,
                                         clan=self.clan,
                                         is_moderator=True)

        self.check_allowed_all(rights)

    def test_only_allowed_permission(self):
        for role in relations.MEMBER_ROLE.records:
            models.Membership.objects.update(role=role)

            rights = logic.operations_rights(initiator=self.account,
                                             clan=self.clan,
                                             is_moderator=False)

            self.check_allowed_roles(rights, allowed_permissions=role.permissions)

    def test_moderator_is_member(self):
        for role in relations.MEMBER_ROLE.records:
            models.Membership.objects.update(role=role)

            rights = logic.operations_rights(initiator=self.account,
                                             clan=self.clan,
                                             is_moderator=True)

            self.check_allowed_all(rights)

    def test_lower_or_equal_priority_member(self):
        for initiator_role in relations.MEMBER_ROLE.records:
            models.Membership.objects.update(role=initiator_role)

            for member_role in relations.MEMBER_ROLE.records:
                if initiator_role.priority < member_role.priority:
                    continue

                self.check_member_permissions(initiator=self.account,
                                              clan=self.clan,
                                              member_clan_id=self.clan.id,
                                              member_role=member_role,
                                              expected_permissions=())

    def test_lower_or_equal_priority_member__moderator(self):
        for initiator_role in relations.MEMBER_ROLE.records:
            models.Membership.objects.update(role=initiator_role)

            for member_role in relations.MEMBER_ROLE.records:
                if initiator_role.priority < member_role.priority:
                    continue

                self.check_member_permissions(initiator=self.account,
                                              clan=self.clan,
                                              member_clan_id=self.clan.id,
                                              member_role=member_role,
                                              expected_permissions=relations.PERMISSION.records,
                                              is_moderator=True)

    def test_upper_priority_member(self):
        for initiator_role in relations.MEMBER_ROLE.records:
            models.Membership.objects.update(role=initiator_role)

            for member_role in relations.MEMBER_ROLE.records:
                if initiator_role.priority >= member_role.priority:
                    continue

                self.check_member_permissions(initiator=self.account,
                                              clan=self.clan,
                                              member_clan_id=self.clan.id,
                                              member_role=member_role,
                                              expected_permissions=initiator_role.permissions)

    def test_member_not_from_clan(self):
        for is_moderator in (False, True):
            for initiator_role in relations.MEMBER_ROLE.records:
                models.Membership.objects.update(role=initiator_role)

                self.check_member_permissions(initiator=self.account,
                                              clan=self.clan,
                                              member_clan_id=None,
                                              member_role=None,
                                              expected_permissions=(),
                                              is_moderator=is_moderator)

    def test_member_from_other_clan(self):
        member = self.accounts_factory.create_account()
        self.create_clan(member, uid=2)

        for is_moderator in (False, True):
            for initiator_role in relations.MEMBER_ROLE.records:
                models.Membership.objects.filter(account_id=self.account.id).update(role=initiator_role)

                self.check_member_permissions(initiator=self.account,
                                              clan=self.clan,
                                              member_clan_id=None,
                                              member_role=None,
                                              expected_permissions=(),
                                              is_moderator=is_moderator)

    def test_operations_to_self_not_allowed(self):
        for initiator_role in relations.MEMBER_ROLE.records:
            models.Membership.objects.filter(account_id=self.account.id).update(role=initiator_role)

            self.check_member_permissions(initiator=self.account,
                                          clan=self.clan,
                                          member_clan_id=self.clan.id,
                                          member_role=initiator_role,
                                          expected_permissions=(),
                                          is_moderator=False)


class RemoveMemberTests(BaseClanTests):

    def test(self):
        member = self.accounts_factory.create_account()

        logic._add_member(clan=self.clan, account=member, role=relations.MEMBER_ROLE.RECRUIT)

        with self.check_new_message(member.id, [self.account.id]):
            logic.remove_member(initiator=self.account,
                                clan=self.clan,
                                member=member)

        self.assertFalse(models.Membership.objects.filter(account_id=member.id).exists())

        loaded_clan = logic.load_clan(clan_id=self.clan.id)
        self.assertEqual(loaded_clan.members_number, 1)

        total_events, events = tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(events[0].tags),
                         {self.clan.meta_object().tag,
                          relations.EVENT.MEMBER_REMOVED.meta_object().tag,
                          self.account.meta_object().tag,
                          member.meta_object().tag})


class LeaveClanTests(BaseClanTests):

    def test(self):
        member = self.accounts_factory.create_account()

        logic._add_member(clan=self.clan, account=member, role=relations.MEMBER_ROLE.RECRUIT)

        logic.leave_clan(initiator=member,
                         clan=self.clan)

        total_events, events = tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(events[0].tags),
                         {self.clan.meta_object().tag,
                          relations.EVENT.MEMBER_LEFT.meta_object().tag,
                          member.meta_object().tag})


class ChangeRoleTests(BaseClanTests):

    def test(self):
        member = self.accounts_factory.create_account()

        logic._add_member(clan=self.clan, account=member, role=relations.MEMBER_ROLE.RECRUIT)

        with self.check_new_message(member.id, [self.account.id]):
            logic.change_role(clan=self.clan,
                              initiator=self.account,
                              member=member,
                              new_role=relations.MEMBER_ROLE.COMANDOR)

        self.assertTrue(logic.get_member_role(clan=self.clan, member=member).is_COMANDOR)

        total_events, events = tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(events[0].tags),
                         {self.clan.meta_object().tag,
                          relations.EVENT.ROLE_CHANGED.meta_object().tag,
                          self.account.meta_object().tag,
                          member.meta_object().tag})


class ChangeOwnershipTests(BaseClanTests):

    def test(self):
        member = self.accounts_factory.create_account()

        logic._add_member(clan=self.clan, account=member, role=relations.MEMBER_ROLE.RECRUIT)

        with self.check_new_message(member.id, [self.account.id]):
            logic.change_ownership(clan=self.clan,
                                   initiator=self.account,
                                   member=member)

        self.assertTrue(logic.get_member_role(clan=self.clan, member=member).is_MASTER)
        self.assertTrue(logic.get_member_role(clan=self.clan, member=self.account).is_COMANDOR)

        total_events, events = tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(events[0].tags),
                         {self.clan.meta_object().tag,
                          relations.EVENT.OWNER_CHANGED.meta_object().tag,
                          self.account.meta_object().tag,
                          member.meta_object().tag})


class GetRecrutiersIdsTests(BaseClanTests):

    def test(self):
        expected_recrutiers = {self.account.id}

        for role in relations.MEMBER_ROLE.records:
            if role.is_MASTER:
                continue

            member = self.accounts_factory.create_account()

            if relations.PERMISSION.TAKE_MEMBER in role.permissions:
                expected_recrutiers.add(member.id)

            logic._add_member(clan=self.clan, account=member, role=role)

        account_2 = self.accounts_factory.create_account()
        self.create_clan(account_2, uid=2)

        recrutiers_ids = logic.get_recrutiers_ids(self.clan.id)

        self.assertEqual(set(recrutiers_ids), expected_recrutiers)


class CreateRequestTests(BaseClanTests):

    def test(self):
        comandor = self.accounts_factory.create_account()
        recruit = self.accounts_factory.create_account()
        member = self.accounts_factory.create_account()

        logic._add_member(clan=self.clan, account=comandor, role=relations.MEMBER_ROLE.COMANDOR)
        logic._add_member(clan=self.clan, account=recruit, role=relations.MEMBER_ROLE.RECRUIT)

        account_2 = self.accounts_factory.create_account()
        self.create_clan(account_2, uid=2)

        with self.check_new_message(self.account.id, [member.id]), \
             self.check_new_message(comandor.id, [member.id]), \
             self.check_no_messages(recruit.id), \
             self.check_no_messages(account_2.id):
            logic.create_request(initiator=member,
                                 clan=self.clan,
                                 text='xxx')

        total_events, events = tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(events[0].tags),
                         {self.clan.meta_object().tag,
                          relations.EVENT.NEW_MEMBERSHIP_REQUEST.meta_object().tag,
                          member.meta_object().tag})

        self.assertTrue(models.MembershipRequest.objects.filter(clan_id=self.clan.id,
                                                                account_id=member.id,
                                                                initiator_id=member.id,
                                                                type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT).exists())


class CreateInviteTests(BaseClanTests):

    def test(self):
        member = self.accounts_factory.create_account()

        with self.check_new_message(member.id, [self.account.id]):
            logic.create_invite(initiator=self.account,
                                clan=self.clan,
                                member=member,
                                text='xxx')

        total_events, events = tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(events[0].tags),
                         {self.clan.meta_object().tag,
                          relations.EVENT.NEW_MEMBERSHIP_INVITE.meta_object().tag,
                          self.account.meta_object().tag,
                          member.meta_object().tag})

        self.assertTrue(models.MembershipRequest.objects.filter(clan_id=self.clan.id,
                                                                account_id=member.id,
                                                                initiator_id=self.account.id,
                                                                type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_CLAN).exists())


class LoadRequestTests(BaseClanTests):

    def test_from_id(self):
        member = self.accounts_factory.create_account()

        logic.create_invite(initiator=self.account,
                            clan=self.clan,
                            member=member,
                            text='xxx')

        request_id = models.MembershipRequest.objects.values_list('id', flat=True)[0]

        request = logic.load_request(request_id=request_id)

        self.assertEqual(request.id, request_id)
        self.assertEqual(request.initiator_id, self.account.id)
        self.assertEqual(request.clan_id, self.clan.id)
        self.assertEqual(request.account_id, member.id)
        self.assertEqual(request.text, 'xxx')
        self.assertTrue(request.type.is_FROM_CLAN)

    def test_from_model(self):
        member = self.accounts_factory.create_account()

        logic.create_invite(initiator=self.account,
                            clan=self.clan,
                            member=member,
                            text='xxx')

        request_model = models.MembershipRequest.objects.all()[0]

        request = logic.load_request(request_model=request_model)

        self.assertEqual(request.id, request_model.id)
        self.assertEqual(request.initiator_id, self.account.id)
        self.assertEqual(request.clan_id, self.clan.id)
        self.assertEqual(request.account_id, member.id)
        self.assertEqual(request.text, 'xxx')
        self.assertTrue(request.type.is_FROM_CLAN)


class RequestsForAccountTests(BaseClanTests):

    def test(self):
        member_1 = self.accounts_factory.create_account()
        member_2 = self.accounts_factory.create_account()

        account_2 = self.accounts_factory.create_account()
        clan_2 = self.create_clan(account_2, uid=2)

        account_3 = self.accounts_factory.create_account()
        clan_3 = self.create_clan(account_3, uid=3)

        logic.create_invite(initiator=self.account,
                            clan=self.clan,
                            member=member_1,
                            text='x.1')

        logic.create_invite(initiator=self.account,
                            clan=self.clan,
                            member=member_2,
                            text='x.2')

        logic.create_invite(initiator=account_2,
                            clan=clan_2,
                            member=member_1,
                            text='x.3')

        logic.create_request(initiator=member_1,
                             clan=clan_3,
                             text='x.4')

        requests = logic.requests_for_account(member_1.id)

        self.assertEqual({request.text for request in requests},
                         {'x.1', 'x.3'})


class RequestForClanAndAccountTests(BaseClanTests):

    def test(self):
        member_1 = self.accounts_factory.create_account()
        member_2 = self.accounts_factory.create_account()

        account_2 = self.accounts_factory.create_account()
        clan_2 = self.create_clan(account_2, uid=2)

        account_3 = self.accounts_factory.create_account()
        clan_3 = self.create_clan(account_3, uid=3)

        logic.create_invite(initiator=self.account,
                            clan=self.clan,
                            member=member_1,
                            text='x.1')

        logic.create_invite(initiator=self.account,
                            clan=self.clan,
                            member=member_2,
                            text='x.2')

        logic.create_invite(initiator=account_2,
                            clan=clan_2,
                            member=member_1,
                            text='x.3')

        logic.create_request(initiator=member_1,
                             clan=clan_3,
                             text='x.4')

        request = logic.request_for_clan_and_account(self.clan.id, member_1.id)
        self.assertEqual(request.text, 'x.1')

        request = logic.request_for_clan_and_account(clan_2.id, member_1.id)
        self.assertEqual(request.text, 'x.3')

        request = logic.request_for_clan_and_account(clan_2.id, member_2.id)
        self.assertEqual(request, None)


class RequestsForClanTests(BaseClanTests):

    def test(self):
        member_1 = self.accounts_factory.create_account()
        member_2 = self.accounts_factory.create_account()
        member_3 = self.accounts_factory.create_account()

        account_2 = self.accounts_factory.create_account()
        clan_2 = self.create_clan(account_2, uid=2)

        account_3 = self.accounts_factory.create_account()
        clan_3 = self.create_clan(account_3, uid=3)

        logic.create_request(initiator=member_1,
                             clan=self.clan,
                             text='x.1')

        logic.create_request(initiator=member_1,
                             clan=clan_2,
                             text='x.2')

        logic.create_request(initiator=member_2,
                             clan=self.clan,
                             text='x.3')

        logic.create_invite(initiator=self.account,
                            clan=self.clan,
                            member=member_3,
                            text='x.4')

        logic.create_invite(initiator=account_3,
                            clan=clan_3,
                            member=member_1,
                            text='x.5')

        requests = logic.requests_for_clan(self.clan.id)

        self.assertEqual({request.text for request in requests},
                         {'x.1', 'x.3'})


class RequestsNumberForClanTests(BaseClanTests):

    def test(self):
        member_1 = self.accounts_factory.create_account()
        member_2 = self.accounts_factory.create_account()
        member_3 = self.accounts_factory.create_account()

        account_2 = self.accounts_factory.create_account()
        clan_2 = self.create_clan(account_2, uid=2)

        account_3 = self.accounts_factory.create_account()
        clan_3 = self.create_clan(account_3, uid=3)

        logic.create_request(initiator=member_1,
                             clan=self.clan,
                             text='x.1')

        logic.create_request(initiator=member_1,
                             clan=clan_2,
                             text='x.2')

        logic.create_request(initiator=member_2,
                             clan=self.clan,
                             text='x.3')

        logic.create_invite(initiator=self.account,
                            clan=self.clan,
                            member=member_3,
                            text='x.4')

        logic.create_invite(initiator=account_3,
                            clan=clan_3,
                            member=member_1,
                            text='x.5')

        self.assertEqual(logic.requests_number_for_clan(self.clan.id), 2)


class RejectInviteTests(BaseClanTests):

    def test(self):
        member = self.accounts_factory.create_account()

        request_id = logic.create_invite(initiator=self.account,
                                         clan=self.clan,
                                         member=member,
                                         text='xxx')

        with self.check_new_message(self.account.id, [member.id]):
            logic.reject_invite(logic.load_request(request_id=request_id))

        total_events, events = tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(events[0].tags),
                         {self.clan.meta_object().tag,
                          relations.EVENT.MEMBERSHIP_INVITE_REJECTED.meta_object().tag,
                          member.meta_object().tag})

        self.assertFalse(models.MembershipRequest.objects.exists())

        self.assertEqual(models.Membership.objects.count(), 1)


class RejectRequestTests(BaseClanTests):

    def test(self):
        member = self.accounts_factory.create_account()

        request_id = logic.create_request(initiator=member,
                                          clan=self.clan,
                                          text='xxx')

        with self.check_new_message(member.id, [self.account.id]):
            logic.reject_request(initiator=self.account,
                                 membership_request=logic.load_request(request_id=request_id))

        total_events, events = tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(events[0].tags),
                         {self.clan.meta_object().tag,
                          relations.EVENT.MEMBERSHIP_REQUEST_REJECTED.meta_object().tag,
                          self.account.meta_object().tag,
                          member.meta_object().tag})

        self.assertFalse(models.MembershipRequest.objects.exists())

        self.assertEqual(models.Membership.objects.count(), 1)


class AcceptInviteTests(BaseClanTests):

    def test(self):
        member = self.accounts_factory.create_account()

        request_id = logic.create_invite(initiator=self.account,
                                         clan=self.clan,
                                         member=member,
                                         text='xxx')

        logic.accept_invite(logic.load_request(request_id=request_id))

        total_events, events = tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(events[0].tags),
                         {self.clan.meta_object().tag,
                          relations.EVENT.MEMBERSHIP_INVITE_ACCEPTED.meta_object().tag,
                          member.meta_object().tag})

        self.assertFalse(models.MembershipRequest.objects.exists())

        self.assertEqual(models.Membership.objects.count(), 2)

        self.assertEqual(set(models.Membership.objects.filter(clan_id=self.clan.id).values_list('clan_id', 'account_id', 'role')),
                         {(self.clan.id, self.account.id, relations.MEMBER_ROLE.MASTER),
                          (self.clan.id, member.id, relations.MEMBER_ROLE.RECRUIT)})

        loaded_clan = logic.load_clan(clan_id=self.clan.id)
        self.assertEqual(loaded_clan.members_number, 2)


class AccountRequestTests(BaseClanTests):

    def test(self):
        member = self.accounts_factory.create_account()

        request_id = logic.create_request(initiator=member,
                                          clan=self.clan,
                                          text='xxx')

        with self.check_new_message(member.id, [self.account.id]):
            logic.accept_request(initiator=self.account,
                                 membership_request=logic.load_request(request_id=request_id))

        total_events, events = tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(events[0].tags),
                         {self.clan.meta_object().tag,
                          relations.EVENT.MEMBERSHIP_REQUEST_ACCEPTED.meta_object().tag,
                          self.account.meta_object().tag,
                          member.meta_object().tag})

        self.assertFalse(models.MembershipRequest.objects.exists())

        self.assertEqual(set(models.Membership.objects.filter(clan_id=self.clan.id).values_list('clan_id', 'account_id', 'role')),
                         {(self.clan.id, self.account.id, relations.MEMBER_ROLE.MASTER),
                          (self.clan.id, member.id, relations.MEMBER_ROLE.RECRUIT)})

        loaded_clan = logic.load_clan(clan_id=self.clan.id)
        self.assertEqual(loaded_clan.members_number, 2)
