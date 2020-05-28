
import uuid

from aiohttp import test_utils

from tt_web import s11n
from tt_web import utils

from tt_protocol.protocol import data_protector_pb2

from .. import logic
from .. import objects
from .. import relations
from .. import operations

from . import helpers


class RequestReportTests(helpers.BaseTests):

    async def request(self, ids):
        ids = [data_protector_pb2.SourceInfo(source=str(source), id=str(id))
               for source, id in ids]
        request = await self.client.post('/request-report',
                                         data=data_protector_pb2.RequestReportRequest(ids=ids).SerializeToString())
        return request

    @test_utils.unittest_run_loop
    async def test_no_ids(self):
        request = await self.request([])
        await self.check_error(request, error='data_protector.request_report.no_ids_specified')

    @test_utils.unittest_run_loop
    async def test_unknown_source(self):
        request = await self.request([('test_source_1', 2),
                                      ('unknowm_source', 666)])
        await self.check_error(request, error='data_protector.request_report.wrong_source_id')

    @test_utils.unittest_run_loop
    async def test_success(self):
        request = await self.request([('test_source_1', 2),
                                      ('test_source_2', 40)])
        answer = await self.check_success(request, data_protector_pb2.RequestReportResponse)

        report_id = uuid.UUID(answer.report_id)

        report = await operations.get_report(report_id)

        self.assertEqual(report, objects.Report(id=report_id,
                                                state=relations.REPORT_STATE.PROCESSING,
                                                data={'report': []},
                                                completed_at=None,
                                                expire_at=None))


class GetReportTests(helpers.BaseTests):

    async def request(self, id):
        request = await self.client.post('/get-report',
                                         data=data_protector_pb2.GetReportRequest(report_id=id.hex).SerializeToString())
        return request

    @test_utils.unittest_run_loop
    async def test_not_exists(self):
        request = await self.request(uuid.uuid4())
        answer = await self.check_success(request, data_protector_pb2.GetReportResponse)

        self.assertEqual(answer.report.state, relations.REPORT_STATE.NOT_EXISTS.value)
        self.assertEqual(s11n.from_json(answer.report.data), [])

    @test_utils.unittest_run_loop
    async def test_processing(self):
        report_id = await operations.create_report_base([("test_source_1", 2)])
        request = await self.request(report_id)

        answer = await self.check_success(request, data_protector_pb2.GetReportResponse)

        self.assertEqual(answer.report.state, relations.REPORT_STATE.PROCESSING.value)

    @test_utils.unittest_run_loop
    async def test_success(self):
        report_id = await operations.create_report_base([("test_source_1", 2),
                                                         ("test_source_2", 666)])
        await logic.process_all(helpers.get_config()['custom'])

        request = await self.request(report_id)

        answer = await self.check_success(request, data_protector_pb2.GetReportResponse)

        report = await operations.get_report(report_id)

        self.assertEqual(answer.report.state, relations.REPORT_STATE.READY.value)
        self.assertEqual(s11n.from_json(answer.report.data), [['test_source_1', 'type_3', 'data_3'],
                                                              ['test_source_2', 'xxx', 666]])

        self.assertEqual(answer.report.completed_at,
                         utils.postgres_time_to_timestamp(report.completed_at))
        self.assertEqual(answer.report.expire_at,
                         utils.postgres_time_to_timestamp(report.expire_at))


class RequestDeletionTests(helpers.BaseTests):

    async def request(self, ids):
        ids = [data_protector_pb2.SourceInfo(source=str(source), id=str(id))
               for source, id in ids]
        request = await self.client.post('/request-deletion',
                                         data=data_protector_pb2.RequestDeletionRequest(ids=ids).SerializeToString())
        return request

    @test_utils.unittest_run_loop
    async def test_no_ids(self):
        request = await self.request([])
        await self.check_error(request, error='data_protector.request_deletion.no_ids_specified')

    @test_utils.unittest_run_loop
    async def test_unknown_source(self):
        request = await self.request([('test_source_1', 2),
                                      ('unknowm_source', 666)])
        await self.check_error(request, error='data_protector.request_deletion.wrong_source_id')

    @test_utils.unittest_run_loop
    async def test_success(self):
        request = await self.request([('test_source_1', 2),
                                      ('test_source_2', 40)])
        await self.check_success(request, data_protector_pb2.RequestDeletionResponse)

        unprocessed_ids = await operations.get_unprocessed_deletion_requests()
        unprocessed_ids.sort()

        request_1 = await operations.get_deletion_request(unprocessed_ids[0])
        request_2 = await operations.get_deletion_request(unprocessed_ids[1])

        self.assertEqual(request_1, objects.DeletionRequest(id=request_1.id,
                                                            source='test_source_1',
                                                            data={'id': '2'}))
        self.assertEqual(request_2, objects.DeletionRequest(id=request_2.id,
                                                            source='test_source_2',
                                                            data={'id': '40'}))
