
import smart_imports

smart_imports.all()


class ConstructUserInfoTests(clans_helpers.ClansTestsMixin,
                             utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

    def test_nick(self):
        user = discord.construct_user_info(self.account)

        self.assertEqual(user.nickname, self.account.nick_verbose)

    def test_nick__clan(self):
        self.prepair_forum_for_clans()

        self.create_clan(self.account, 1)

        user = discord.construct_user_info(self.account)

        self.assertEqual(user.nickname, f'[a-1] ♔ {self.account.nick_verbose}')

    @mock.patch('the_tale.accounts.conf.settings.DEVELOPERS_IDS', [])
    @mock.patch('the_tale.accounts.conf.settings.MODERATORS_IDS', [])
    def test_roles(self):

        for might in (0, 99):
            self.account.set_might(might)
            user = discord.construct_user_info(self.account)
            self.assertEqual(user.roles, [discord.DISCORD_ROLE.SPIRIT_OF_PANDORA.name.lower()])

        for might in (100, 999):
            self.account.set_might(might)
            user = discord.construct_user_info(self.account)
            self.assertEqual(user.roles, [discord.DISCORD_ROLE.KEEPER.name.lower()])

        for might in (1000, 9999):
            self.account.set_might(might)
            user = discord.construct_user_info(self.account)
            self.assertEqual(user.roles, [discord.DISCORD_ROLE.MIGHTY_KEEPER.name.lower()])

        for might in (10000,):
            self.account.set_might(might)
            user = discord.construct_user_info(self.account)
            self.assertEqual(user.roles, [discord.DISCORD_ROLE.PILLAR_OF_WORLD.name.lower()])

    def test_roles__special(self):

        self.account.set_might(0)

        with mock.patch('the_tale.accounts.conf.settings.DEVELOPERS_IDS', []):
            with mock.patch('the_tale.accounts.conf.settings.MODERATORS_IDS', [self.account.id]):

                user = discord.construct_user_info(self.account)
                self.assertEqual(set(user.roles), {discord.DISCORD_ROLE.SPIRIT_OF_PANDORA.name.lower(),
                                                   discord.DISCORD_ROLE.MODERATOR.name.lower()})

    def test_roles__clan(self):

        self.prepair_forum_for_clans()

        clan = self.create_clan(self.account, 1)

        for role in [clans_relations.MEMBER_ROLE.MASTER,
                     clans_relations.MEMBER_ROLE.COMANDOR]:

            clans_models.Membership.objects.filter(clan_id=clan.id,
                                                   account_id=self.account.id).update(role=role)

            user = discord.construct_user_info(self.account)
            self.assertEqual(set(user.roles), {discord.DISCORD_ROLE.SPIRIT_OF_PANDORA.name.lower(),
                                               discord.DISCORD_ROLE.CLAN_COMMAND.name.lower()})

        for role in clans_relations.MEMBER_ROLE.records:

            if role in [clans_relations.MEMBER_ROLE.MASTER,
                        clans_relations.MEMBER_ROLE.COMANDOR]:
                continue

            clans_models.Membership.objects.filter(clan_id=clan.id,
                                                   account_id=self.account.id).update(role=role)

            user = discord.construct_user_info(self.account)
            self.assertEqual(set(user.roles), {discord.DISCORD_ROLE.SPIRIT_OF_PANDORA.name.lower()})

    def test_ban(self):
        user = discord.construct_user_info(self.account)
        self.assertFalse(user.banned)

        self.account.ban_game(1)
        user = discord.construct_user_info(self.account)
        self.assertFalse(user.banned)

        self.account.ban_forum(1)
        user = discord.construct_user_info(self.account)
        self.assertTrue(user.banned)
