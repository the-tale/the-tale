
import uuid

import asyncio

from aiohttp import test_utils

from tt_protocol.protocol import base_pb2
from tt_protocol.protocol import storage_pb2

from tt_web import utils
from tt_web import exceptions
from tt_web import postgresql as db

from .. import objects
from .. import protobuf
from .. import operations

from . import helpers


class ApplyTests(helpers.BaseTests):

    def setUp(self):
        super().setUp()

        self.item_1_id = uuid.uuid4()
        self.item_2_id = uuid.uuid4()
        self.item_3_id = uuid.uuid4()

        self.operations = [storage_pb2.Operation(create=storage_pb2.OperationCreate(owner_id=1,
                                                                                    item_id=self.item_1_id.hex,
                                                                                    storage_id=1,
                                                                                    data='{"a": 1}',
                                                                                    operation_type='#test',
                                                                                    base_type='base-type',
                                                                                    full_type='full-type')),
                           storage_pb2.Operation(create=storage_pb2.OperationCreate(owner_id=2,
                                                                                    item_id=self.item_2_id.hex,
                                                                                    storage_id=2,
                                                                                    data='{"b": 2}',
                                                                                    operation_type='#test',
                                                                                    base_type='base-type',
                                                                                    full_type='full-type')),
                           storage_pb2.Operation(create=storage_pb2.OperationCreate(owner_id=3,
                                                                                    item_id=self.item_3_id.hex,
                                                                                    storage_id=3,
                                                                                    data='{"c": 3}',
                                                                                    operation_type='#test',
                                                                                    base_type='base-type',
                                                                                    full_type='full-type')),
                           storage_pb2.Operation(change_owner=storage_pb2.OperationChangeOwner(item_id=self.item_2_id.hex,
                                                                                               old_owner_id=2,
                                                                                               new_owner_id=3,
                                                                                               new_storage_id=4,
                                                                                               operation_type='#test')),
                           storage_pb2.Operation(destroy=storage_pb2.OperationDestroy(item_id=self.item_3_id.hex,
                                                                                      owner_id=3,
                                                                                      operation_type='#test'))]


    @test_utils.unittest_run_loop
    async def test_no_operations(self):
        request = await self.client.post('/apply', data=storage_pb2.ApplyRequest(operations=[]).SerializeToString())
        await self.check_answer(request, storage_pb2.ApplyResponse)


    @test_utils.unittest_run_loop
    async def test_success(self):
        request = await self.client.post('/apply', data=storage_pb2.ApplyRequest(operations=self.operations).SerializeToString())
        await self.check_answer(request, storage_pb2.ApplyResponse)

        result = await db.sql('SELECT * FROM items ORDER BY updated_at DESC')

        self.assertEqual(set((row['id'], row['owner']) for row in result),
                         {(self.item_1_id, 1), (self.item_2_id, 3)})

        result = await db.sql('SELECT * FROM log_records ORDER BY created_at ASC')

        self.assertEqual([(row['item'], row['data']) for row in result],
                         [(self.item_1_id, {'item': {'a': 1}, 'operation_type': '#test', 'owner_id': 1, 'storage_id': 1, 'base_type': 'base-type', 'full_type': 'full-type'}),
                          (self.item_2_id, {'item': {'b': 2}, 'operation_type': '#test', 'owner_id': 2, 'storage_id': 2, 'base_type': 'base-type', 'full_type': 'full-type'}),
                          (self.item_3_id, {'item': {'c': 3}, 'operation_type': '#test', 'owner_id': 3, 'storage_id': 3, 'base_type': 'base-type', 'full_type': 'full-type'}),
                          (self.item_2_id, {'operation_type': '#test', 'new_owner_id': 3, 'old_owner_id': 2, 'new_storage_id': 4}),
                          (self.item_3_id, {'operation_type': '#test', 'owner_id': 3})])


    @test_utils.unittest_run_loop
    async def test_failed_operations(self):

        request = await self.client.post('/apply', data=storage_pb2.ApplyRequest(operations=[self.operations[2]]).SerializeToString())
        await self.check_answer(request, storage_pb2.ApplyResponse)

        request = await self.client.post('/apply', data=storage_pb2.ApplyRequest(operations=self.operations).SerializeToString())
        await self.check_answer(request, storage_pb2.ApplyResponse, api_status=base_pb2.ApiResponse.ERROR)

        result = await db.sql('SELECT * FROM items ORDER BY updated_at DESC')

        self.assertEqual(set((row['id'], row['owner']) for row in result),
                         {(self.item_3_id, 3)})

        result = await db.sql('SELECT * FROM log_records ORDER BY created_at ASC')

        self.assertEqual([(row['item'], row['data']) for row in result],
                         [(self.item_3_id, {'item': {'c': 3}, 'operation_type': '#test', 'owner_id': 3, 'storage_id': 3, 'base_type': 'base-type', 'full_type': 'full-type'})])



