
import smart_imports

smart_imports.all()


# xsolla_client = shop_tt_services.xsolla


# class TTAPiTests(utils_testcase.TestCase):

#     def setUp(self):
#         super().setUp()
#         game_logic.create_test_map()
#         xsolla_client.cmd_debug_clear_service()

#         self.account_1 = self.accounts_factory.create_account()
#         self.account_2 = self.accounts_factory.create_account()

#     def test_get_token(self):
#         token_1 = xsolla_client.cmd_get_token(self.account_1)
#         self.assertNotEqual(token, None)

#         token_2 = xsolla_client.cmd_get_token(self.account_2)
#         self.assertNotEqual(token_1, token_2)

#         token_3 = xsolla_client.cmd_get_token(self.account_1)
#         self.assertEqual(token_1, token_3)
