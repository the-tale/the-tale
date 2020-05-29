
import uuid

from aiohttp import test_utils

from tt_web import postgresql as db

from .. import logic
from .. import relations
from .. import operations
from .. import exceptions

from . import helpers


class GetPluginForSourceTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test(self):
        plugin_1 = await logic.get_pluging_for_source(helpers.get_config()['custom'],
                                                      'test_source_1')

        plugin_2 = await logic.get_pluging_for_source(helpers.get_config()['custom'],
                                                      'test_source_3')

        new_plugin_1 = await logic.get_pluging_for_source(helpers.get_config()['custom'],
                                                         'test_source_1')

        self.assertIs(plugin_1, new_plugin_1)
        self.assertIsNot(plugin_1, plugin_2)

    @test_utils.unittest_run_loop
    async def test_error(self):
        with self.assertRaises(exceptions.CanNotConstructPlugin):
            await logic.get_pluging_for_source(helpers.get_config()['custom'],
                                               'unknowm_source')


class ProcessSubreportTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_already_processed(self):
        await operations.create_report_base([("test_source_1", 2)])
        subreport_ids = await operations.get_unprocessed_subpreports()
        subreport = await operations.get_subreport(subreport_ids[0])

        subreport = subreport.replace(state=relations.SUBREPORT_STATE.READY)

        await operations.update_subreport(subreport)

        async with self.check_db_record_not_changed('subreports', subreport.id):
            await logic.process_subreport(helpers.get_config()['custom'], subreport.id)

    @test_utils.unittest_run_loop
    async def test_processing_failed__no_plugin(self):
        await operations.create_report_base([("unknowm_source", 2)])
        subreport_ids = await operations.get_unprocessed_subpreports()
        subreport = await operations.get_subreport(subreport_ids[0])

        with self.assertRaises(exceptions.CanNotConstructPlugin):
            async with self.check_db_record_not_changed('subreports', subreport.id):
                await logic.process_subreport(helpers.get_config()['custom'], subreport.id)

    @test_utils.unittest_run_loop
    async def test_processing_failed__plugin_work_failed(self):
        await operations.create_report_base([("test_source_2", 20)])
        subreport_ids = await operations.get_unprocessed_subpreports()
        subreport = await operations.get_subreport(subreport_ids[0])

        async with self.check_db_record_not_changed('subreports', subreport.id):
            await logic.process_subreport(helpers.get_config()['custom'], subreport.id)

        await logic.process_subreport(helpers.get_config()['custom'], subreport.id)

        new_subreport = await operations.get_subreport(subreport.id)

        self.assertEqual(new_subreport.state, relations.SUBREPORT_STATE.READY)
        self.assertEqual(new_subreport.data,
                         {'id': 20,
                          'report': [['test_source_2', 'type_3', 'data_5'],
                                     ['test_source_2', 'type_3', 'data_6']]})

    @test_utils.unittest_run_loop
    async def test_has_changes(self):
        await operations.create_report_base([("test_source_1", 2)])
        subreport_ids = await operations.get_unprocessed_subpreports()
        subreport = await operations.get_subreport(subreport_ids[0])

        await logic.process_subreport(helpers.get_config()['custom'], subreport.id)

        new_subreport = await operations.get_subreport(subreport.id)

        self.assertEqual(new_subreport.state, relations.SUBREPORT_STATE.READY)
        self.assertEqual(new_subreport.data,
                         {'id': 2,
                          'report': [['test_source_1', 'type_3', 'data_3']]})


class ProcessSubreportsTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test(self):
        report_1_id = await operations.create_report_base([("test_source_1", 2),
                                                           ("test_source_2", 20),
                                                           ("test_source_2", 40)])
        report_2_id = await operations.create_report_base([("test_source_1", 3),
                                                           ("test_source_2", 20)])

        await logic.process_subreports(helpers.get_config()['custom'])

        result = await db.sql('SELECT * FROM subreports WHERE state=%(state)s',
                              {'state': relations.SUBREPORT_STATE.READY.value})

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['report'], report_1_id)

        await logic.process_subreports(helpers.get_config()['custom'])

        result = await db.sql('SELECT * FROM subreports WHERE state=%(state)s ORDER BY id',
                              {'state': relations.SUBREPORT_STATE.READY.value})

        self.assertEqual(len(result), 4)
        self.assertTrue(all(row['report'] == report_1_id for row in result[:2]))
        self.assertTrue(all(row['report'] == report_2_id for row in result[2:]))

        await logic.process_subreports(helpers.get_config()['custom'])

        result = await db.sql('SELECT * FROM subreports WHERE state=%(state)s ORDER BY ID',
                              {'state': relations.SUBREPORT_STATE.READY.value})

        self.assertEqual(len(result), 5)


class FormReportTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test(self):
        report_1_id = await operations.create_report_base([("test_source_1", 1)])
        report_2_id = await operations.create_report_base([("test_source_1", 333)])

        await logic.process_subreports(helpers.get_config()['custom'])

        await logic.form_report(helpers.get_config()['custom'], report_2_id)

        report_1 = await operations.get_report(report_1_id)
        self.assertEqual(report_1.state, relations.REPORT_STATE.PROCESSING)
        self.assertEqual(report_1.data, {'report': []})

        report_2 = await operations.get_report(report_2_id)
        self.assertEqual(report_2.state, relations.REPORT_STATE.READY)
        self.assertEqual(report_2.data, {'report': [['test_source_1', 'xxx', 333]]})

        result = await db.sql('SELECT * FROM subreports WHERE state=%(state)s',
                              {'state': relations.SUBREPORT_STATE.READY.value})

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['report'], report_1_id)


class FormReportsTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test(self):
        report_1_id = await operations.create_report_base([("test_source_1", 1)])
        report_2_id = await operations.create_report_base([("test_source_1", 333)])

        await logic.process_subreports(helpers.get_config()['custom'])

        await logic.form_reports(helpers.get_config()['custom'])

        report_1 = await operations.get_report(report_1_id)
        self.assertEqual(report_1.state, relations.REPORT_STATE.READY)
        self.assertEqual(report_1.data, {'report': [['test_source_1', 'type_1', 'data_1'],
                                                    ['test_source_1', 'type_2', 'data_2']]})

        report_2 = await operations.get_report(report_2_id)
        self.assertEqual(report_2.state, relations.REPORT_STATE.READY)
        self.assertEqual(report_2.data, {'report': [['test_source_1', 'xxx', 333]]})

        result = await db.sql('SELECT * FROM subreports WHERE state=%(state)s',
                              {'state': relations.SUBREPORT_STATE.READY.value})

        self.assertEqual(len(result), 0)


class MergeReportTests(helpers.BaseTests):

    def test_no_reports(self):
        self.assertEqual(logic.merge_report([]), [])

    def test_has_reports(self):
        self.assertEqual(logic.merge_report([[('a', 'b', 'c'),
                                              ('d', 'e', 'f')],
                                             [],
                                             [('a', 'b', 'c'),
                                              ('k', 'e', 'f')]]),
                         [('a', 'b', 'c'),
                          ('d', 'e', 'f'),
                          ('k', 'e', 'f')])


class NormalizeReportTests(helpers.BaseTests):

    def test_no_reports(self):
        self.assertEqual(logic.normalize_report([]), [])

    def test_has_reports(self):
        self.assertEqual(logic.normalize_report([('a', 'b', 'c'),
                                                 ('a', 'b', 'c'),
                                                 ('k', 'e', 'f'),
                                                 ('d', 'e', 'f')]),
                         [('a', 'b', 'c'),
                          ('d', 'e', 'f'),
                          ('k', 'e', 'f')])


class ProcessDeletionRequestTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_request(self):
        await logic.process_deletion_request(helpers.get_config()['custom'], 666)

    @test_utils.unittest_run_loop
    async def test_update_request(self):
        await operations.mark_for_deletion(core_id=uuid.uuid4().hex,
                                           ids=[('test_source_2', 20),
                                                ('test_source_2', 40)])

        unprocessed_ids = await operations.get_unprocessed_deletion_requests()

        old_request_1 = await operations.get_deletion_request(unprocessed_ids[0])
        old_request_2 = await operations.get_deletion_request(unprocessed_ids[1])

        await logic.process_deletion_request(helpers.get_config()['custom'], old_request_1.id)

        new_request_1 = await operations.get_deletion_request(unprocessed_ids[0])
        new_request_2 = await operations.get_deletion_request(unprocessed_ids[1])

        self.assertEqual(old_request_2, new_request_2)

        self.assertEqual(new_request_1.data['counter'], 1)

    @test_utils.unittest_run_loop
    async def test_remove_request(self):
        await operations.mark_for_deletion(core_id=uuid.uuid4().hex,
                                           ids=[('test_source_2', 20),
                                                ('test_source_2', 40)])

        unprocessed_ids = await operations.get_unprocessed_deletion_requests()

        unprocessed_ids.sort()

        old_request_1 = await operations.get_deletion_request(unprocessed_ids[0])
        old_request_2 = await operations.get_deletion_request(unprocessed_ids[1])

        await logic.process_deletion_request(helpers.get_config()['custom'], old_request_1.id)
        await logic.process_deletion_request(helpers.get_config()['custom'], old_request_1.id)

        new_request_1 = await operations.get_deletion_request(unprocessed_ids[0])
        new_request_2 = await operations.get_deletion_request(unprocessed_ids[1])

        self.assertEqual(old_request_2, new_request_2)
        self.assertEqual(new_request_1, None)


class ProcessDeletionRequestsTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_requests(self):
        await logic.process_deletion_requests(helpers.get_config()['custom'])

    @test_utils.unittest_run_loop
    async def test(self):
        await operations.mark_for_deletion(core_id=uuid.uuid4().hex,
                                           ids=[('test_source_2', 20),
                                                ('test_source_2', 40)])

        await operations.mark_for_deletion(core_id=uuid.uuid4().hex,
                                           ids=[('test_source_1', 1)])

        unprocessed_ids = await operations.get_unprocessed_deletion_requests()
        unprocessed_ids.sort()

        await logic.process_deletion_requests(helpers.get_config()['custom'])

        new_request_1 = await operations.get_deletion_request(unprocessed_ids[0])
        new_request_2 = await operations.get_deletion_request(unprocessed_ids[1])
        new_request_3 = await operations.get_deletion_request(unprocessed_ids[2])

        self.assertEqual(new_request_1.data['counter'], 1)
        self.assertEqual(new_request_2.data['counter'], 1)
        self.assertEqual(new_request_3, None)

        await logic.process_deletion_requests(helpers.get_config()['custom'])

        new_request_1 = await operations.get_deletion_request(unprocessed_ids[0])
        new_request_2 = await operations.get_deletion_request(unprocessed_ids[1])

        self.assertEqual(new_request_1, None)
        self.assertEqual(new_request_2.data['counter'], 2)

        await logic.process_deletion_requests(helpers.get_config()['custom'])

        new_request_2 = await operations.get_deletion_request(unprocessed_ids[1])

        self.assertEqual(new_request_2, None)
