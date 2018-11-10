import smart_imports

smart_imports.all()


# for complex permissions tests see test_logic.OperationsRightsTests
class TestOperationsRights(dext_testcase.TestCase):

    def setUp(self):
        super().setUp()

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
                                        role=relations.MEMBER_ROLE.RECRUIT)

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
                                        role=relations.MEMBER_ROLE.MASTER)

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
                                            role=relations.MEMBER_ROLE.MASTER)

            self.assertFalse(rights.can_change_role(membership))
