
import smart_imports

smart_imports.all()


data_protector_client = accounts_tt_services.data_protector


class TTAPiTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()
        data_protector_client.cmd_debug_clear_service()

        self.account = self.accounts_factory.create_account()

    def test_request_report(self):

        report_id = data_protector_client.cmd_request_report(ids=[('the_tale', self.account.id),
                                                                  ('tt_personal_messages', self.account.id),
                                                                  ('tt_discord', self.account.id)])

        self.assertTrue(isinstance(report_id, uuid.UUID))

    def test_get_report__no_report(self):

        report = data_protector_client.cmd_get_report(id=uuid.uuid4())

        self.assertEqual(report, data_protector.Report(data=[],
                                                       state=data_protector.REPORT_STATE.NOT_EXISTS,
                                                       completed_at=datetime.datetime(1970, 1, 1, 0, 0),
                                                       expire_at=datetime.datetime(1970, 1, 1, 0, 0)))

    def test_get_report__report_not_ready(self):

        report_id = data_protector_client.cmd_request_report(ids=[('the_tale', self.account.id),
                                                                  ('tt_personal_messages', self.account.id),
                                                                  ('tt_discord', self.account.id)])

        report = data_protector_client.cmd_get_report(id=report_id)

        self.assertEqual(report, data_protector.Report(data=[],
                                                       state=data_protector.REPORT_STATE.PROCESSING,
                                                       completed_at=datetime.datetime(1970, 1, 1, 0, 0),
                                                       expire_at=datetime.datetime(1970, 1, 1, 0, 0)))

    def test_get_report__report_ready(self):
        completed_at = datetime.datetime.now()
        expire_at = completed_at + datetime.timedelta(days=30)
        state = data_protector.REPORT_STATE.READY.value

        data = accounts_data_protection.collect_full_data(self.account.id)
        data = [['the_tale', *record] for record in data]

        report = tt_protocol_data_protector_pb2.Report(data=s11n.to_json(data),
                                                       state=state,
                                                       completed_at=utils_logic.to_timestamp(completed_at),
                                                       expire_at=utils_logic.to_timestamp(expire_at))

        answer = tt_protocol_data_protector_pb2.GetReportResponse(report=report)

        with mock.patch('the_tale.common.tt_api.operations.sync_request', mock.Mock(return_value=answer)):
            report = data_protector_client.cmd_get_report(id=uuid.uuid4())

        self.assertEqual(report, data_protector.Report(data=data,
                                                       state=data_protector.REPORT_STATE.READY,
                                                       completed_at=completed_at,
                                                       expire_at=expire_at))
