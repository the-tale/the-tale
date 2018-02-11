

from tt_logic.cards import constants as logic_cards_constants

from the_tale.common.utils import testcase

from .. import tt_api
from .. import relations
from .. import exceptions


class CreateCardsTimerTests(testcase.TestCase):

    def setUp(self):
        tt_api.debug_clear_service()

    def test_create_timer(self):
        tt_api.create_cards_timer(account_id=666)

        timers = tt_api.get_owner_timers(account_id=666)

        self.assertEqual(len(timers), 1)

        self.assertEqual(timers[0].entity_id, 0)
        self.assertEqual(timers[0].type, relations.PLAYER_TIMERS_TYPES.CARDS_MINER)
        self.assertEqual(timers[0].speed, 1)
        self.assertEqual(timers[0].border, logic_cards_constants.RECEIVE_TIME)

    def test_exception_in_error(self):
        tt_api.create_cards_timer(account_id=666)

        with self.assertRaises(exceptions.CanNotCreateCardsTimer):
            tt_api.create_cards_timer(account_id=666)


class ChangeCardsTimerSpeedTests(testcase.TestCase):

    def setUp(self):
        tt_api.debug_clear_service()

    def test_create_timer(self):
        tt_api.create_cards_timer(account_id=666)

        tt_api.change_cards_timer_speed(account_id=666, speed=2)

        timers = tt_api.get_owner_timers(account_id=666)

        self.assertEqual(len(timers), 1)

        self.assertEqual(timers[0].entity_id, 0)
        self.assertEqual(timers[0].type, relations.PLAYER_TIMERS_TYPES.CARDS_MINER)
        self.assertEqual(timers[0].speed, 2)
        self.assertEqual(timers[0].border, logic_cards_constants.RECEIVE_TIME)

    def test_exception_in_error(self):
        tt_api.create_cards_timer(account_id=666)

        with self.assertRaises(exceptions.CanNotChangeCardsTimerSpeed):
            tt_api.change_cards_timer_speed(account_id=777, speed=2)


class GetOwnerTimersTests(testcase.TestCase):

    def setUp(self):
        tt_api.debug_clear_service()

    def test_create_timer(self):
        tt_api.create_cards_timer(account_id=666)

        timers = tt_api.get_owner_timers(account_id=666)

        self.assertEqual(len(timers), 1)

        self.assertEqual(timers[0].entity_id, 0)
        self.assertEqual(timers[0].type, relations.PLAYER_TIMERS_TYPES.CARDS_MINER)
        self.assertEqual(timers[0].speed, 1)
        self.assertEqual(timers[0].border, logic_cards_constants.RECEIVE_TIME)
