
import smart_imports

smart_imports.all()


class RemoveDataTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        tt_services.market.cmd_debug_clear_service()
        cards_tt_services.storage.cmd_debug_clear_service()

        self.cards = [cards_types.CARD.CANCEL_QUEST.effect.create_card(available_for_auction=True,
                                                                       type=cards_types.CARD.CANCEL_QUEST),

                      cards_types.CARD.CANCEL_QUEST.effect.create_card(available_for_auction=True,
                                                                       type=cards_types.CARD.CANCEL_QUEST),

                      cards_types.CARD.ADD_GOLD_COMMON.effect.create_card(available_for_auction=True,
                                                                          type=cards_types.CARD.ADD_GOLD_COMMON)]

        cards_logic.change_cards(self.account_1.id, operation_type='#test', to_add=[self.cards[0], self.cards[2]])
        cards_logic.change_cards(self.account_2.id, operation_type='#test', to_add=[self.cards[1]])

        logic.create_lots(owner_id=self.account_1.id,
                          cards=[self.cards[0]],
                          price=random.randint(100, 1000))
        logic.create_lots(owner_id=self.account_1.id,
                          cards=[self.cards[2]],
                          price=random.randint(100, 1000))

        logic.create_lots(owner_id=self.account_2.id,
                          cards=[self.cards[1]],
                          price=100)

    def test_remove(self):

        cards = cards_tt_services.storage.cmd_get_items(self.account_1.id)
        self.assertEqual(cards, {})

        cards = cards_tt_services.storage.cmd_get_items(self.account_2.id)
        self.assertEqual(cards, {})

        data_protection.remove_data(self.account_1.id)

        cards = cards_tt_services.storage.cmd_get_items(self.account_1.id)
        self.assertCountEqual(list(cards.values()), [self.cards[0], self.cards[2]])

        cards = cards_tt_services.storage.cmd_get_items(self.account_2.id)
        self.assertEqual(list(cards.values()), [])

        data_protection.remove_data(self.account_2.id)

        cards = cards_tt_services.storage.cmd_get_items(self.account_1.id)
        self.assertCountEqual(list(cards.values()), [self.cards[0], self.cards[2]])

        cards = cards_tt_services.storage.cmd_get_items(self.account_2.id)
        self.assertEqual(list(cards.values()), [self.cards[1]])
