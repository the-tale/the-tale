
from aiohttp import test_utils

from tt_protocol.protocol import properties_pb2
from tt_protocol.protocol import data_protector_pb2

from tt_web import s11n
from tt_web import postgresql as db

from .. import protobuf
from .. import operations
from .. import relations

from . import helpers


class SetPropertiesTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test(self):
        properties = [properties_pb2.Property(object_id=100, type=200, value='x.1', mode=properties_pb2.Property.Mode.REPLACE),
                      properties_pb2.Property(object_id=200, type=200, value='x.2', mode=properties_pb2.Property.Mode.REPLACE)]

        data = properties_pb2.SetPropertiesRequest(properties=properties).SerializeToString()
        request = await self.client.post('/set-properties', data=data)
        await self.check_success(request, properties_pb2.SetPropertiesResponse)

        properties = [properties_pb2.Property(object_id=100, type=200, value='y.1', mode=properties_pb2.Property.Mode.REPLACE),
                      properties_pb2.Property(object_id=300, type=200, value='y.2', mode=properties_pb2.Property.Mode.REPLACE),
                      properties_pb2.Property(object_id=200, type=200, value='y.3', mode=properties_pb2.Property.Mode.APPEND)]

        data = properties_pb2.SetPropertiesRequest(properties=properties).SerializeToString()
        request = await self.client.post('/set-properties', data=data)
        await self.check_success(request, properties_pb2.SetPropertiesResponse)

        result = await db.sql('SELECT * FROM properties ORDER BY created_at')

        self.assertCountEqual([operations.property_from_row(row) for row in result],
                              [helpers.property(object_id=200, type=200, value='x.2'),
                               helpers.property(object_id=200, type=200, value='y.3'),
                               helpers.property(object_id=100, type=200, value='y.1'),
                               helpers.property(object_id=300, type=200, value='y.2')])


class GetPropertiesTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test(self):
        properties = [properties_pb2.Property(object_id=100, type=200, value='x.1', mode=properties_pb2.Property.Mode.REPLACE),
                      properties_pb2.Property(object_id=200, type=200, value='x.2', mode=properties_pb2.Property.Mode.REPLACE),
                      properties_pb2.Property(object_id=100, type=300, value='x.3', mode=properties_pb2.Property.Mode.REPLACE),
                      properties_pb2.Property(object_id=100, type=400, value='x.4', mode=properties_pb2.Property.Mode.REPLACE)]

        data = properties_pb2.SetPropertiesRequest(properties=properties).SerializeToString()
        request = await self.client.post('/set-properties', data=data)
        await self.check_success(request, properties_pb2.SetPropertiesResponse)

        properties = [properties_pb2.Property(object_id=100, type=200, value='y.1', mode=properties_pb2.Property.Mode.REPLACE),
                      properties_pb2.Property(object_id=300, type=200, value='y.2', mode=properties_pb2.Property.Mode.REPLACE),
                      properties_pb2.Property(object_id=200, type=200, value='y.3', mode=properties_pb2.Property.Mode.APPEND),
                      properties_pb2.Property(object_id=100, type=400, value='y.4', mode=properties_pb2.Property.Mode.APPEND)]

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

        self.assertCountEqual(properties,
                              [helpers.property(object_id=100, type=200, value='y.1'),
                               helpers.property(object_id=100, type=400, value='x.4'),
                               helpers.property(object_id=100, type=400, value='y.4'),
                               helpers.property(object_id=300, type=200, value='y.2')])


class DataProtectionCollectDataTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_wrong_secret(self):
        secret = 'wrong.secret'

        request = await self.client.post('/data-protection-collect-data',
                                         data=data_protector_pb2.PluginReportRequest(account_id='777',
                                                                                      secret=secret).SerializeToString())
        await self.check_error(request, 'properties.data_protection_collect_data.wrong_secret')

    @test_utils.unittest_run_loop
    async def test_no_data(self):

        secret = helpers.get_config()['custom']['data_protector']['secret']

        request = await self.client.post('/data-protection-collect-data',
                                         data=data_protector_pb2.PluginReportRequest(account_id='777',
                                                                                      secret=secret).SerializeToString())
        response = await self.check_success(request, data_protector_pb2.PluginReportResponse, raw=True)

        self.assertEqual(response.result, data_protector_pb2.PluginReportResponse.ResultType.Value('SUCCESS'))

        report = s11n.from_json(response.data)

        self.assertEqual(report, [])

    @test_utils.unittest_run_loop
    async def test_has_data(self):
        # prepair data
        await operations.set_properties([helpers.property(object_id=100, type=200, value='x.1', mode=relations.MODE.APPEND),
                                         helpers.property(object_id=200, type=200, value='x.2', mode=relations.MODE.APPEND),
                                         helpers.property(object_id=100, type=200, value='y.1', mode=relations.MODE.APPEND),
                                         helpers.property(object_id=300, type=200, value='y.2', mode=relations.MODE.APPEND),
                                         helpers.property(object_id=100, type=400, value='x.4', mode=relations.MODE.APPEND)])

        # request data

        secret = helpers.get_config()['custom']['data_protector']['secret']

        request = await self.client.post('/data-protection-collect-data',
                                         data=data_protector_pb2.PluginReportRequest(account_id=str('100'),
                                                                                     secret=secret).SerializeToString())
        response = await self.check_success(request, data_protector_pb2.PluginReportResponse, raw=True)

        self.assertEqual(response.result, data_protector_pb2.PluginReportResponse.ResultType.Value('SUCCESS'))

        report = s11n.from_json(response.data)

        self.assertCountEqual(report, [['property', {'type': 200, 'value': 'x.1'}],
                                       ['property', {'type': 200, 'value': 'y.1'}],
                                       ['property', {'type': 400, 'value': 'x.4'}]])


class DataProtectionDeleteDataTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_wrong_secret(self):
        secret = 'wrong.secret'

        request = await self.client.post('/data-protection-delete-data',
                                         data=data_protector_pb2.PluginDeletionRequest(account_id='777',
                                                                                       secret=secret).SerializeToString())
        await self.check_error(request, 'properties.data_protection_delete_data.wrong_secret')

    @test_utils.unittest_run_loop
    async def test_no_data(self):

        secret = helpers.get_config()['custom']['data_protector']['secret']

        request = await self.client.post('/data-protection-delete-data',
                                         data=data_protector_pb2.PluginDeletionRequest(account_id='777',
                                                                                       secret=secret).SerializeToString())
        response = await self.check_success(request, data_protector_pb2.PluginDeletionResponse, raw=True)

        self.assertEqual(response.result, data_protector_pb2.PluginDeletionResponse.ResultType.Value('SUCCESS'))


    @test_utils.unittest_run_loop
    async def test_has_data(self):
        # prepair data
        await operations.set_properties([helpers.property(object_id=100, type=200, value='x.1', mode=relations.MODE.APPEND),
                                         helpers.property(object_id=200, type=200, value='x.2', mode=relations.MODE.APPEND),
                                         helpers.property(object_id=100, type=200, value='y.1', mode=relations.MODE.APPEND),
                                         helpers.property(object_id=300, type=200, value='y.2', mode=relations.MODE.APPEND),
                                         helpers.property(object_id=100, type=400, value='x.4', mode=relations.MODE.APPEND)])
        # request data

        secret = helpers.get_config()['custom']['data_protector']['secret']

        request = await self.client.post('/data-protection-delete-data',
                                         data=data_protector_pb2.PluginDeletionRequest(account_id='100',
                                                                                       secret=secret).SerializeToString())
        response = await self.check_success(request, data_protector_pb2.PluginDeletionResponse, raw=True)

        self.assertEqual(response.result, data_protector_pb2.PluginDeletionResponse.ResultType.Value('SUCCESS'))

        report = await operations.get_data_report(object_id=100)

        self.assertCountEqual(report, [])

        report = await operations.get_data_report(object_id=200)

        self.assertCountEqual(report, [('property', {'type': 200, 'value': 'x.2'})])
