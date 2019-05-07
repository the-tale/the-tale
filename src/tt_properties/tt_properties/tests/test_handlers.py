
from aiohttp import test_utils

from tt_protocol.protocol import properties_pb2

from tt_web import postgresql as db

from .. import objects
from .. import protobuf
from .. import operations

from . import helpers


class SetPropertiesTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test(self):
        properties = [properties_pb2.Property(object_id=100, type=200, value='x.1'),
                      properties_pb2.Property(object_id=200, type=200, value='x.2')]

        data = properties_pb2.SetPropertiesRequest(properties=properties).SerializeToString()
        request = await self.client.post('/set-properties', data=data)
        await self.check_success(request, properties_pb2.SetPropertiesResponse)

        properties = [properties_pb2.Property(object_id=100, type=200, value='y.1'),
                      properties_pb2.Property(object_id=300, type=200, value='y.2')]

        data = properties_pb2.SetPropertiesRequest(properties=properties).SerializeToString()
        request = await self.client.post('/set-properties', data=data)
        await self.check_success(request, properties_pb2.SetPropertiesResponse)

        result = await db.sql('SELECT * FROM properties ORDER BY updated_at')

        self.assertEqual([operations.property_from_row(row) for row in result],
                         [objects.Property(object_id=200, type=200, value='x.2'),
                          objects.Property(object_id=100, type=200, value='y.1'),
                          objects.Property(object_id=300, type=200, value='y.2')])


class GetPropertiesTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test(self):
        properties = [properties_pb2.Property(object_id=100, type=200, value='x.1'),
                      properties_pb2.Property(object_id=200, type=200, value='x.2'),
                      properties_pb2.Property(object_id=100, type=300, value='x.3'),
                      properties_pb2.Property(object_id=100, type=400, value='x.4')]

        data = properties_pb2.SetPropertiesRequest(properties=properties).SerializeToString()
        request = await self.client.post('/set-properties', data=data)
        await self.check_success(request, properties_pb2.SetPropertiesResponse)

        properties = [properties_pb2.Property(object_id=100, type=200, value='y.1'),
                      properties_pb2.Property(object_id=300, type=200, value='y.2')]

        data = properties_pb2.SetPropertiesRequest(properties=properties).SerializeToString()
        request = await self.client.post('/set-properties', data=data)
        await self.check_success(request, properties_pb2.SetPropertiesResponse)

        objects_properties = [properties_pb2.PropertiesList(object_id=100, types=[200, 400]),
                              properties_pb2.PropertiesList(object_id=300, types=[200, 500])]

        data = properties_pb2.GetPropertiesRequest(objects=objects_properties).SerializeToString()
        request = await self.client.post('/get-properties', data=data)
        answer = await self.check_success(request, properties_pb2.GetPropertiesResponse)

        properties = [protobuf.to_property(property) for property in answer.properties]

        properties.sort(key=lambda property: (property.object_id, property.type))

        self.assertEqual(properties,
                         [objects.Property(object_id=100, type=200, value='y.1'),
                          objects.Property(object_id=100, type=400, value='x.4'),
                          objects.Property(object_id=300, type=200, value='y.2')])
