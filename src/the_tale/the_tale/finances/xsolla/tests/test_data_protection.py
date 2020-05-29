
import smart_imports

smart_imports.all()


class CollectDataTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()

        self.accounts = [self.accounts_factory.create_account() for _ in range(3)]

        self.fabric = helpers.TestInvoiceFabric()

    def test_no_invoices__collect(self):
        report = data_protection.collect_data(self.accounts[0].id)
        self.assertCountEqual(report, [])

    def test_no_invoices__remove(self):
        data_protection.remove_data(self.accounts[0].id)

    def prepair_data(self):
        dates = [datetime.datetime(2020, 5, 17, 6, 12),
                 datetime.datetime(2020, 5, 17, 6, 13),
                 datetime.datetime(2020, 5, 17, 6, 14)]

        invoices = [self.fabric.create_invoice(account_id=self.accounts[0].id,
                                               user_email=self.accounts[0].email,
                                               xsolla_id=10001,
                                               payment_sum=1005001,
                                               date=dates[0].strftime('%Y-%m-%d %H:%M:%S')),
                    self.fabric.create_invoice(account_id=self.accounts[1].id,
                                               user_email=self.accounts[1].email,
                                               xsolla_id=10002,
                                               payment_sum=1005002,
                                               date=dates[1].strftime('%Y-%m-%d %H:%M:%S')),
                    self.fabric.create_invoice(account_id=self.accounts[0].id,
                                               user_email=self.accounts[0].email,
                                               xsolla_id=10003,
                                               payment_sum=1005003,
                                               date=dates[2].strftime('%Y-%m-%d %H:%M:%S'))]

        invoices[0]._model.comment = 'xx yy'
        invoices[0]._model.save()

        invoices[2].process()

        return invoices, dates

    def test_has_invoices__collect(self):

        invoices, dates = self.prepair_data()

        report = data_protection.collect_data(self.accounts[0].id)

        self.assertCountEqual(report,
                              [('xsolla_invoice', {'created_at': invoices[0].created_at,
                                                   'updated_at': invoices[0].updated_at,
                                                   'state': relations.INVOICE_STATE.CREATED,
                                                   'xsolla': {'id': '10001',
                                                              'v1': self.accounts[0].email,
                                                              'v2': 'bla-bla',
                                                              'v3': 'alb-alb'},
                                                   'comment': 'xx yy',
                                                   'pay_result': relations.PAY_RESULT.SUCCESS,
                                                   'date': dates[0]}),
                               ('xsolla_invoice', {'created_at': invoices[2].created_at,
                                                   'updated_at': invoices[2].updated_at,
                                                   'state': relations.INVOICE_STATE.PROCESSED,
                                                   'xsolla': {'id': '10003',
                                                              'v1': self.accounts[0].email,
                                                              'v2': 'bla-bla',
                                                              'v3': 'alb-alb'},
                                                    'comment': '',
                                                    'pay_result': relations.PAY_RESULT.SUCCESS,
                                                    'date': dates[2]})])

    def test_has_invoices__remove(self):

        invoices, dates = self.prepair_data()

        data_protection.remove_data(self.accounts[0].id, v1_filler='xxx.yyy')

        report = data_protection.collect_data(self.accounts[0].id)

        self.assertCountEqual(report,
                              [('xsolla_invoice', {'created_at': invoices[0].created_at,
                                                   'updated_at': invoices[0].updated_at,
                                                   'state': relations.INVOICE_STATE.CREATED,
                                                   'xsolla': {'id': '10001',
                                                              'v1': 'xxx.yyy',
                                                              'v2': None,
                                                              'v3': None},
                                                   'comment': '',
                                                   'pay_result': relations.PAY_RESULT.SUCCESS,
                                                   'date': dates[0]}),
                               ('xsolla_invoice', {'created_at': invoices[2].created_at,
                                                   'updated_at': invoices[2].updated_at,
                                                   'state': relations.INVOICE_STATE.PROCESSED,
                                                   'xsolla': {'id': '10003',
                                                              'v1': 'xxx.yyy',
                                                              'v2': None,
                                                              'v3': None},
                                                    'comment': '',
                                                    'pay_result': relations.PAY_RESULT.SUCCESS,
                                                    'date': dates[2]})])

        report = data_protection.collect_data(self.accounts[1].id)

        self.assertCountEqual(report,
                              [('xsolla_invoice', {'created_at': invoices[1].created_at,
                                                   'updated_at': invoices[1].updated_at,
                                                   'state': relations.INVOICE_STATE.CREATED,
                                                   'xsolla': {'id': '10002',
                                                              'v1': self.accounts[1].email,
                                                              'v2': 'bla-bla',
                                                              'v3': 'alb-alb'},
                                                   'comment': '',
                                                   'pay_result': relations.PAY_RESULT.SUCCESS,
                                                   'date': dates[1]})])
