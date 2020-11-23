

import smart_imports

smart_imports.all()


class PaymentCallbackTests(utils_testcase.TestCase, tt_api_testcase.TestCaseMixin):

    def setUp(self):
        super().setUp()

        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account.id)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

    def create_data(self, secret=None, account_id=None, amount=666):

        if secret is None:
            secret = django_settings.TT_SECRET

        if account_id is None:
            account_id = self.account.id

        return tt_protocol_xsolla_pb2.PaymentCallbackBody(account_id=account_id,
                                                          amount=amount,
                                                          secret=secret).SerializeToString()

    @contextlib.contextmanager
    def check_amount_changed(self, account_id, delta):
        with self.check_delta(bank_prototypes.InvoicePrototype._db_count, 1):
            with self.check_delta(lambda: accounts_prototypes.AccountPrototype.get_by_id(account_id).bank_account.amount, delta):
                yield

                bank_invoice = bank_prototypes.InvoicePrototype._db_get_object(0)
                bank_invoice.confirm()

    @contextlib.contextmanager
    def check_amount_not_changed(self, account_id):
        with self.check_not_changed(bank_prototypes.InvoicePrototype._db_count):
            with self.check_not_changed(lambda: accounts_prototypes.AccountPrototype.get_by_id(account_id).bank_account.amount):
                yield

    def test_no_post_data(self):
        with self.check_amount_not_changed(self.account.id):
            self.check_ajax_error(self.post_protobuf(utils_urls.url('bank:tt-process-payment')),
                                  'common.wrong_tt_secret',
                                  status_code=500)

    def test_wrong_secret_key(self):
        data = self.create_data(secret='wrong.secret')

        with self.check_amount_not_changed(self.account.id):
            self.check_ajax_error(self.post_protobuf(utils_urls.url('bank:tt-process-payment'), data),
                                  'common.wrong_tt_secret',
                                  status_code=500)

    @mock.patch('tt_logic.common.checkers.is_player_participate_in_game', mock.Mock(return_value=False))
    def test_no_account(self):
        data = self.create_data(account_id=9999999)

        with self.check_amount_not_changed(self.account.id):
            self.check_ajax_error(self.post_protobuf(utils_urls.url('bank:tt-process-payment'), data),
                                  'bank.take_card_callback.account_not_found',
                                  status_code=200)

    def test_success(self):
        data = self.create_data()

        with self.check_amount_changed(self.account.id, 666):
            self.check_protobuf_ok(self.post_protobuf(utils_urls.url('bank:tt-process-payment'), data),
                                   answer_type=tt_protocol_xsolla_pb2.PaymentCallbackAnswer)
