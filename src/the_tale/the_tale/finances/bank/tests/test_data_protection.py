
import smart_imports

smart_imports.all()


class CollectDataTests(helpers.BankTestsMixin,
                       utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()

        self.accounts = [self.accounts_factory.create_account() for _ in range(3)]

        self.target_account_id = self.accounts[0].id
        self.other_account_1_id = self.accounts[1].id
        self.other_account_2_id = self.accounts[2].id

    def create_invoice(self, uid, **kwargs):
        return super().create_invoice(description_for_sender=f'ds-{uid}',
                                      description_for_recipient=f'dr-{uid}',
                                      operation_uid=f'op-{uid}',
                                      amount=10000 + uid,
                                      **kwargs)

    def test_no_invoices__collect(self):
        report = data_protection.collect_data(self.other_account_2_id)
        self.assertCountEqual(report, [])

    def test_no_invoices__remove(self):
        data_protection.remove_data(self.other_account_2_id)

    def prepair_data(self):
        invoices = [self.create_invoice(1,
                                        recipient_type=relations.ENTITY_TYPE.GAME_ACCOUNT,
                                        recipient_id=self.target_account_id,
                                        sender_type=relations.ENTITY_TYPE.GAME_LOGIC,
                                        sender_id=self.other_account_1_id),
                    self.create_invoice(2,
                                        recipient_type=relations.ENTITY_TYPE.GAME_LOGIC,
                                        recipient_id=self.target_account_id,
                                        sender_type=relations.ENTITY_TYPE.GAME_ACCOUNT,
                                        sender_id=self.other_account_1_id),

                    self.create_invoice(3,
                                        recipient_type=relations.ENTITY_TYPE.GAME_ACCOUNT,
                                        recipient_id=self.target_account_id,
                                        sender_type=relations.ENTITY_TYPE.GAME_ACCOUNT,
                                        sender_id=self.other_account_1_id,
                                        state=relations.INVOICE_STATE.random()),
                    self.create_invoice(4,
                                        recipient_type=relations.ENTITY_TYPE.GAME_LOGIC,
                                        recipient_id=self.other_account_1_id,
                                        sender_type=relations.ENTITY_TYPE.GAME_ACCOUNT,
                                        sender_id=self.target_account_id),

                    self.create_invoice(5,
                                        recipient_type=relations.ENTITY_TYPE.GAME_ACCOUNT,
                                        recipient_id=self.other_account_2_id,
                                        sender_type=relations.ENTITY_TYPE.GAME_LOGIC,
                                        sender_id=self.other_account_1_id)]

        return invoices

    def expected_data(self, invoices):
        return [('game_invoice', {'amount': 10001,
                                  'created_at': invoices[0].created_at,
                                  'currency': relations.CURRENCY_TYPE.PREMIUM,
                                  'description_for_recipient': 'dr-1',
                                  'description_for_sender': 'ds-1',
                                  'recipient_id': self.target_account_id,
                                  'recipient_type': relations.ENTITY_TYPE.GAME_ACCOUNT,
                                  'sender_id': self.other_account_1_id,
                                  'sender_type': relations.ENTITY_TYPE.GAME_LOGIC,
                                  'state': relations.INVOICE_STATE.REQUESTED,
                                  'updated_at': invoices[0].updated_at}),
                ('game_invoice', {'amount': 10003,
                                  'created_at': invoices[2].created_at,
                                  'currency': relations.CURRENCY_TYPE.PREMIUM,
                                  'description_for_recipient': 'dr-3',
                                  'description_for_sender': 'ds-3',
                                  'recipient_id': self.target_account_id,
                                  'recipient_type': relations.ENTITY_TYPE.GAME_ACCOUNT,
                                  'sender_id': self.other_account_1_id,
                                  'sender_type': relations.ENTITY_TYPE.GAME_ACCOUNT,
                                  'state': invoices[2].state,
                                  'updated_at': invoices[2].updated_at}),
                ('game_invoice', {'amount': 10004,
                                  'created_at': invoices[3].created_at,
                                  'currency': relations.CURRENCY_TYPE.PREMIUM,
                                  'description_for_recipient': 'dr-4',
                                  'description_for_sender': 'ds-4',
                                  'recipient_id': self.other_account_1_id,
                                  'recipient_type': relations.ENTITY_TYPE.GAME_LOGIC,
                                  'sender_id': self.target_account_id,
                                  'sender_type': relations.ENTITY_TYPE.GAME_ACCOUNT,
                                  'state': relations.INVOICE_STATE.REQUESTED,
                                  'updated_at': invoices[3].updated_at})]

    def test_has_invoices__collect(self):
        invoices = self.prepair_data()

        report = data_protection.collect_data(self.target_account_id)

        self.assertCountEqual(report, self.expected_data(invoices))

    def test_has_invoices__remove(self):
        invoices = self.prepair_data()

        data_protection.remove_data(self.target_account_id)

        report = data_protection.collect_data(self.target_account_id)

        self.assertCountEqual(report, self.expected_data(invoices))
