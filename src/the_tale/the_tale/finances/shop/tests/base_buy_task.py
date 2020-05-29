
import smart_imports

smart_imports.all()


class _BaseBuyPosponedTaskTests(utils_testcase.TestCase):

    CREATE_INVOICE = True

    def setUp(self):
        super(_BaseBuyPosponedTaskTests, self).setUp()

        game_logic.create_test_map()

        self.initial_amount = 500
        self.amount = 130

        self.account = self.accounts_factory.create_account()

        self.bank_account = bank_prototypes.AccountPrototype.create(entity_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                                                                    entity_id=self.account.id,
                                                                    currency=bank_relations.CURRENCY_TYPE.PREMIUM)
        self.bank_account.amount = self.initial_amount
        self.bank_account.save()

        if self.CREATE_INVOICE:
            self.invoice = bank_prototypes.InvoicePrototype.create(recipient_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                                                                   recipient_id=self.account.id,
                                                                   sender_type=bank_relations.ENTITY_TYPE.GAME_LOGIC,
                                                                   sender_id=0,
                                                                   currency=bank_relations.CURRENCY_TYPE.PREMIUM,
                                                                   amount=-self.amount,
                                                                   description_for_sender='transaction-description-for-sender',
                                                                   description_for_recipient='transaction-description-for-recipient',
                                                                   operation_uid='transaction-operation-ui')

            self.transaction = bank_transaction.Transaction(self.invoice.id)

        self.task = None
        self.storage = None
        self.cmd_update_with_account_data__call_count = 1
        self.with_referrals = True
        self.supervisor_worker = False

    def test_create(self):
        self.assertTrue(self.task.state.is_TRANSACTION_REQUESTED)
        self._test_create()

    def test_serialization(self):
        self.assertEqual(self.task.serialize(), self.task.__class__.deserialize(self.task.serialize()).serialize())

    def test_process__transaction_requested__invoice_unprocessed(self):
        self.assertEqual(self.task.process(main_task=mock.Mock()), POSTPONED_TASK_LOGIC_RESULT.WAIT)
        self.assertTrue(self.task.state.is_TRANSACTION_REQUESTED)

        self._test_process__transaction_requested__invoice_unprocessed()

        self.bank_account.reload()
        self.assertEqual(self.bank_account.amount, self.initial_amount)

    def test_process__transaction_requested__invoice_rejected(self):
        self.invoice.reload()
        self.invoice.state = bank_relations.INVOICE_STATE.REJECTED
        self.invoice.save()

        self.assertEqual(self.task.process(main_task=mock.Mock()), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertTrue(self.task.state.is_TRANSACTION_REJECTED)

        self._test_process__transaction_requested__invoice_rejected()

        self.bank_account.reload()
        self.assertEqual(self.bank_account.amount, self.initial_amount)

    def test_process__transaction_requested__invoice_wrong_state(self):
        self.invoice.reload()
        self.invoice.state = bank_relations.INVOICE_STATE.CONFIRMED
        self.invoice.save()

        self.assertEqual(self.task.process(main_task=mock.Mock()), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertTrue(self.task.state.is_ERROR_IN_FREEZING_TRANSACTION)

        self._test_process__transaction_requested__invoice_wrong_state()

        self.bank_account.reload()
        self.assertEqual(self.bank_account.amount, self.initial_amount)

    def test_process__transaction_requested__invoice_frozen(self):
        self.invoice.reload()
        self.invoice.state = bank_relations.INVOICE_STATE.FROZEN
        self.invoice.save()

        main_task = mock.Mock()

        self.assertEqual(self.task.process(main_task=main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)
        self.assertTrue(self.task.state.is_TRANSACTION_FROZEN)

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_logic_task') as cmd_logic_task:
            postsave_actions = main_task.extend_postsave_actions.call_args[0][0]

        self.assertEqual(postsave_actions, (main_task.cmd_wait, ))

        if self.supervisor_worker:
            self.assertEqual(cmd_logic_task.call_count, 1)

        self._test_process__transaction_requested__invoice_frozen()

        self.bank_account.reload()
        self.assertEqual(self.bank_account.amount, self.initial_amount)

    def test_process__transaction_frozen(self):
        self.invoice.reload()
        self.invoice.state = bank_relations.INVOICE_STATE.FROZEN
        self.invoice.save()

        self.task.state = self.task.RELATION.TRANSACTION_FROZEN

        with mock.patch('the_tale.accounts.prototypes.AccountPrototype.cmd_update_hero') as cmd_update_hero:
            with mock.patch('the_tale.finances.bank.transaction.Transaction.confirm') as transaction_confirm:
                self.assertEqual(self.task.process(main_task=mock.Mock(), storage=self.storage), POSTPONED_TASK_LOGIC_RESULT.WAIT)

        self.assertEqual(cmd_update_hero.call_count, self.cmd_update_with_account_data__call_count)
        self.assertEqual(transaction_confirm.call_count, 1)

        self._test_process__transaction_frozen()

        self.bank_account.reload()
        self.assertEqual(self.bank_account.amount, self.initial_amount)  # money will be withdrawed after transaction confirm processed

    def test_process__wait_confirmation__transaction_frozen(self):
        self.invoice.reload()
        self.invoice.state = bank_relations.INVOICE_STATE.FROZEN
        self.invoice.save()

        self.task.state = self.task.RELATION.WAIT_TRANSACTION_CONFIRMATION

        self.assertEqual(self.task.process(main_task=mock.Mock()), POSTPONED_TASK_LOGIC_RESULT.WAIT)
        self.assertTrue(self.task.state.is_WAIT_TRANSACTION_CONFIRMATION)

    def test_process__wait_confirmation__transaction_confirmed(self):
        self.invoice.reload()
        self.invoice.state = bank_relations.INVOICE_STATE.CONFIRMED
        self.invoice.save()

        self.task.state = self.task.RELATION.WAIT_TRANSACTION_CONFIRMATION

        with mock.patch('the_tale.finances.shop.postponed_tasks.BaseBuyTask.process_referrals') as process_referrals:
            self.assertEqual(self.task.process(main_task=mock.Mock()), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertEqual(process_referrals.call_count, 1 if self.with_referrals else 0)

        self.assertTrue(self.task.state.is_SUCCESSED)

    def test_process__wait_confirmation__transaction_confirmed__with_referal(self):
        self.invoice.reload()
        self.invoice.state = bank_relations.INVOICE_STATE.CONFIRMED
        self.invoice.save()

        account_2 = self.accounts_factory.create_account()

        self.account._model.referral_of_id = account_2.id
        self.account.save()

        self.task.state = self.task.RELATION.WAIT_TRANSACTION_CONFIRMATION

        self.assertEqual(self.task.process(main_task=mock.Mock()), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertEqual(bank_prototypes.InvoicePrototype._db_count(), (2 if self.with_referrals else 1))

        if self.with_referrals:
            referral_invoice = bank_prototypes.InvoicePrototype._db_get_object(1)

            self.assertTrue(referral_invoice.amount > 0)
            self.assertTrue(referral_invoice.amount < self.amount)
            self.assertEqual(referral_invoice.recipient_id, account_2.id)
            self.assertTrue(referral_invoice.state.is_FORCED)

        self.assertTrue(self.task.state.is_SUCCESSED)

    def test_process__wait_confirmation__transaction_in_wrong_state(self):
        self.invoice.reload()
        self.invoice.state = bank_relations.INVOICE_STATE.REJECTED
        self.invoice.save()

        self.task.state = self.task.RELATION.WAIT_TRANSACTION_CONFIRMATION

        self.assertEqual(self.task.process(main_task=mock.Mock()), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertTrue(self.task.state.is_ERROR_IN_CONFIRM_TRANSACTION)

    def test_process__wrong_state(self):
        self.task.state = self.task.RELATION.ERROR_IN_FREEZING_TRANSACTION

        self.assertEqual(self.task.process(main_task=mock.Mock()), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertTrue(self.task.state.is_WRONG_TASK_STATE)

        self._test_process__wrong_state()

        self.bank_account.reload()
        self.assertEqual(self.bank_account.amount, self.initial_amount)
