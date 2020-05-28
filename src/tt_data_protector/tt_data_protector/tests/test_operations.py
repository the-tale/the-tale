
import uuid
import asyncio
import datetime

from aiohttp import test_utils

from tt_web import postgresql as db

from .. import logic
from .. import objects
from .. import relations
from .. import operations

from . import helpers


class CreateReportBaseTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test(self):

        report_id = await operations.create_report_base([('test_source_1', 2),
                                                         ('test_source_2', 40)])

        results = await db.sql('SELECT * FROM reports')

        self.assertEqual(len(results), 1)

        row = results[0]

        self.assertEqual(row['id'], report_id)
        self.assertEqual(row['state'], relations.REPORT_STATE.PROCESSING.value)
        self.assertEqual(row['data'], {'report': []})
        self.assertEqual(row['completed_at'], None)
        self.assertEqual(row['expire_at'], None)

        results = await db.sql('SELECT * FROM subreports ORDER BY source')

        self.assertEqual(len(results), 2)

        row = results[0]

        self.assertEqual(row['report'], report_id)
        self.assertEqual(row['source'], 'test_source_1')
        self.assertEqual(row['state'], relations.SUBREPORT_STATE.PROCESSING.value)
        self.assertEqual(row['data'], {'report': [],
                                       'id': 2})

        row = results[1]

        self.assertEqual(row['report'], report_id)
        self.assertEqual(row['source'], 'test_source_2')
        self.assertEqual(row['state'], relations.SUBREPORT_STATE.PROCESSING.value)
        self.assertEqual(row['data'], {'report': [],
                                       'id': 40})

    @test_utils.unittest_run_loop
    async def test_multiple_reports(self):

        report_1_id = await operations.create_report_base([('test_source_1', 2),
                                                           ('test_source_2', 40)])

        report_2_id = await operations.create_report_base([('test_source_2', 2),
                                                           ('test_source_3', 500)])

        report_3_id = await operations.create_report_base([('test_source_1', 2),
                                                           ('test_source_3', 500)])

        results = await db.sql('SELECT * FROM reports ORDER BY id')

        self.assertEqual(len(results), 3)

        results = await db.sql('SELECT * FROM subreports ORDER BY created_at')

        self.assertEqual(len(results), 6)

        expected_subreports = [(report_1_id, 'test_source_1', 2),
                               (report_1_id, 'test_source_2', 40),
                               (report_2_id, 'test_source_2', 2),
                               (report_2_id, 'test_source_3', 500),
                               (report_3_id, 'test_source_1', 2),
                               (report_3_id, 'test_source_3', 500)]

        for row, (report, source, id) in zip(results, expected_subreports):
            self.assertEqual(row['report'], report)
            self.assertEqual(row['source'], source)
            self.assertEqual(row['data'], {'report': [],
                                           'id': id})


