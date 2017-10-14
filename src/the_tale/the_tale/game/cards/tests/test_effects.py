
import uuid

from unittest import mock

from the_tale.common.utils import testcase

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from .. import relations
from .. import effects
from .. import objects
from .. import tt_api
from .. import logic
from .. import cards


class EffectsTests(testcase.TestCase):

    def setUp(self):
        super().setUp()

        create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        tt_api.debug_clear_service()

        self.card = objects.Card(cards.CARD.KEEPERS_GOODS_COMMON, uid=uuid.uuid4())

        tt_api.change_cards(account_id=self.hero.account_id, operation_type='#test', to_add=[self.card])

        self.task_data = {'card': {'id': self.card.uid.hex,
                                   'data': self.card.serialize()}}


    def test_check_hero_conditions__has_card(self):
        self.assertTrue(self.card.effect.check_hero_conditions(self.hero, self.task_data))


    def test_check_hero_conditions__has_no_card(self):
        tt_api.change_cards(account_id=self.hero.account_id, operation_type='#test', to_remove=[self.card])
        self.assertFalse(self.card.effect.check_hero_conditions(self.hero, self.task_data))


    def test_hero_actions(self):
        card_2 = objects.Card(cards.CARD.KEEPERS_GOODS_COMMON, uid=uuid.uuid4())

        tt_api.change_cards(account_id=self.hero.account_id, operation_type='#test', to_add=[card_2])

        self.assertEqual(self.card.type, card_2.type)

        account_cards = tt_api.load_cards(self.hero.account_id)
        self.assertEqual(len(account_cards), 2)

        with self.check_delta(lambda: self.hero.statistics.cards_used, 1):
            self.card.effect.hero_actions(self.hero, self.task_data)

        account_cards = tt_api.load_cards(self.hero.account_id)
        self.assertEqual(len(account_cards), 1)

        self.assertIn(card_2.uid, account_cards)
        self.assertNotIn(self.card.uid, account_cards)


    def test_activate(self):
        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_logic_task') as cmd_logic_task:
            task = self.card.effect.activate(self.hero, self.card, {'x': 'y'})

        self.assertEqual(cmd_logic_task.call_args_list, [mock.call(self.hero.account_id, task.id)])
