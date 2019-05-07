
from aiohttp import test_utils

from tt_web import postgresql as db

from .. import objects
from .. import operations

from . import helpers


class SetPropertyTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_new_property(self):
        await operations.set_property(objects.Property(object_id=100, type=200, value='x.1'))
        await operations.set_property(objects.Property(object_id=200, type=200, value='x.2'))
        await operations.set_property(objects.Property(object_id=100, type=300, value='x.3'))
        await operations.set_property(objects.Property(object_id=200, type=400, value='x.4'))

        result = await db.sql('SELECT * FROM properties ORDER BY created_at')

        self.assertEqual([operations.property_from_row(row) for row in result],
                         [objects.Property(object_id=100, type=200, value='x.1'),
                          objects.Property(object_id=200, type=200, value='x.2'),
                          objects.Property(object_id=100, type=300, value='x.3'),
                          objects.Property(object_id=200, type=400, value='x.4')])

    @test_utils.unittest_run_loop
    async def test_property_exists(self):
        await operations.set_property(objects.Property(object_id=100, type=200, value='x.1'))
        await operations.set_property(objects.Property(object_id=200, type=200, value='x.2'))

        await operations.set_property(objects.Property(object_id=100, type=200, value='y.1'))
        await operations.set_property(objects.Property(object_id=300, type=200, value='y.2'))

        result = await db.sql('SELECT * FROM properties ORDER BY updated_at')

        self.assertEqual([operations.property_from_row(row) for row in result],
                         [objects.Property(object_id=200, type=200, value='x.2'),
                          objects.Property(object_id=100, type=200, value='y.1'),
                          objects.Property(object_id=300, type=200, value='y.2')])


class SetPropertiesTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test(self):
        await operations.set_properties([objects.Property(object_id=100, type=200, value='x.1'),
                                         objects.Property(object_id=200, type=200, value='x.2'),
                                         objects.Property(object_id=100, type=200, value='y.1'),
                                         objects.Property(object_id=300, type=200, value='y.2')])

        result = await db.sql('SELECT * FROM properties ORDER BY updated_at')

        self.assertEqual([operations.property_from_row(row) for row in result],
                         [objects.Property(object_id=200, type=200, value='x.2'),
                          objects.Property(object_id=100, type=200, value='y.1'),
                          objects.Property(object_id=300, type=200, value='y.2')])


class GetObjectsPropertyTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test(self):
        await operations.set_properties([objects.Property(object_id=100, type=200, value='x.1'),
                                         objects.Property(object_id=200, type=200, value='x.2'),
                                         objects.Property(object_id=100, type=200, value='y.1'),
                                         objects.Property(object_id=300, type=200, value='y.2'),
                                         objects.Property(object_id=100, type=400, value='x.4')])

        properties = await operations.get_object_properties(object_id=100, types=[200, 300, 400])

        self.assertEqual(properties,
                         [objects.Property(object_id=100, type=200, value='y.1'),
                          objects.Property(object_id=100, type=400, value='x.4')])


class GetPropertiesTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test(self):
        await operations.set_properties([objects.Property(object_id=100, type=200, value='x.1'),
                                         objects.Property(object_id=200, type=200, value='x.2'),
                                         objects.Property(object_id=100, type=200, value='y.1'),
                                         objects.Property(object_id=300, type=200, value='y.2'),
                                         objects.Property(object_id=100, type=400, value='x.4')])

        properties = await operations.get_properties({100: [200, 300, 400],
                                                      300: [200, 400]})

        properties.sort(key=lambda property: (property.object_id, property.type))

        self.assertEqual(properties,
                         [objects.Property(object_id=100, type=200, value='y.1'),
                          objects.Property(object_id=100, type=400, value='x.4'),
                          objects.Property(object_id=300, type=200, value='y.2')])
