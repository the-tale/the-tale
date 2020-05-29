
import smart_imports

smart_imports.all()


class CollectAccountDataTests(helpers.ClansTestsMixin,
                              utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()

        self.prepair_forum_for_clans()

        self.accounts = [self.accounts_factory.create_account()
                         for _ in range(2)]

        self.clan = self.create_clan(self.accounts[0], uid=1)

    def test_no_clan_data(self):
        report = data_protection.collect_account_data(self.accounts[1].id)
        self.assertEqual(report, [('clan_id', None)])

    def test_has_clan_data(self):
        report = data_protection.collect_account_data(self.accounts[0].id)
        self.assertEqual(report, [('clan_id', self.clan.id)])


class RemoveAccountDataTests(helpers.ClansTestsMixin,
                             utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()

        self.prepair_forum_for_clans()

        self.accounts = [self.accounts_factory.create_account()
                         for _ in range(5)]

        self.clans = [self.create_clan(self.accounts[0], uid=1),
                      self.create_clan(self.accounts[1], uid=2),
                      self.create_clan(self.accounts[2], uid=3)]

        logic._add_member(clan=self.clans[1],
                          account=self.accounts[3],
                          role=relations.MEMBER_ROLE.OFFICER)

    def test_no_clan_data(self):
        with self.check_not_changed(models.Clan.objects.filter(state=relations.STATE.ACTIVE).count):
            with self.check_not_changed(models.Membership.objects.count):
                data_protection.remove_account_data(self.accounts[4].id)

    def test_single_clan_member(self):
        with self.check_delta(models.Clan.objects.filter(state=relations.STATE.REMOVED).count, 1):
            with self.check_delta(models.Membership.objects.count, -1):
                data_protection.remove_account_data(self.accounts[0].id)

        self.assertTrue(models.Clan.objects.get(id=self.clans[0].id).state.is_REMOVED)

    def test_multiple_clan_members(self):
        with self.check_not_changed(models.Clan.objects.filter(state=relations.STATE.ACTIVE).count):
            with self.check_delta(lambda: logic.members_number(self.clans[1].id), -1):
                data_protection.remove_account_data(self.accounts[3].id)
