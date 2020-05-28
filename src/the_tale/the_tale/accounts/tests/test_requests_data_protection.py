
import smart_imports

smart_imports.all()


class DataProtectionGetDataDialogTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

    def test_login_required(self):
        self.check_html_ok(self.request_ajax_html(utils_urls.url('accounts:profile:data-protection-get-data-dialog')),
                           texts=['common.login_required'])

    def test_success(self):
        self.request_login(self.account.email)

        self.check_html_ok(self.request_ajax_html(utils_urls.url('accounts:profile:data-protection-get-data-dialog')),
                           texts=[utils_urls.full_url('https', 'accounts:profile:data-protection-report', '')])


class DataProtectionReportTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

    def test_not_exists(self):
        self.check_html_ok(self.request_html(utils_urls.url('accounts:profile:data-protection-report', uuid.uuid4().hex)),
                           texts=['accounts.profile.data_protection_report.report_not_exists'])

    def test_uncompleted(self):
        report_id = tt_services.data_protector.cmd_request_report(ids=[('the_tale', self.account.id)])

        report_url = utils_urls.full_url('https', 'accounts:profile:data-protection-report', report_id.hex)

        self.check_html_ok(self.request_html(report_url),
                           texts=['accounts.profile.data_protection_report.report_processing'])

    def test_success(self):

        data = data_protection.collect_full_data(self.account.id)

        data = [('the_tale', *record) for record in data]

        report = tt_api_data_protector.Report(data=data,
                                              state=tt_api_data_protector.REPORT_STATE.READY,
                                              completed_at=datetime.datetime.now(),
                                              expire_at=datetime.datetime.now() + datetime.timedelta(days=1))

        with mock.patch('the_tale.accounts.tt_services.DataProtectorClient.cmd_get_report',
                        mock.Mock(return_value=report)):
            self.check_html_ok(self.request_html(utils_urls.url('accounts:profile:data-protection-report', uuid.uuid4().hex)),
                               texts=[self.account.nick_verbose])

    def test_success__technical(self):

        data = data_protection.collect_full_data(self.account.id)

        expected_data = [['the_tale', *record] for record in data]

        report = tt_api_data_protector.Report(data=expected_data,
                                              state=tt_api_data_protector.REPORT_STATE.READY,
                                              completed_at=datetime.datetime.now(),
                                              expire_at=datetime.datetime.now() + datetime.timedelta(days=1))

        with mock.patch('the_tale.accounts.tt_services.DataProtectorClient.cmd_get_report',
                        mock.Mock(return_value=report)):
            data = self.check_ajax_ok(self.request_json(utils_urls.url('accounts:profile:data-protection-report',
                                                                       uuid.uuid4().hex,
                                                                       mode='technical')))

        self.maxDiff = None
        self.assertEqual(data['report'], expected_data)


class DataProtectionCollectDataTests(tt_api_testcase.TestCaseMixin,
                                     utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

    def create_data(self, secret):
        return tt_protocol_data_protector_pb2.PluginReportRequest(account_id=str(self.account.id),
                                                                  secret=secret).SerializeToString()

    def test_wrong_secret_key(self):
        data = self.create_data(secret='wrong.secret')
        self.check_ajax_error(self.post_ajax_binary(utils_urls.url('accounts:profile:tt-data-protection-collect-data'), data),
                              'common.wrong_tt_secret', status_code=500)

    def test_success(self):
        data = self.create_data(secret=django_settings.TT_SECRET)

        answer = self.check_protobuf_ok(self.post_ajax_binary(utils_urls.url('accounts:profile:tt-data-protection-collect-data'), data),
                                        answer_type=tt_protocol_data_protector_pb2.PluginReportResponse)

        self.assertEqual(answer.result, tt_protocol_data_protector_pb2.PluginReportResponse.ResultType.Value('SUCCESS'))

        answer_data = s11n.from_json(answer.data)
        expected_data = [list(record) for record in data_protection.collect_full_data(self.account.id)]

        self.assertCountEqual(answer_data, expected_data)


class DataProtectionRequestDeletionTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

    def test_login_required(self):
        self.check_ajax_error(self.post_ajax_json(utils_urls.url('accounts:profile:data-protection-request-deletion')),
                              'common.login_required')

    def test_success(self):
        self.request_login(self.account.email)

        old_password = self.account._model.password

        with mock.patch('the_tale.common.tt_api.data_protector.Client.cmd_request_deletion') as cmd_request_deletion:
            self.check_ajax_ok(self.post_ajax_json(utils_urls.url('accounts:profile:data-protection-request-deletion')))

        self.assertEqual(cmd_request_deletion.call_args_list, [mock.call(ids=[('the_tale', self.account.id),
                                                                              ('tt_players_properties', self.account.id),
                                                                              ('tt_personal_messages', self.account.id),
                                                                              ('tt_discord', self.account.id)])])

        self.request_html('/')

        self.check_logged_out()

        self.account.reload()

        self.assertGreater(self.account.removed_at,
                           datetime.datetime.now() - datetime.timedelta(seconds=1))
        self.assertEqual(self.account.email, None)
        self.assertNotEqual(self.account._model.password, old_password)


class DataProtectionDeleteDataTests(tt_api_testcase.TestCaseMixin,
                                    utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

    def create_data(self, secret):
        return tt_protocol_data_protector_pb2.PluginDeletionRequest(account_id=str(self.account.id),
                                                                    secret=secret).SerializeToString()

    def test_wrong_secret_key(self):
        data = self.create_data(secret='wrong.secret')
        self.check_ajax_error(self.post_ajax_binary(utils_urls.url('accounts:profile:tt-data-protection-delete-data'), data),
                              'common.wrong_tt_secret', status_code=500)

    def test_first_call(self):
        data = self.create_data(secret=django_settings.TT_SECRET)

        with mock.patch('the_tale.game.heroes.data_protection.remove_data', mock.Mock(return_value=False)):
            with self.check_not_changed(lambda: models.Account.objects.get(id=self.account.id).email):
                url = utils_urls.url('accounts:profile:tt-data-protection-delete-data')
                answer = self.check_protobuf_ok(self.post_ajax_binary(url, data),
                                                answer_type=tt_protocol_data_protector_pb2.PluginDeletionResponse)

        self.assertEqual(answer.result, tt_protocol_data_protector_pb2.PluginDeletionResponse.ResultType.Value('FAILED'))

    def test_second_call(self):
        data = self.create_data(secret=django_settings.TT_SECRET)

        with mock.patch('the_tale.game.heroes.data_protection.remove_data', mock.Mock(return_value=True)):
            with self.check_changed(lambda: models.Account.objects.get(id=self.account.id).email):
                url = utils_urls.url('accounts:profile:tt-data-protection-delete-data')
                answer = self.check_protobuf_ok(self.post_ajax_binary(url, data),
                                                answer_type=tt_protocol_data_protector_pb2.PluginDeletionResponse)

        self.assertEqual(answer.result, tt_protocol_data_protector_pb2.PluginDeletionResponse.ResultType.Value('SUCCESS'))
