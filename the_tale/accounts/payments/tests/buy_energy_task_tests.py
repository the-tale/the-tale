# coding: utf-8

from the_tale.accounts.payments.postponed_tasks import BuyEnergy
from the_tale.accounts.payments.tests.base_buy_task_tests import BaseBuyHeroMethodPosponedTaskTests as _BaseBuyHeroMethodPosponedTaskTests

from the_tale.game.logic_storage import LogicStorage


class BuyEnergyTaskTests(_BaseBuyHeroMethodPosponedTaskTests):

    def setUp(self):
        super(BuyEnergyTaskTests, self).setUp()
        self.energy = 666

        self.task = BuyEnergy(account_id=self.account.id,
                              energy=self.energy,
                              transaction=self.transaction)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.cmd_update_with_account_data__call_count = 0
        self.accounts_manages_worker = False
        self.supervisor_worker = True

        self.hero = self.storage.accounts_to_heroes[self.account.id]
        self.hero._model.energy_bonus = 0

    def _get_expected_arguments(self):
        return {'energy': self.energy}

    def _check_not_used(self):
        self.assertEqual(self.hero.energy_bonus, 0)

    def _check_used(self):
        self.assertEqual(self.hero.energy_bonus, self.energy)
