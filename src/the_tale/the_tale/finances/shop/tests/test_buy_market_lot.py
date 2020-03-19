
import smart_imports

smart_imports.all()


class BuyMarketLotPosponedTaskTests(base_buy_task._BaseBuyPosponedTaskTests, personal_messages_helpers.Mixin):
    CREATE_INVOICE = False

    def setUp(self):
        super(BuyMarketLotPosponedTaskTests, self).setUp()

        self.seller_account = self.accounts_factory.create_account()

        tt_services.market.cmd_debug_clear_service()
        cards_tt_services.storage.cmd_debug_clear_service()

        self.card = cards_types.CARD.CANCEL_QUEST.effect.create_card(available_for_auction=True, type=cards_types.CARD.CANCEL_QUEST)

        cards_logic.change_cards(accounts_logic.get_system_user_id(), operation_type='#test', to_add=[self.card])

        self.lot = objects.Lot(owner_id=self.seller_account.id,
                               full_type=self.card.item_full_type,
                               item_id=self.card.uid,
                               price=self.amount)

        tt_services.market.cmd_place_sell_lots([self.lot])

        self.task = logic.close_lot(item_type=self.lot.full_type,
                                    price=self.amount,
                                    buyer_id=self.account.id)
        self.invoice = bank_prototypes.InvoicePrototype.get_by_id(self.task.transaction.invoice_id)

        self.market_basic_information = tt_services.market.cmd_info()

        self.cmd_update_with_account_data__call_count = 0  # no need in updating hero state
        self.with_referrals = False  # no money for referrals

        personal_messages_tt_services.personal_messages.cmd_debug_clear_service()

    def _test_create(self):
        self.assertEqual(self.task.item_type, self.lot.full_type)
        self.assertEqual(self.task.price, self.amount)

    def _test_process__transaction_requested__invoice_unprocessed(self):
        self.assertEqual(self.market_basic_information, tt_services.market.cmd_info())
        self.assertNotIn(self.card.uid, cards_tt_services.storage.cmd_get_items(self.account.id))
        self.assertNotIn(self.card.uid, cards_tt_services.storage.cmd_get_items(self.seller_account.id))

    def _test_process__transaction_requested__invoice_rejected(self):
        self.assertEqual(self.market_basic_information, tt_services.market.cmd_info())
        self.assertNotIn(self.card.uid, cards_tt_services.storage.cmd_get_items(self.account.id))
        self.assertNotIn(self.card.uid, cards_tt_services.storage.cmd_get_items(self.seller_account.id))

    def _test_process__transaction_requested__invoice_wrong_state(self):
        self.assertEqual(self.market_basic_information, tt_services.market.cmd_info())
        self.assertNotIn(self.card.uid, cards_tt_services.storage.cmd_get_items(self.account.id))
        self.assertNotIn(self.card.uid, cards_tt_services.storage.cmd_get_items(self.seller_account.id))

    def _test_process__transaction_requested__invoice_frozen(self):
        self.assertEqual(self.market_basic_information, tt_services.market.cmd_info())
        self.assertNotIn(self.card.uid, cards_tt_services.storage.cmd_get_items(self.account.id))
        self.assertNotIn(self.card.uid, cards_tt_services.storage.cmd_get_items(self.seller_account.id))

    def _test_process__transaction_frozen(self):
        self.assertEqual([], tt_services.market.cmd_info())
        self.assertIn(self.card.uid, cards_tt_services.storage.cmd_get_items(self.account.id))
        self.assertNotIn(self.card.uid, cards_tt_services.storage.cmd_get_items(self.seller_account.id))

        buy_invoice = bank_prototypes.InvoicePrototype._db_get_object(0)

        self.assertEqual(buy_invoice.amount, self.amount)
        self.assertEqual(buy_invoice.recipient_type, bank_relations.ENTITY_TYPE.GAME_ACCOUNT)
        self.assertEqual(buy_invoice.recipient_id, self.seller_account.id)
        self.assertEqual(buy_invoice.sender_type, bank_relations.ENTITY_TYPE.GAME_ACCOUNT)
        self.assertEqual(buy_invoice.sender_id, self.account.id)

        comission_invoice = bank_prototypes.InvoicePrototype._db_get_object(1)

        self.assertEqual(comission_invoice.amount, -logic.get_commission(self.amount))
        self.assertEqual(comission_invoice.recipient_type, bank_relations.ENTITY_TYPE.GAME_ACCOUNT)
        self.assertEqual(comission_invoice.recipient_id, self.seller_account.id)
        self.assertEqual(comission_invoice.sender_type, bank_relations.ENTITY_TYPE.GAME_LOGIC)
        self.assertEqual(comission_invoice.sender_id, 0)

        self.assertEqual(personal_messages_tt_services.personal_messages.cmd_new_messages_number(self.lot.owner_id), 1)

    def _test_process__wrong_state(self):
        self.assertNotIn(self.card.uid, cards_tt_services.storage.cmd_get_items(self.account.id))
        self.assertNotIn(self.card.uid, cards_tt_services.storage.cmd_get_items(self.seller_account.id))

    def test_process__transaction_frozen__no_lots(self):
        self.invoice.reload()
        self.invoice.state = bank_relations.INVOICE_STATE.FROZEN
        self.invoice.save()

        self.task.state = self.task.RELATION.TRANSACTION_FROZEN

        tt_services.market.cmd_close_lot(item_type=self.lot.full_type,
                                         price=self.lot.price,
                                         buyer_id=777)

        self.assertEqual([], tt_services.market.cmd_info())
        self.assertNotIn(self.card.uid, cards_tt_services.storage.cmd_get_items(self.account.id))
        self.assertNotIn(self.card.uid, cards_tt_services.storage.cmd_get_items(self.seller_account.id))

        with self.check_no_messages(recipient_id=self.lot.owner_id):
            with mock.patch('the_tale.accounts.prototypes.AccountPrototype.cmd_update_hero') as cmd_update_hero:
                with mock.patch('the_tale.finances.bank.transaction.Transaction.cancel') as transaction_cancel:
                    self.assertEqual(self.task.process(main_task=mock.Mock(), storage=self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)

        self.assertEqual(cmd_update_hero.call_count, self.cmd_update_with_account_data__call_count)
        self.assertEqual(transaction_cancel.call_count, 1)

        self.assertEqual(bank_prototypes.InvoicePrototype._db_count(), 1)

        self.assertEqual(self.task.error_message, 'Не удалось купить карту: только что её купил другой игрок.')
        self.assertTrue(self.task.state.is_CANCELED)

        self.bank_account.reload()
        self.assertEqual(self.bank_account.amount, self.initial_amount)