class GetItemsTests(helpers.BaseTests):

    def setUp(self):
        super().setUp()

        self.item_1_id = uuid.uuid4()
        self.item_2_id = uuid.uuid4()
        self.item_3_id = uuid.uuid4()

        self.operations = [storage_pb2.Operation(create=storage_pb2.OperationCreate(owner_id=1,
                                                                                    item_id=self.item_1_id.hex,
                                                                                    data='{"a": 1}',
                                                                                    operation_type='#test',
                                                                                    base_type='base-type',
                                                                                    full_type='full-type')),
                           storage_pb2.Operation(create=storage_pb2.OperationCreate(owner_id=2,
                                                                                    item_id=self.item_2_id.hex,
                                                                                    data='{"b": 2}',
                                                                                    operation_type='#test',
                                                                                    base_type='base-type',
                                                                                    full_type='full-type')),
                           storage_pb2.Operation(create=storage_pb2.OperationCreate(owner_id=2,
                                                                                    item_id=self.item_3_id.hex,
                                                                                    data='{"c": 2}',
                                                                                    operation_type='#test',
                                                                                    base_type='base-type',
                                                                                    full_type='full-type'))]


    async def fill_database(self):
        request = await self.client.post('/apply', data=storage_pb2.ApplyRequest(operations=self.operations).SerializeToString())
        await self.check_answer(request, storage_pb2.ApplyResponse)


    @test_utils.unittest_run_loop
    async def test_no_items(self):
        await self.fill_database()

        request = await self.client.post('/get-items', data=storage_pb2.GetItemsRequest(owner_id=666).SerializeToString())
        data = await self.check_answer(request, storage_pb2.GetItemsResponse)
        self.assertEqual(list(data.items), [])


    @test_utils.unittest_run_loop
    async def test_has_items(self):
        await self.fill_database()

        request = await self.client.post('/get-items', data=storage_pb2.GetItemsRequest(owner_id=2).SerializeToString())
        data = await self.check_answer(request, storage_pb2.GetItemsResponse)

        self.assertCountEqual(list(data.items),
                              [storage_pb2.Item(id=self.item_2_id.hex, owner_id=2, data='{"b": 2}'),
                               storage_pb2.Item(id=self.item_3_id.hex, owner_id=2, data='{"c": 2}')])



class HasItemsTests(helpers.BaseTests):

    def setUp(self):
        super().setUp()

        self.item_1_id = uuid.uuid4()
        self.item_2_id = uuid.uuid4()
        self.item_3_id = uuid.uuid4()

        self.operations = [storage_pb2.Operation(create=storage_pb2.OperationCreate(owner_id=1,
                                                                                    item_id=self.item_1_id.hex,
                                                                                    data='{"a": 1}',
                                                                                    operation_type='#test',
                                                                                    base_type='base-type',
                                                                                    full_type='full-type')),
                           storage_pb2.Operation(create=storage_pb2.OperationCreate(owner_id=2,
                                                                                    item_id=self.item_2_id.hex,
                                                                                    data='{"b": 2}',
                                                                                    operation_type='#test',
                                                                                    base_type='base-type',
                                                                                    full_type='full-type')),
                           storage_pb2.Operation(create=storage_pb2.OperationCreate(owner_id=2,
                                                                                    item_id=self.item_3_id.hex,
                                                                                    data='{"c": 2}',
                                                                                    operation_type='#test',
                                                                                    base_type='base-type',
                                                                                    full_type='full-type'))]


    async def fill_database(self):
        request = await self.client.post('/apply', data=storage_pb2.ApplyRequest(operations=self.operations).SerializeToString())
        await self.check_answer(request, storage_pb2.ApplyResponse)


    @test_utils.unittest_run_loop
    async def test_no_items(self):
        await self.fill_database()

        request = await self.client.post('/has-items', data=storage_pb2.HasItemsRequest(owner_id=666, items_ids=[uuid.uuid4().hex]).SerializeToString())
        data = await self.check_answer(request, storage_pb2.HasItemsResponse)
        self.assertFalse(data.has)


    @test_utils.unittest_run_loop
    async def test_has_items(self):
        await self.fill_database()

        request = await self.client.post('/has-items', data=storage_pb2.HasItemsRequest(owner_id=2, items_ids=[self.item_2_id.hex]).SerializeToString())
        data = await self.check_answer(request, storage_pb2.HasItemsResponse)

        self.assertTrue(data.has)
