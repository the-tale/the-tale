
import smart_imports

smart_imports.all()


class CollectDataTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()

        self.accounts = [self.accounts_factory.create_account(),
                         self.accounts_factory.create_account(),
                         self.accounts_factory.create_account()]

        self.tokens = [prototypes.AccessTokenPrototype.fast_create(1),
                       prototypes.AccessTokenPrototype.fast_create(2, self.accounts[0], state=relations.ACCESS_TOKEN_STATE.ACCEPTED),
                       prototypes.AccessTokenPrototype.fast_create(3, self.accounts[1], state=relations.ACCESS_TOKEN_STATE.ACCEPTED),
                       prototypes.AccessTokenPrototype.fast_create(4, self.accounts[0], state=relations.ACCESS_TOKEN_STATE.ACCEPTED),]

    def test_no_tokens__collect(self):
        report = data_protection.collect_data(self.accounts[2].id)
        self.assertCountEqual(report, [])

    def test_no_tokens__remove(self):
        data_protection.remove_data(self.accounts[2].id)

    def test_has_tokens__collect(self):
        report = data_protection.collect_data(self.accounts[0].id)

        self.assertCountEqual(report, [('third_party_token', {'created_at': self.tokens[1].created_at,
                                                              'updated_at': self.tokens[1].updated_at,
                                                              'uid': self.tokens[1].uid,
                                                              'application_name': 'app-name-2',
                                                              'application_info': 'app-info-2',
                                                              'application_description': 'app-descr-2',
                                                              'state': relations.ACCESS_TOKEN_STATE.ACCEPTED}),
                                       ('third_party_token', {'created_at': self.tokens[3].created_at,
                                                              'updated_at': self.tokens[3].updated_at,
                                                              'uid': self.tokens[3].uid,
                                                              'application_name': 'app-name-4',
                                                              'application_info': 'app-info-4',
                                                              'application_description': 'app-descr-4',
                                                              'state': relations.ACCESS_TOKEN_STATE.ACCEPTED})])

    def test_has_tokens__remove(self):
        data_protection.remove_data(self.accounts[0].id)

        report = data_protection.collect_data(self.accounts[0].id)

        self.assertCountEqual(report, [])

        report = data_protection.collect_data(self.accounts[1].id)

        self.assertCountEqual(report, [('third_party_token', {'created_at': self.tokens[2].created_at,
                                                              'updated_at': self.tokens[2].updated_at,
                                                              'uid': self.tokens[2].uid,
                                                              'application_name': 'app-name-3',
                                                              'application_info': 'app-info-3',
                                                              'application_description': 'app-descr-3',
                                                              'state': relations.ACCESS_TOKEN_STATE.ACCEPTED})])
