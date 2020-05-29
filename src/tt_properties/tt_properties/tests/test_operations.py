
from aiohttp import test_utils

from tt_web import postgresql as db

from .. import relations
from .. import operations

from . import helpers


class SetPropertyTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_replace(self):
        await operations.set_property(helpers.property(object_id=100, type=200, value='x.1', mode=relations.MODE.REPLACE))
        await operations.set_property(helpers.property(object_id=200, type=200, value='x.2', mode=relations.MODE.REPLACE))

        await operations.set_property(helpers.property(object_id=100, type=200, value='y.1', mode=relations.MODE.REPLACE))
        await operations.set_property(helpers.property(object_id=300, type=200, value='y.2', mode=relations.MODE.REPLACE))

        result = await db.sql('SELECT * FROM properties ORDER BY created_at')

        self.assertEqual([operations.property_from_row(row) for row in result],
                         [helpers.property(object_id=200, type=200, value='x.2'),
                          helpers.property(object_id=100, type=200, value='y.1'),
                          helpers.property(object_id=300, type=200, value='y.2')])


class AppendPropertyTests(helpers.BaseTests):
    @test_utils.unittest_run_loop
    async def test_append(self):
        await operations.append_property(helpers.property(object_id=100, type=200, value='x.1', mode=relations.MODE.APPEND))
        await operations.append_property(helpers.property(object_id=200, type=200, value='x.2', mode=relations.MODE.APPEND))
        await operations.append_property(helpers.property(object_id=100, type=300, value='x.3', mode=relations.MODE.APPEND))
        await operations.append_property(helpers.property(object_id=200, type=200, value='x.4', mode=relations.MODE.APPEND))

        result = await db.sql('SELECT * FROM properties ORDER BY created_at')

        self.assertCountEqual([operations.property_from_row(row) for row in result],
                              [helpers.property(object_id=100, type=200, value='x.1'),
                               helpers.property(object_id=200, type=200, value='x.2'),
                               helpers.property(object_id=100, type=300, value='x.3'),
                               helpers.property(object_id=200, type=200, value='x.4')])


class SetPropertiesTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test(self):
        await operations.set_properties([helpers.property(object_id=100, type=200, value='x.1', mode=relations.MODE.REPLACE),
                                         helpers.property(object_id=200, type=200, value='x.2', mode=relations.MODE.REPLACE),
                                         helpers.property(object_id=100, type=200, value='y.1', mode=relations.MODE.REPLACE),
                                         helpers.property(object_id=300, type=200, value='y.2', mode=relations.MODE.REPLACE),
                                         helpers.property(object_id=100, type=200, value='y.3', mode=relations.MODE.APPEND),
                                         helpers.property(object_id=300, type=200, value='y.4', mode=relations.MODE.REPLACE)])

        result = await db.sql('SELECT * FROM properties ORDER BY created_at')

        self.assertCountEqual([operations.property_from_row(row) for row in result],
                              [helpers.property(object_id=200, type=200, value='x.2'),
                               helpers.property(object_id=100, type=200, value='y.1'),
                               helpers.property(object_id=300, type=200, value='y.4'),
                               helpers.property(object_id=100, type=200, value='y.3')])


class GetObjectsPropertyTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test(self):
        await operations.set_properties([helpers.property(object_id=100, type=200, value='x.1', mode=relations.MODE.REPLACE),
                                         helpers.property(object_id=200, type=200, value='x.2', mode=relations.MODE.REPLACE),
                                         helpers.property(object_id=100, type=200, value='y.1', mode=relations.MODE.REPLACE),
                                         helpers.property(object_id=300, type=200, value='y.2', mode=relations.MODE.REPLACE),
                                         helpers.property(object_id=100, type=400, value='x.4', mode=relations.MODE.REPLACE)])

        properties = await operations.get_object_properties(object_id=100, types=[200, 300, 400])

        self.assertEqual(properties,
                         [helpers.property(object_id=100, type=200, value='y.1'),
                          helpers.property(object_id=100, type=400, value='x.4')])

    @test_utils.unittest_run_loop
    async def test_multiple(self):
        await operations.set_properties([helpers.property(object_id=100, type=200, value='x.1', mode=relations.MODE.APPEND),
                                         helpers.property(object_id=200, type=200, value='x.2', mode=relations.MODE.APPEND),
                                         helpers.property(object_id=100, type=200, value='y.1', mode=relations.MODE.APPEND),
                                         helpers.property(object_id=300, type=200, value='y.2', mode=relations.MODE.APPEND),
                                         helpers.property(object_id=100, type=400, value='x.4', mode=relations.MODE.APPEND)])

        properties = await operations.get_object_properties(object_id=100, types=[200, 300, 400])

        self.assertCountEqual(properties,
                              [helpers.property(object_id=100, type=200, value='x.1'),
                               helpers.property(object_id=100, type=200, value='y.1'),
                               helpers.property(object_id=100, type=400, value='x.4')])


class GetPropertiesTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test(self):
        await operations.set_properties([helpers.property(object_id=100, type=200, value='x.1', mode=relations.MODE.REPLACE),
                                         helpers.property(object_id=200, type=200, value='x.2', mode=relations.MODE.REPLACE),
                                         helpers.property(object_id=100, type=200, value='y.1', mode=relations.MODE.REPLACE),
                                         helpers.property(object_id=300, type=200, value='y.2', mode=relations.MODE.REPLACE),
                                         helpers.property(object_id=100, type=400, value='x.4', mode=relations.MODE.REPLACE)])

        properties = await operations.get_properties({100: [200, 300, 400],
                                                      300: [200, 400]})

        properties.sort(key=lambda property: (property.object_id, property.type))

        self.assertEqual(properties,
                         [helpers.property(object_id=100, type=200, value='y.1'),
                          helpers.property(object_id=100, type=400, value='x.4'),
                          helpers.property(object_id=300, type=200, value='y.2')])

    @test_utils.unittest_run_loop
    async def test_multiple(self):
        await operations.set_properties([helpers.property(object_id=100, type=200, value='x.1', mode=relations.MODE.APPEND),
                                         helpers.property(object_id=200, type=200, value='x.2', mode=relations.MODE.APPEND),
                                         helpers.property(object_id=100, type=200, value='y.1', mode=relations.MODE.APPEND),
                                         helpers.property(object_id=300, type=200, value='y.2', mode=relations.MODE.APPEND),
                                         helpers.property(object_id=100, type=400, value='x.4', mode=relations.MODE.APPEND)])

        properties = await operations.get_properties({100: [200, 300, 400],
                                                      300: [200, 400]})

        properties.sort(key=lambda property: (property.object_id, property.type))

        self.assertCountEqual(properties,
                              [helpers.property(object_id=100, type=200, value='x.1'),
                               helpers.property(object_id=100, type=200, value='y.1'),
                               helpers.property(object_id=100, type=400, value='x.4'),
                               helpers.property(object_id=300, type=200, value='y.2')])


class GetDataReportTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test(self):
        await operations.set_properties([helpers.property(object_id=100, type=200, value='x.1', mode=relations.MODE.APPEND),
                                         helpers.property(object_id=200, type=200, value='x.2', mode=relations.MODE.APPEND),
                                         helpers.property(object_id=100, type=200, value='y.1', mode=relations.MODE.APPEND),
                                         helpers.property(object_id=300, type=200, value='y.2', mode=relations.MODE.APPEND),
                                         helpers.property(object_id=100, type=400, value='x.4', mode=relations.MODE.APPEND)])

        report = await operations.get_data_report(object_id=100)

        self.assertCountEqual(report, [('property', {'type': 200, 'value': 'x.1'}),
                                       ('property', {'type': 200, 'value': 'y.1'}),
                                       ('property', {'type': 400, 'value': 'x.4'})])


class CleanObjectProperties(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test(self):
        await operations.set_properties([helpers.property(object_id=100, type=200, value='x.1', mode=relations.MODE.APPEND),
                                         helpers.property(object_id=200, type=200, value='x.2', mode=relations.MODE.APPEND),
                                         helpers.property(object_id=100, type=200, value='y.1', mode=relations.MODE.APPEND),
                                         helpers.property(object_id=300, type=200, value='y.2', mode=relations.MODE.APPEND),
                                         helpers.property(object_id=100, type=400, value='x.4', mode=relations.MODE.APPEND)])

        await operations.clean_object_properties(object_id=100)

        report = await operations.get_data_report(object_id=100)

        self.assertCountEqual(report, [])

        report = await operations.get_data_report(object_id=200)

        self.assertCountEqual(report, [('property', {'type': 200, 'value': 'x.2'})])
