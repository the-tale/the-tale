# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.cards import relations
from the_tale.game.cards import prototypes
from the_tale.game.cards import objects


class PrototypesTests(testcase.TestCase):

    def setUp(self):
        super(PrototypesTests, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')

        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.card_effect = prototypes.CARDS[relations.CARD_TYPE.KEEPERS_GOODS_COMMON]
        self.card_1 = objects.Card(relations.CARD_TYPE.KEEPERS_GOODS_COMMON)

        self.hero.cards.add_card(self.card_1)


    def test_check_hero_conditions__has_card(self):
        self.assertTrue(self.card_effect.check_hero_conditions(self.hero))


    def test_check_hero_conditions__has_no_card(self):
        self.hero.cards.remove_card(self.card_1.uid)
        self.assertFalse(self.card_effect.check_hero_conditions(self.hero))


    def test_hero_actions(self):
        self.hero.cards.add_card(objects.Card(relations.CARD_TYPE.KEEPERS_GOODS_COMMON))
        self.assertEqual(self.hero.cards.card_count(relations.CARD_TYPE.KEEPERS_GOODS_COMMON), 2)
        with self.check_delta(lambda: self.hero.statistics.cards_used, 1):
            self.card_effect.hero_actions(self.hero)
        self.assertEqual(self.hero.cards.card_count(relations.CARD_TYPE.KEEPERS_GOODS_COMMON), 1)


    def test_activate(self):
        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_logic_task') as cmd_logic_task:
            task = self.card_effect.activate(self.hero, {'x': 'y'})

        self.assertEqual(cmd_logic_task.call_args_list, [mock.call(self.hero.account_id, task.id)])
