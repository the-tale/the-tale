
import smart_imports

smart_imports.all()


discord_client = portal_tt_services.discord


class TTAPiTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()
        discord_client.cmd_debug_clear_service()

        self.account = self.accounts_factory.create_account()

    def test_get_bind_code(self):

        bind_code = discord_client.cmd_get_bind_code(portal_discord.construct_user_info(self.account), expire_timeout=60)

        self.assertTrue(isinstance(bind_code.code, uuid.UUID))

        self.assertEqual(bind_code.created_at + datetime.timedelta(seconds=60),
                         bind_code.expire_at)

    def test_update_user(self):

        discord_client.cmd_update_user(portal_discord.construct_user_info(self.account))
