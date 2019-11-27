
import smart_imports

smart_imports.all()


class PermissionsListTests(utils_testcase.TestCase):

    def test_permissions_not_changed_unexpectedly(self):
        expected_permissions = {relations.MEMBER_ROLE.MASTER: {relations.PERMISSION.DESTROY,
                                                               relations.PERMISSION.CHANGE_OWNER,
                                                               relations.PERMISSION.EDIT,
                                                               relations.PERMISSION.CHANGE_ROLE,
                                                               relations.PERMISSION.POLITICS,
                                                               relations.PERMISSION.EMISSARIES_RELOCATION,
                                                               relations.PERMISSION.EMISSARIES_PLANING,
                                                               relations.PERMISSION.EMISSARIES_QUESTS,
                                                               relations.PERMISSION.TAKE_MEMBER,
                                                               relations.PERMISSION.REMOVE_MEMBER,
                                                               relations.PERMISSION.FORUM_MODERATION,
                                                               relations.PERMISSION.ACCESS_CHRONICLE,
                                                               relations.PERMISSION.BULK_MAILING},
                                relations.MEMBER_ROLE.COMANDOR: {relations.PERMISSION.EDIT,
                                                                 relations.PERMISSION.CHANGE_ROLE,
                                                                 relations.PERMISSION.POLITICS,
                                                                 relations.PERMISSION.EMISSARIES_RELOCATION,
                                                                 relations.PERMISSION.EMISSARIES_PLANING,
                                                                 relations.PERMISSION.EMISSARIES_QUESTS,
                                                                 relations.PERMISSION.TAKE_MEMBER,
                                                                 relations.PERMISSION.REMOVE_MEMBER,
                                                                 relations.PERMISSION.FORUM_MODERATION,
                                                                 relations.PERMISSION.ACCESS_CHRONICLE,
                                                                 relations.PERMISSION.BULK_MAILING},
                                relations.MEMBER_ROLE.OFFICER: {relations.PERMISSION.EMISSARIES_PLANING,
                                                                relations.PERMISSION.EMISSARIES_QUESTS,
                                                                relations.PERMISSION.TAKE_MEMBER,
                                                                relations.PERMISSION.REMOVE_MEMBER,
                                                                relations.PERMISSION.FORUM_MODERATION,
                                                                relations.PERMISSION.ACCESS_CHRONICLE,
                                                                relations.PERMISSION.BULK_MAILING},
                                relations.MEMBER_ROLE.FIGHTER: {relations.PERMISSION.EMISSARIES_QUESTS,
                                                                relations.PERMISSION.ACCESS_CHRONICLE,
                                                                relations.PERMISSION.BULK_MAILING},
                                relations.MEMBER_ROLE.RECRUIT: set()}

        for role in relations.MEMBER_ROLE.records:
            self.assertEqual(set(role.permissions), expected_permissions[role])
