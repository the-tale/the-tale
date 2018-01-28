
import datetime

from tt_logic.cards import constants as logic_cards_constants

from the_tale.accounts import tt_api as accounts_tt_api

from the_tale.finances.shop.postponed_tasks import BuyPremium
from the_tale.finances.shop.tests import base_buy_task


class BuyPremiumPosponedTaskTests(base_buy_task._BaseBuyPosponedTaskTests):

    def setUp(self):
        super(BuyPremiumPosponedTaskTests, self).setUp()
        self.days = 13

        self.task = BuyPremium(account_id=self.account.id,
                               days=self.days,
                               transaction=self.transaction)

    def check_timers_speed(self, cards_timer_speed):
        timers = accounts_tt_api.get_owner_timers(self.account.id)

        new_card_timer = None

        for timer in timers:
            if timer.type.is_CARDS_MINER:
                new_card_timer = timer
                break

        self.assertEqual(new_card_timer.speed, cards_timer_speed)

    def _test_create(self):
        self.assertEqual(self.task.days, self.days)

        self.check_timers_speed(cards_timer_speed=logic_cards_constants.NORMAL_PLAYER_SPEED)

    def _test_process__transaction_requested__invoice_unprocessed(self):
        self.account.reload()
        self.assertTrue(self.account.premium_end_at < datetime.datetime.now())

        self.check_timers_speed(cards_timer_speed=logic_cards_constants.NORMAL_PLAYER_SPEED)

    def _test_process__transaction_requested__invoice_rejected(self):
        self.account.reload()
        self.assertTrue(self.account.premium_end_at < datetime.datetime.now())

        self.check_timers_speed(cards_timer_speed=logic_cards_constants.NORMAL_PLAYER_SPEED)

    def _test_process__transaction_requested__invoice_wrong_state(self):
        self.account.reload()
        self.assertTrue(self.account.premium_end_at < datetime.datetime.now())

        self.check_timers_speed(cards_timer_speed=logic_cards_constants.NORMAL_PLAYER_SPEED)

    def _test_process__transaction_requested__invoice_frozen(self):
        self.account.reload()
        self.assertTrue(self.account.premium_end_at < datetime.datetime.now())

        self.check_timers_speed(cards_timer_speed=logic_cards_constants.NORMAL_PLAYER_SPEED)

    def _test_process__transaction_frozen(self):
        self.account.reload()
        self.assertTrue(self.account.premium_end_at > datetime.datetime.now())
        self.assertTrue(datetime.datetime.now() + datetime.timedelta(days=self.days-1) < self.account.premium_end_at)
        self.assertTrue(datetime.datetime.now() + datetime.timedelta(days=self.days+1) > self.account.premium_end_at)

        self.check_timers_speed(cards_timer_speed=logic_cards_constants.PREMIUM_PLAYER_SPEED)

    def _test_process__wrong_state(self):
        self.account.reload()
        self.assertTrue(self.account.premium_end_at < datetime.datetime.now())

        self.check_timers_speed(cards_timer_speed=logic_cards_constants.NORMAL_PLAYER_SPEED)
