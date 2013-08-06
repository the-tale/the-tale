# coding: utf-8

from common.utils import testcase

from game.logic import create_test_map

from accounts.logic import register_user
from accounts.prototypes import AccountPrototype

from accounts.clans.prototypes import ClanPrototype, ClanMembershipPrototype


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

        membership = ClanMembershipPrototype.get_by_account_id(self.account.id)

        self.assertEqual(membership.clan_id, self.clan.id)
        self.assertEqual(membership.account_id, self.account.id)
        self.assertTrue(membership.role._is_LEADER)
