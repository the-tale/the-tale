
from the_tale.common.utils import testcase

from the_tale.game.logic import create_test_map
from the_tale.game import turn
from the_tale.game.logic_storage import LogicStorage


class GameTest(testcase.TestCase):

    def test_statistics_consistency(self):
        create_test_map()

        account = self.accounts_factory.create_account(is_fast=True)

        self.storage = LogicStorage()
        self.storage.load_account_data(account)
        self.hero = self.storage.accounts_to_heroes[account.id]

        for i in range(10000):
            self.storage.process_turn()
            turn.increment()

        self.assertEqual(self.hero.money, self.hero.statistics.money_earned - self.hero.statistics.money_spend)
