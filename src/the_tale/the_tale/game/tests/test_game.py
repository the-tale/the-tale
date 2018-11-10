
import smart_imports

smart_imports.all()


class GameTest(utils_testcase.TestCase):

    def test_statistics_consistency(self):
        logic.create_test_map()

        account = self.accounts_factory.create_account(is_fast=True)

        self.storage = logic_storage.LogicStorage()
        self.storage.load_account_data(account)
        self.hero = self.storage.accounts_to_heroes[account.id]

        for i in range(10000):
            self.storage.process_turn()
            game_turn.increment()

        self.assertEqual(self.hero.money, self.hero.statistics.money_earned - self.hero.statistics.money_spend)
