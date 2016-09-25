# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.cards import relations
from the_tale.game.cards import effects
from the_tale.game.cards import objects


class PrototypesTests(testcase.TestCase):

    def setUp(self):
        super(PrototypesTests, self).setUp()

        create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.card_effect = effects.EFFECTS[relations.CARD_TYPE.KEEPERS_GOODS_COMMON]
        self.card_1 = objects.Card(relations.CARD_TYPE.KEEPERS_GOODS_COMMON)

        self.hero.cards.add_card(self.card_1)

        self.task_data = {'card_uid': self.card_1.uid}


    def test_check_hero_conditions__has_card(self):
        self.assertTrue(self.card_effect.check_hero_conditions(self.hero, self.task_data))


    def test_check_hero_conditions__has_no_card(self):
        self.hero.cards.remove_card(self.card_1.uid)
        self.assertFalse(self.card_effect.check_hero_conditions(self.hero, self.task_data))


    def test_hero_actions(self):
        card_2 = objects.Card(relations.CARD_TYPE.KEEPERS_GOODS_COMMON)
        self.hero.cards.add_card(card_2)

        self.assertEqual(self.card_1.type, card_2.type)
        self.assertEqual(self.hero.cards.cards_count(), 2)

        with self.check_delta(lambda: self.hero.statistics.cards_used, 1):
            self.card_effect.hero_actions(self.hero, self.task_data)

        self.assertEqual(self.hero.cards.cards_count(), 1)
        self.assertTrue(self.hero.cards.has_card(card_2.uid))
        self.assertFalse(self.hero.cards.has_card(self.card_1.uid))


    def test_activate(self):
        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_logic_task') as cmd_logic_task:
            task = self.card_effect.activate(self.hero, self.card_1.uid, {'x': 'y'})

        self.assertEqual(cmd_logic_task.call_args_list, [mock.call(self.hero.account_id, task.id)])
