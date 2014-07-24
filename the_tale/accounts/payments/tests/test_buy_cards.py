# coding: utf-8

from the_tale.accounts.payments.postponed_tasks import BuyCards
from the_tale.accounts.payments.tests import base_buy_task

from the_tale.game.cards.relations import CARD_TYPE

from the_tale.game.logic_storage import LogicStorage


class BuyEnergyTaskTests(base_buy_task._BaseBuyHeroMethodPosponedTaskTests):

    def setUp(self):
        super(BuyEnergyTaskTests, self).setUp()
        self.card_type = CARD_TYPE.KEEPERS_GOODS_COMMON
        self.count = 666

        self.task = BuyCards(account_id=self.account.id,
                             card_type=self.card_type,
                             count=self.count,
                             transaction=self.transaction)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.cmd_update_with_account_data__call_count = 0
        self.accounts_manages_worker = False
        self.supervisor_worker = True

        self.hero = self.storage.accounts_to_heroes[self.account.id]
        self.hero._model.energy_bonus = 0

    def _get_expected_arguments(self):
        return {'card_type': self.card_type,
                'count': self.count}

    def _check_not_used(self):
        self.assertFalse(self.hero.cards.has_cards)

    def _check_used(self):
        self.assertEqual(self.hero.cards.cards, [(self.card_type, self.count)])
