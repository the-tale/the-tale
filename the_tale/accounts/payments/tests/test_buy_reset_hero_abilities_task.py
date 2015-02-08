# coding: utf-8

from the_tale.accounts.payments.postponed_tasks import BuyResetHeroAbilities
from the_tale.accounts.payments.tests import base_buy_task

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.heroes.habilities.battle import HIT


class BuyResetHeroAbilitiesTaskTests(base_buy_task._BaseBuyHeroMethodPosponedTaskTests):

    def setUp(self):
        super(BuyResetHeroAbilitiesTaskTests, self).setUp()

        self.task = BuyResetHeroAbilities(account_id=self.account.id,
                                          transaction=self.transaction)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.cmd_update_with_account_data__call_count = 0
        self.accounts_manages_worker = False
        self.supervisor_worker = True

        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero._model.level = 5

        self.hero.randomized_level_up()
        self.hero.randomized_level_up()
        self.hero.randomized_level_up()

        self.hero.save()

        self.assertEqual(self.hero.abilities.current_ability_points_number, 5)

    def _get_expected_arguments(self):
        return {}

    def _check_not_used(self):
        self.assertEqual(self.hero.abilities.current_ability_points_number, 5)
        self.assertTrue(len(self.hero.abilities.abilities) > 1)

    def _check_used(self):
        self.assertEqual(self.hero.abilities.current_ability_points_number, 2)
        self.assertTrue(self.hero.abilities.abilities.keys(), [HIT.get_id()] )