class GetUnsupportedSubreports(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_subreports(self):
        subreport_ids = await operations.get_unprocessed_subpreports()

        self.assertEqual(subreport_ids, [])

    @test_utils.unittest_run_loop
    async def test_has_subreports(self):

        report_1_id = await operations.create_report_base([('test_source_1', 1),
                                                           ('test_source_2', 3)])

        subreport_ids = await operations.get_unprocessed_subpreports()

        self.assertEqual(len(subreport_ids), 2)

        for subreport_id in subreport_ids:
            subreport = await operations.get_subreport(subreport_id)
            self.assertEqual(subreport.report_id, report_1_id)

        await logic.process_subreports(helpers.get_config()['custom'])
        await logic.form_reports(helpers.get_config()['custom'])

        report_2_id = await operations.create_report_base([('test_source_3', 1),
                                                           ('test_source_2', 5)])

        subreport_ids = await operations.get_unprocessed_subpreports()

        self.assertEqual(len(subreport_ids), 2)

        for subreport_id in subreport_ids:
            subreport = await operations.get_subreport(subreport_id)
            self.assertEqual(subreport.report_id, report_2_id)


class GetReportTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_report_exists(self):
        id = uuid.uuid4().hex

        report = await operations.get_report(id)

        self.assertEqual(report, objects.Report(id=id,
                                                state=relations.REPORT_STATE.NOT_EXISTS,
                                                data=None,
                                                completed_at=None,
                                                expire_at=None))

    @test_utils.unittest_run_loop
    async def test_report_found(self):
        report_id = await operations.create_report_base([('test_source_1', 2),
                                                         ('test_source_2', 40)])

        report = await operations.get_report(report_id)

        self.assertEqual(report, objects.Report(id=report_id,
                                                state=relations.REPORT_STATE.PROCESSING,
                                                data={'report': []},
                                                completed_at=None,
                                                expire_at=None))

    @test_utils.unittest_run_loop
    async def test_ready_report_found(self):
        report_id = await operations.create_report_base([('test_source_1', 2)])

        await logic.process_subreports(helpers.get_config()['custom'])
        await logic.form_reports(helpers.get_config()['custom'])

        report = await operations.get_report(report_id)

        self.assertNotEqual(report.completed_at, None)

        self.assertEqual(report, objects.Report(id=report_id,
                                                state=relations.REPORT_STATE.READY,
                                                data={'report': [['test_source_1', 'type_3', 'data_3']]},
                                                completed_at=report.completed_at,
                                                expire_at=report.completed_at + datetime.timedelta(seconds=helpers.report_livetime())))


class GetSubreportTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_subreport_exists(self):
        with self.assertRaises(NotImplementedError):
            await operations.get_subreport(666)

    @test_utils.unittest_run_loop
    async def test_report_found(self):
        report_id = await operations.create_report_base([('test_source_1', 2)])

        subreport_ids = await operations.get_unprocessed_subpreports()

        subreport = await operations.get_subreport(subreport_ids[0])

        self.assertEqual(subreport.id, subreport_ids[0])
        self.assertEqual(subreport.report_id, report_id)
        self.assertEqual(subreport.state, relations.SUBREPORT_STATE.PROCESSING)
        self.assertEqual(subreport.source, 'test_source_1')
        self.assertEqual(subreport.data, {'report': [],
                                          'id': 2})


class UpdateSubreportTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_subreport_exists(self):
        new_subreport = objects.SubReport(id=666,
                                          report_id=uuid.uuid4(),
                                          source='test_source_1',
                                          state=relations.SUBREPORT_STATE.READY,
                                          data={'report': [],
                                                'id': 100500})

        with self.assertRaises(NotImplementedError):
            await operations.update_subreport(new_subreport)

    @test_utils.unittest_run_loop
    async def test_success(self):
        await operations.create_report_base([('test_source_1', 2),
                                             ('test_source_2', 3)])

        subreport_ids = await operations.get_unprocessed_subpreports()

        subreport = await operations.get_subreport(subreport_ids[0])

        new_subreport = subreport.replace(state=relations.SUBREPORT_STATE.READY,
                                          data={'report': [['test_source_x', 'type_x', 'data_x']]})

        await operations.update_subreport(new_subreport)

        loaded_subreport = await operations.get_subreport(subreport_ids[0])

        self.assertEqual(new_subreport, loaded_subreport)


class GetReportsWithReadySubreportsTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_reports(self):
        reports_ids = await operations.get_reports_with_ready_subreports()

        self.assertEqual(reports_ids, [])

        await operations.create_report_base([('test_source_1', 2),
                                             ('test_source_2', 3)])

        reports_ids = await operations.get_reports_with_ready_subreports()

        self.assertEqual(reports_ids, [])

        subreport_ids = await operations.get_unprocessed_subpreports()

        subreport = await operations.get_subreport(subreport_ids[0])

        new_subreport = subreport.replace(state=relations.SUBREPORT_STATE.READY)

        await operations.update_subreport(new_subreport)

        reports_ids = await operations.get_reports_with_ready_subreports()

        self.assertEqual(reports_ids, [])

    @test_utils.unittest_run_loop
    async def test_has_reports(self):

        report_id = await operations.create_report_base([('test_source_1', 2),
                                                         ('test_source_2', 3)])

        subreport_ids = await operations.get_unprocessed_subpreports()

        for subreport_id in subreport_ids:
            subreport = await operations.get_subreport(subreport_id)
            new_subreport = subreport.replace(state=relations.SUBREPORT_STATE.READY)
            await operations.update_subreport(new_subreport)

        reports_ids = await operations.get_reports_with_ready_subreports()

        self.assertEqual(set(reports_ids), {report_id})

    @test_utils.unittest_run_loop
    async def test_has_partial_reports(self):

        report_1_id = await operations.create_report_base([('test_source_1', 2),
                                                          ('test_source_2', 3)])

        report_2_id = await operations.create_report_base([('test_source_1', 2),
                                                           ('test_source_2', 3)])

        subreport_ids = await operations.get_unprocessed_subpreports()

        for subreport_id in subreport_ids:
            subreport = await operations.get_subreport(subreport_id)

            if subreport.report_id == report_2_id and subreport.source == 'test_source_1':
                continue

            new_subreport = subreport.replace(state=relations.SUBREPORT_STATE.READY)
            await operations.update_subreport(new_subreport)

        reports_ids = await operations.get_reports_with_ready_subreports()

        self.assertEqual(set(reports_ids), {report_1_id})


class GetReportSubreportsTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_report(self):
        subreports = await operations.get_report_subreports(uuid.uuid4())
        self.assertEqual(subreports, [])

    @test_utils.unittest_run_loop
    async def test_has_subreports(self):
        report_1_id = await operations.create_report_base([('test_source_1', 2),
                                                          ('test_source_2', 3)])

        await operations.create_report_base([('test_source_1', 2),
                                             ('test_source_2', 3)])

        subreports = await operations.get_report_subreports(report_1_id)

        self.assertCountEqual([(subreport.report_id, subreport.source, subreport.data['id'])
                               for subreport in subreports],
                              [(report_1_id, 'test_source_1', 2),
                               (report_1_id, 'test_source_2', 3)])


class CompleteReportTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test(self):

        report_1_id = await operations.create_report_base([('test_source_1', 2),
                                                           ('test_source_2', 3)])

        report_2_id = await operations.create_report_base([('test_source_1', 2),
                                                           ('test_source_2', 3)])

        original_report_2 = await operations.get_report(report_2_id)

        await operations.complete_report(report_id=report_1_id,
                                         full_data=[('a', 'b', 'c'),
                                                    ('d', 'e', 'f')],
                                         livetime=60)

        subreports_1 = await operations.get_report_subreports(report_1_id)
        self.assertEqual(subreports_1, [])

        subreports_2 = await operations.get_report_subreports(report_2_id)
        self.assertEqual(len(subreports_2), 2)

        report_1 = await operations.get_report(report_1_id)

        self.assertEqual(report_1, objects.Report(id=report_1_id,
                                                  state=relations.REPORT_STATE.READY,
                                                  data={'report': [['a', 'b', 'c'],
                                                                   ['d', 'e', 'f']]},
                                                  completed_at=report_1.completed_at,
                                                  expire_at=report_1.completed_at + datetime.timedelta(seconds=60)))

        report_2 = await operations.get_report(report_2_id)

        self.assertEqual(report_2, original_report_2)


class RemoveOldReportsReportTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_reports(self):
        await operations.remove_old_reports()

    @test_utils.unittest_run_loop
    async def test_has_reports(self):

        report_1_id = await operations.create_report_base([('test_source_1', 2),
                                                           ('test_source_2', 3)])

        report_2_id = await operations.create_report_base([('test_source_1', 4),
                                                           ('test_source_2', 5)])

        report_3_id = await operations.create_report_base([('test_source_1', 6),
                                                           ('test_source_2', 7)])

        await operations.complete_report(report_id=report_1_id,
                                         full_data=[],
                                         livetime=0.1)

        await operations.complete_report(report_id=report_3_id,
                                         full_data=[],
                                         livetime=10)

        await asyncio.sleep(0.2)

        await operations.remove_old_reports()

        subreports_1 = await operations.get_report_subreports(report_1_id)
        self.assertEqual(subreports_1, [])

        subreports_2 = await operations.get_report_subreports(report_2_id)
        self.assertEqual(len(subreports_2), 2)

        subreports_3 = await operations.get_report_subreports(report_3_id)
        self.assertEqual(subreports_3, [])

        report = await operations.get_report(report_1_id)
        self.assertEqual(report.state, relations.REPORT_STATE.NOT_EXISTS)

        report = await operations.get_report(report_2_id)
        self.assertEqual(report.state, relations.REPORT_STATE.PROCESSING)

        report = await operations.get_report(report_3_id)
        self.assertEqual(report.state, relations.REPORT_STATE.READY)


class MarkForDeletionTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test(self):
        core_id = uuid.uuid4().hex

        await operations.mark_for_deletion(core_id=core_id,
                                           ids=[('test_source_1', 2),
                                                ('test_source_2', 40)])

        result = await db.sql('SELECT * FROM deletion_requests')

        self.assertCountEqual([(row['core_id'], row['source'], row['data']) for row in result],
                              [(core_id, 'test_source_1', {'id': 2}),
                               (core_id, 'test_source_2', {'id': 40})])

        result = await db.sql('SELECT * FROM deletion_history')

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['core_id'], core_id)


class GetUnprocessedDeletionRequestsTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_requests(self):
        requests_ids = await operations.get_unprocessed_deletion_requests()

        self.assertEqual(requests_ids, [])

    @test_utils.unittest_run_loop
    async def test_has_requests(self):
        core_id = uuid.uuid4().hex

        await operations.mark_for_deletion(core_id=core_id,
                                           ids=[('test_source_1', 2),
                                                ('test_source_2', 40)])

        requests_ids = await operations.get_unprocessed_deletion_requests()

        self.assertEqual(len(requests_ids), 2)


class GetDeletionRequestTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test(self):
        core_id = uuid.uuid4().hex

        await operations.mark_for_deletion(core_id=core_id,
                                           ids=[('test_source_1', 2),
                                                ('test_source_2', 40)])

        requests_ids = await operations.get_unprocessed_deletion_requests()

        requests_ids.sort()

        request_1 = await operations.get_deletion_request(requests_ids[0])
        request_2 = await operations.get_deletion_request(requests_ids[1])

        self.assertEqual(request_1, objects.DeletionRequest(id=requests_ids[0],
                                                            source='test_source_1',
                                                            data={'id': 2}))
        self.assertEqual(request_2, objects.DeletionRequest(id=requests_ids[1],
                                                            source='test_source_2',
                                                            data={'id': 40}))


class RemoveDeletionRequestTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test(self):
        core_id = uuid.uuid4().hex

        await operations.mark_for_deletion(core_id=core_id,
                                           ids=[('test_source_1', 2),
                                                ('test_source_2', 40)])

        old_requests_ids = await operations.get_unprocessed_deletion_requests()

        await operations.remove_deletion_request(old_requests_ids[0])

        new_requests_ids = await operations.get_unprocessed_deletion_requests()

        self.assertEqual(new_requests_ids, [old_requests_ids[1]])

        result = await db.sql('SELECT * FROM deletion_requests')

        self.assertEqual(len(result), 1)


class UpdateDeletionRequestTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test(self):
        core_id = uuid.uuid4().hex

        await operations.mark_for_deletion(core_id=core_id,
                                           ids=[('test_source_1', 2),
                                                ('test_source_2', 40)])

        requests_ids = await operations.get_unprocessed_deletion_requests()
        requests_ids.sort()

        old_request_1 = await operations.get_deletion_request(requests_ids[0])
        old_request_2 = await operations.get_deletion_request(requests_ids[1])

        new_request = old_request_1.replace(data={'id': old_request_1.data['id'],
                                                  'x': 'y'})

        await operations.update_deletion_request(new_request)

        requests_ids = await operations.get_unprocessed_deletion_requests()
        requests_ids.sort()

        new_request_1 = await operations.get_deletion_request(requests_ids[0])
        new_request_2 = await operations.get_deletion_request(requests_ids[1])

        self.assertEqual(new_request, new_request_1)
        self.assertEqual(old_request_2, new_request_2)
