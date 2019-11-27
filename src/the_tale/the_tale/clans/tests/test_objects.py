import smart_imports

smart_imports.all()


class TestMembership(dext_testcase.TestCase):

    def test_recruite_is_freezed(self):
        membership = objects.Membership(clan_id=1,
                                        account_id=2,
                                        role=relations.MEMBER_ROLE.RECRUIT,
                                        created_at=datetime.datetime.now(),
                                        updated_at=datetime.datetime.now())

        self.assertTrue(membership.is_freezed())

        membership.updated_at -= datetime.timedelta(days=conf.settings.RECRUITE_FREEZE_PERIOD)

        self.assertFalse(membership.is_freezed())

    def test_non_recruites_not_freezed(self):
        for role in relations.MEMBER_ROLE.records:
            if role.is_RECRUIT:
                continue

            membership = objects.Membership(clan_id=1,
                                            account_id=2,
                                            role=role,
                                            created_at=datetime.datetime.now(),
                                            updated_at=datetime.datetime.now())

            self.assertFalse(membership.is_freezed())


# for complex permissions tests see test_logic.OperationsRightsTests
class TestOperationsRights(dext_testcase.TestCase):

    def test_initialize(self):
        rights = objects.OperationsRights(clan_id=666,
                                          initiator_role=relations.MEMBER_ROLE.COMANDOR,
                                          is_moderator=True)

        self.assertEqual(rights.clan_id, 666)
        self.assertTrue(rights.initiator_role.is_COMANDOR)
        self.assertTrue(rights.is_moderator)

    def test_static_permissions__all(self):
        rights = objects.OperationsRights(clan_id=666,
                                          initiator_role=relations.MEMBER_ROLE.MASTER,
                                          is_moderator=False)

        for permission in relations.PERMISSION.records:
            if permission.on_member:
                continue

            self.assertTrue(getattr(rights, 'can_{}'.format(permission.name.lower()))())

    def test_static_permissions__none(self):
        rights = objects.OperationsRights(clan_id=666,
                                          initiator_role=relations.MEMBER_ROLE.RECRUIT,
                                          is_moderator=False)

        for permission in relations.PERMISSION.records:
            if permission.on_member:
                continue

            self.assertFalse(getattr(rights, 'can_{}'.format(permission.name.lower()))())

    def test_static_permissions__member_all(self):
        rights = objects.OperationsRights(clan_id=666,
                                          initiator_role=relations.MEMBER_ROLE.MASTER,
                                          is_moderator=False)

        membership = objects.Membership(clan_id=666,
                                        account_id=777,
                                        role=relations.MEMBER_ROLE.FIGHTER,
                                        created_at=datetime.datetime.now(),
                                        updated_at=datetime.datetime.now())

        for permission in relations.PERMISSION.records:
            if not permission.on_member:
                continue

            self.assertTrue(getattr(rights, 'can_{}'.format(permission.name.lower()))(membership))

    def test_static_permissions__member_none(self):
        rights = objects.OperationsRights(clan_id=666,
                                          initiator_role=relations.MEMBER_ROLE.RECRUIT,
                                          is_moderator=False)

        membership = objects.Membership(clan_id=666,
                                        account_id=777,
                                        role=relations.MEMBER_ROLE.MASTER,
                                        created_at=datetime.datetime.now(),
                                        updated_at=datetime.datetime.now())

        for permission in relations.PERMISSION.records:
            if not permission.on_member:
                continue

            self.assertFalse(getattr(rights, 'can_{}'.format(permission.name.lower()))(membership))

    def test_can_change_role_for_master(self):
        for is_moderator in (True, False):
            rights = objects.OperationsRights(clan_id=666,
                                              initiator_role=relations.MEMBER_ROLE.MASTER,
                                              is_moderator=is_moderator)

            membership = objects.Membership(clan_id=666,
                                            account_id=777,
                                            role=relations.MEMBER_ROLE.MASTER,
                                            created_at=datetime.datetime.now(),
                                            updated_at=datetime.datetime.now())

            self.assertFalse(rights.can_change_role(membership))


class TestAttributes(dext_testcase.TestCase):

    def test_initialize(self):
        attributes = objects.Attributes(fighters_maximum_level=1,
                                        emissary_maximum_level=2,
                                        points_gain_level=3,
                                        free_quests_maximum_level=4)

        self.assertEqual(attributes.fighters_maximum_level, 1)
        self.assertEqual(attributes.emissary_maximum_level, 2)
        self.assertEqual(attributes.points_gain_level, 3)
        self.assertEqual(attributes.free_quests_maximum_level, 4)

        self.assertEqual(attributes.fighters_maximum, tt_clans_constants.INITIAL_FIGHTERS_MAXIMUM + 1)
        self.assertEqual(attributes.emissary_maximum, tt_clans_constants.INITIAL_EMISSARY_MAXIMUM + 2)
        self.assertEqual(attributes.points_gain, int(math.ceil((tt_clans_constants.INITIAL_POINTS_GAIN + 3 * 85) / 24)))
        self.assertEqual(attributes.free_quests_maximum, tt_clans_constants.INITIAL_FREE_QUESTS_MAXIMUM + 4)
