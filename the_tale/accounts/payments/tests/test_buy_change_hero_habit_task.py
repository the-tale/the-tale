# coding: utf-8

import random

from the_tale.accounts.payments.postponed_tasks import BuyChangeHeroHabits
from the_tale.accounts.payments.tests.base_buy_task_tests import BaseBuyHeroMethodPosponedTaskTests as _BaseBuyHeroMethodPosponedTaskTests

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.heroes.relations import HABIT_TYPE


class BuyChangeHeroHabitsTaskTests(_BaseBuyHeroMethodPosponedTaskTests):

    def setUp(self):
        super(BuyChangeHeroHabitsTaskTests, self).setUp()

        self.habit_type = random.choice(HABIT_TYPE.records)
        self.habit_value = 666

        self.task = BuyChangeHeroHabits(account_id=self.account.id,
                                        habit_type=self.habit_type,
                                        habit_value=self.habit_value,
                                        transaction=self.transaction)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.cmd_update_with_account_data__call_count = 0
        self.accounts_manages_worker = False
        self.supervisor_worker = True

        self.hero = self.storage.accounts_to_heroes[self.account.id]
        self.hero._model.energy_bonus = 0

    @property
    def habit(self):
        if self.habit_type.is_HONOR:
            return self.hero.habit_honor

        if self.habit_type.is_PEACEFULNESS:
            return self.hero.habit_peacefulness

    def _get_expected_arguments(self):
        return {'habit_type': self.habit_type,
                'habit_value': self.habit_value}

    def _check_not_used(self):
        self.assertEqual(self.habit.raw_value, 0)

    def _check_used(self):
        self.assertEqual(self.habit.raw_value, 666)
