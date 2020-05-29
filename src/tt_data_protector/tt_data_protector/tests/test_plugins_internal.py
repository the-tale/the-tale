
import uuid

from aiohttp import test_utils

from tt_web import s11n

from tt_protocol.protocol import data_protector_pb2

from .. import objects
from .. import relations
from ..plugins import internal

from . import helpers


class TestPlugin(internal.Plugin):
    __slots__ = ()

    async def request_report(self, account_id, logger):
        if account_id in ['555']:
            return None

        if account_id in ['777']:
            return data_protector_pb2.PluginReportResponse(result=data_protector_pb2.PluginReportResponse.FAILED)

        return data_protector_pb2.PluginReportResponse(result=data_protector_pb2.PluginReportResponse.SUCCESS,
                                                       data=s11n.to_json([('x', f'y-{account_id}'),
                                                                          ('a', f'b-{account_id}')]))

    async def request_deletion(self, account_id, logger):
        if account_id in ['555']:
            return None

        if account_id in ['777']:
            return data_protector_pb2.PluginDeletionResponse(result=data_protector_pb2.PluginReportResponse.FAILED)

        return data_protector_pb2.PluginDeletionResponse(result=data_protector_pb2.PluginReportResponse.SUCCESS)


def plugin():
    return TestPlugin(report_url='/debug-request-report',
                      deletion_url='/debug-request-deletion',
                      secret='some secret')


class FillSubreportTests(helpers.BaseTests):

    def subreport(self, account_id, report=None, report_id=None, state=relations.SUBREPORT_STATE.PROCESSING):

        if report_id is None:
            report_id = uuid.uuid4()

        if report is None:
            report = []

        return objects.SubReport(id=666,
                                 report_id=report_id,
                                 source='test_source_1',
                                 state=state,
                                 data={'report': report,
                                       'id': account_id})

    @test_utils.unittest_run_loop
    async def test_api_error(self):
        old_subreport = self.subreport(account_id=555)

        result = await plugin().fill_subreport(old_subreport)

        self.assertEqual(result, None)

    @test_utils.unittest_run_loop
    async def test_failed(self):
        old_subreport = self.subreport(account_id=777)

        result = await plugin().fill_subreport(old_subreport)

        self.assertEqual(result, None)

    @test_utils.unittest_run_loop
    async def test_successed(self):
        old_subreport = self.subreport(account_id=888)

        new_subreport = await plugin().fill_subreport(old_subreport)

        expected_subreport = self.subreport(account_id=888,
                                            report_id=old_subreport.report_id,
                                            state=relations.SUBREPORT_STATE.READY,
                                            report=[('test_source_1', 'x', f'y-888'),
                                                    ('test_source_1', 'a', f'b-888')])

        self.assertEqual(new_subreport, expected_subreport)


class ProcessDeletionRequestTests(helpers.BaseTests):

    def request(self, account_id):
        return objects.DeletionRequest(id=666,
                                       source='source_xxx',
                                       data={'id': account_id})

    @test_utils.unittest_run_loop
    async def test_api_error(self):
        result = await plugin().process_deletion_request(self.request(555))
        self.assertEqual(result, (False, None))

    @test_utils.unittest_run_loop
    async def test_failed(self):
        result = await plugin().process_deletion_request(self.request(777))
        self.assertEqual(result, (False, None))

    @test_utils.unittest_run_loop
    async def test_successed(self):
        result = await plugin().process_deletion_request(self.request(888))
        self.assertEqual(result, (True, None))
