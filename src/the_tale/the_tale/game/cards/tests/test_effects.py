
import smart_imports

smart_imports.all()


class EffectsTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account.id)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        tt_services.storage.cmd_debug_clear_service()

        self.card = objects.Card(types.CARD.KEEPERS_GOODS_COMMON, uid=uuid.uuid4())

        logic.change_cards(owner_id=self.hero.account_id, operation_type='#test', to_add=[self.card])

        self.task_data = {'card': {'id': self.card.uid.hex,
                                   'data': self.card.serialize()}}

    def test_check_hero_conditions__has_card(self):
        self.assertTrue(self.card.effect.check_hero_conditions(self.hero, self.task_data))

    def test_check_hero_conditions__has_no_card(self):
        logic.change_cards(owner_id=self.hero.account_id, operation_type='#test', to_remove=[self.card])
        self.assertFalse(self.card.effect.check_hero_conditions(self.hero, self.task_data))

    def test_hero_actions(self):
        card_2 = objects.Card(types.CARD.KEEPERS_GOODS_COMMON, uid=uuid.uuid4())

        logic.change_cards(owner_id=self.hero.account_id, operation_type='#test', to_add=[card_2])

        self.assertEqual(self.card.type, card_2.type)

        account_cards = tt_services.storage.cmd_get_items(self.hero.account_id)
        self.assertEqual(len(account_cards), 2)

        with self.check_delta(lambda: self.hero.statistics.cards_used, 1):
            self.card.effect.hero_actions(self.hero, self.task_data)

        account_cards = tt_services.storage.cmd_get_items(self.hero.account_id)
        self.assertEqual(len(account_cards), 1)

        self.assertIn(card_2.uid, account_cards)
        self.assertNotIn(self.card.uid, account_cards)

    def test_activate(self):
        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_logic_task') as cmd_logic_task:
            task = self.card.effect.activate(self.hero, self.card, {'x': 'y'})

        self.assertEqual(cmd_logic_task.call_args_list, [mock.call(self.hero.account_id, task.id)])
