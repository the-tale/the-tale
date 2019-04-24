
import uuid

from aiohttp import test_utils

from tt_web import postgresql as db

from .. import objects
from .. import operations
from .. import exceptions
from .. import relations

from . import helpers


class LogTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_create(self):
        transaction_id = uuid.uuid4()
        item_id = uuid.uuid4()

        await operations.log(db.sql, transaction_id, item_id=item_id, data={'a': 'b'}, type=relations.OPERATION.DESTROY)

        result = await db.sql('SELECT * FROM log_records ORDER BY created_at DESC')

        self.assertEqual(result[0]['transaction'], transaction_id)
        self.assertEqual(result[0]['item'], item_id)
        self.assertEqual(result[0]['type'], relations.OPERATION.DESTROY.value)
        self.assertEqual(result[0]['data'], {'a': 'b'})


class ApplyCreateTests(helpers.BaseTests):

    def setUp(self):
        super().setUp()
        self.operation = objects.OperationCreate(owner_id=666,
                                                 item_id=uuid.uuid4(),
                                                 storage_id=13,
                                                 base_type='base-type',
                                                 full_type='full-type',
                                                 data={'a': 'b'},
                                                 operation_type='#test')

    @test_utils.unittest_run_loop
    async def test_create(self):
        await operations.apply_create(db.sql, uuid.uuid4(), self.operation)

        result = await db.sql('SELECT * FROM items ORDER BY created_at DESC')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['id'], self.operation.item_id)
        self.assertEqual(result[0]['owner'], 666)
        self.assertEqual(result[0]['storage'], 13)
        self.assertEqual(result[0]['base_type'], 'base-type')
        self.assertEqual(result[0]['full_type'], 'full-type')
        self.assertEqual(result[0]['data'], {'a': 'b'})

        item_id = result[0]['id']

        result = await db.sql('SELECT * FROM log_records ORDER BY created_at DESC')

        self.assertEqual(result[0]['item'], item_id)
        self.assertEqual(result[0]['type'], relations.OPERATION.CREATE.value)
        self.assertEqual(result[0]['data'], {'item': {'a': 'b'},
                                             'base_type': 'base-type',
                                             'full_type': 'full-type',
                                             'owner_id': 666,
                                             'storage_id': 13,
                                             'operation_type': '#test'})

    async def check_duplicate_item_id(self, user_id):

        operation_2 = objects.OperationCreate(owner_id=user_id,
                                              item_id=self.operation.item_id,
                                              storage_id=0,
                                              data={'c': 'd'},
                                              base_type='base-type-2',
                                              full_type='full-type-2',
                                              operation_type='#test')

        await operations.apply_create(db.sql, uuid.uuid4(), self.operation)

        with self.assertRaises(exceptions.ItemAlreadyCreated):
            await operations.apply_create(db.sql, uuid.uuid4(), operation_2)

        result = await db.sql('SELECT * FROM items ORDER BY created_at DESC')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['id'], self.operation.item_id)
        self.assertEqual(result[0]['owner'], 666)
        self.assertEqual(result[0]['storage'], 13)
        self.assertEqual(result[0]['base_type'], 'base-type')
        self.assertEqual(result[0]['full_type'], 'full-type')
        self.assertEqual(result[0]['data'], {'a': 'b'})

        item_id = result[0]['id']

        result = await db.sql('SELECT * FROM log_records ORDER BY created_at DESC')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['item'], item_id)
        self.assertEqual(result[0]['type'], relations.OPERATION.CREATE.value)
        self.assertEqual(result[0]['data'], {'item': {'a': 'b'},
                                             'base_type': 'base-type',
                                             'full_type': 'full-type',
                                             'owner_id': 666,
                                             'storage_id': 13,
                                             'operation_type': '#test'})

    @test_utils.unittest_run_loop
    async def test_duplicate_item_id__same_owner(self):
        await self.check_duplicate_item_id(self.operation.owner_id)

    @test_utils.unittest_run_loop
    async def check_duplicate_item_id__other_owner(self, user_id):
        await self.check_duplicate_item_id(self.operation.owner_id+1)


class ApplyDestroyTests(helpers.BaseTests):

    def setUp(self):
        super().setUp()
        self.operation_destroy = objects.OperationDestroy(owner_id=666,
                                                          item_id=uuid.uuid4(),
                                                          operation_type='#test')

    @test_utils.unittest_run_loop
    async def test_no_object(self):

        with self.assertRaises(exceptions.CanNotDeleteItem):
            await operations.apply_destroy(db.sql, uuid.uuid4(), self.operation_destroy)

        result = await db.sql('SELECT * FROM items ORDER BY created_at DESC')

        self.assertEqual(len(result), 0)

        result = await db.sql('SELECT * FROM log_records ORDER BY created_at DESC')

        self.assertEqual(len(result), 0)

    @test_utils.unittest_run_loop
    async def test_wrong_owner(self):
        operation_create = objects.OperationCreate(owner_id=self.operation_destroy.owner_id+1,
                                                   item_id=self.operation_destroy.item_id,
                                                   storage_id=666,
                                                   data={'a': 'b'},
                                                   base_type='base-type',
                                                   full_type='full-type',
                                                   operation_type='#test')

        await operations.apply_create(db.sql, uuid.uuid4(), operation_create)

        with self.assertRaises(exceptions.CanNotDeleteItem):
            await operations.apply_destroy(db.sql, uuid.uuid4(), self.operation_destroy)

        result = await db.sql('SELECT * FROM items ORDER BY created_at DESC')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['id'], self.operation_destroy.item_id)
        self.assertEqual(result[0]['owner'], self.operation_destroy.owner_id+1)
        self.assertEqual(result[0]['storage'], 666)
        self.assertEqual(result[0]['data'], {'a': 'b'})

        result = await db.sql('SELECT * FROM log_records ORDER BY created_at DESC')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['type'], relations.OPERATION.CREATE.value)

    @test_utils.unittest_run_loop
    async def test_success(self):
        operation_create = objects.OperationCreate(owner_id=self.operation_destroy.owner_id,
                                                   item_id=self.operation_destroy.item_id,
                                                   storage_id=666,
                                                   data={'a': 'b'},
                                                   base_type='base-type',
                                                   full_type='full-type',
                                                   operation_type='#test')

        await operations.apply_create(db.sql, uuid.uuid4(), operation_create)

        await operations.apply_destroy(db.sql, uuid.uuid4(), self.operation_destroy)

        result = await db.sql('SELECT * FROM items ORDER BY created_at DESC')

        self.assertEqual(len(result), 0)

        result = await db.sql('SELECT * FROM log_records ORDER BY created_at DESC')

        self.assertEqual(len(result), 2)

        self.assertEqual(result[0]['item'], self.operation_destroy.item_id)
        self.assertEqual(result[0]['type'], relations.OPERATION.DESTROY.value)
        self.assertEqual(result[0]['data'], {'owner_id': self.operation_destroy.owner_id,
                                             'operation_type': '#test'})

        self.assertEqual(result[1]['type'], relations.OPERATION.CREATE.value)


class ApplyChangeOwnerTests(helpers.BaseTests):

    def setUp(self):
        super().setUp()
        self.operation_move = objects.OperationChangeOwner(item_id=uuid.uuid4(),
                                                           old_owner_id=666,
                                                           new_owner_id=777,
                                                           new_storage_id=5,
                                                           operation_type='#test')

    @test_utils.unittest_run_loop
    async def test_no_item(self):

        with self.assertRaises(exceptions.CanNotChangeItemOwner):
            await operations.apply_change_owner(db.sql, uuid.uuid4(), self.operation_move)

        result = await db.sql('SELECT * FROM items ORDER BY created_at DESC')

        self.assertEqual(len(result), 0)

        result = await db.sql('SELECT * FROM log_records ORDER BY created_at DESC')

        self.assertEqual(len(result), 0)

    @test_utils.unittest_run_loop
    async def test_move_to_same_user(self):
        operation_create = objects.OperationCreate(owner_id=self.operation_move.old_owner_id,
                                                   item_id=self.operation_move.item_id,
                                                   storage_id=0,
                                                   data={'a': 'b'},
                                                   base_type='base-type',
                                                   full_type='full-type',
                                                   operation_type='#test')

        await operations.apply_create(db.sql, uuid.uuid4(), operation_create)

        operation_move_2 = objects.OperationChangeOwner(item_id=self.operation_move.item_id,
                                                        old_owner_id=self.operation_move.old_owner_id,
                                                        new_owner_id=self.operation_move.old_owner_id,
                                                        new_storage_id=6,
                                                        operation_type='#test')

        with self.assertRaises(exceptions.CanNotChangeItemOwnerSameOwner):
            await operations.apply_change_owner(db.sql, uuid.uuid4(), operation_move_2)

        result = await db.sql('SELECT * FROM items ORDER BY created_at DESC')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['id'], self.operation_move.item_id)
        self.assertEqual(result[0]['owner'], self.operation_move.old_owner_id)
        self.assertEqual(result[0]['storage'], operation_create.storage_id)

        result = await db.sql('SELECT * FROM log_records ORDER BY created_at DESC')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['type'], relations.OPERATION.CREATE.value)

    @test_utils.unittest_run_loop
    async def test_wrong_owner(self):
        operation_create = objects.OperationCreate(owner_id=self.operation_move.old_owner_id,
                                                   item_id=self.operation_move.item_id,
                                                   storage_id=1,
                                                   data={'a': 'b'},
                                                   base_type='base-type',
                                                   full_type='full-type',
                                                   operation_type='#test')

        await operations.apply_create(db.sql, uuid.uuid4(), operation_create)

        operation_move_2 = objects.OperationChangeOwner(item_id=self.operation_move.item_id,
                                                        old_owner_id=self.operation_move.old_owner_id+1,
                                                        new_owner_id=self.operation_move.old_owner_id,
                                                        new_storage_id=2,
                                                        operation_type='#test')

        with self.assertRaises(exceptions.CanNotChangeItemOwner):
            await operations.apply_change_owner(db.sql, uuid.uuid4(), operation_move_2)

        result = await db.sql('SELECT * FROM items ORDER BY created_at DESC')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['id'], self.operation_move.item_id)
        self.assertEqual(result[0]['owner'], self.operation_move.old_owner_id)
        self.assertEqual(result[0]['storage'], operation_create.storage_id)

        result = await db.sql('SELECT * FROM log_records ORDER BY created_at DESC')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['type'], relations.OPERATION.CREATE.value)

    @test_utils.unittest_run_loop
    async def test_success(self):
        operation_create = objects.OperationCreate(owner_id=self.operation_move.old_owner_id,
                                                   item_id=self.operation_move.item_id,
                                                   storage_id=1,
                                                   data={'a': 'b'},
                                                   base_type='base-type',
                                                   full_type='full-type',
                                                   operation_type='#test')

        await operations.apply_create(db.sql, uuid.uuid4(), operation_create)

        await operations.apply_change_owner(db.sql, uuid.uuid4(), self.operation_move)

        result = await db.sql('SELECT * FROM items ORDER BY created_at DESC')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['id'], self.operation_move.item_id)
        self.assertEqual(result[0]['owner'], self.operation_move.new_owner_id)
        self.assertEqual(result[0]['storage'], self.operation_move.new_storage_id)

        result = await db.sql('SELECT * FROM log_records ORDER BY created_at DESC')

        self.assertEqual(len(result), 2)

        self.assertEqual(result[0]['item'], self.operation_move.item_id)
        self.assertEqual(result[0]['type'], relations.OPERATION.CHANGE_OWNER.value)
        self.assertEqual(result[0]['data'], {'old_owner_id': self.operation_move.old_owner_id,
                                             'new_owner_id': self.operation_move.new_owner_id,
                                             'new_storage_id': 5,
                                             'operation_type': '#test'})

        self.assertEqual(result[1]['type'], relations.OPERATION.CREATE.value)


class ApplyChangeStorageTests(helpers.BaseTests):

    def setUp(self):
        super().setUp()
        self.operation_move = objects.OperationChangeStorage(item_id=uuid.uuid4(),
                                                             owner_id=666,
                                                             old_storage_id=1,
                                                             new_storage_id=5,
                                                             operation_type='#test')

    @test_utils.unittest_run_loop
    async def test_no_item(self):

        with self.assertRaises(exceptions.CanNotChangeItemStorage):
            await operations.apply_change_storage(db.sql, uuid.uuid4(), self.operation_move)

        result = await db.sql('SELECT * FROM items ORDER BY created_at DESC')

        self.assertEqual(len(result), 0)

        result = await db.sql('SELECT * FROM log_records ORDER BY created_at DESC')

        self.assertEqual(len(result), 0)

    @test_utils.unittest_run_loop
    async def test_move_to_same_storage(self):
        operation_create = objects.OperationCreate(owner_id=self.operation_move.owner_id,
                                                   item_id=self.operation_move.item_id,
                                                   storage_id=7,
                                                   data={'a': 'b'},
                                                   base_type='base-type',
                                                   full_type='full-type',
                                                   operation_type='#test')

        await operations.apply_create(db.sql, uuid.uuid4(), operation_create)

        operation_move_2 = objects.OperationChangeStorage(item_id=self.operation_move.item_id,
                                                          owner_id=self.operation_move.owner_id,
                                                          old_storage_id=1,
                                                          new_storage_id=7,
                                                          operation_type='#test')

        await operations.apply_change_storage(db.sql, uuid.uuid4(), operation_move_2)

        result = await db.sql('SELECT * FROM items ORDER BY created_at DESC')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['id'], self.operation_move.item_id)
        self.assertEqual(result[0]['storage'], operation_create.storage_id)

        result = await db.sql('SELECT * FROM log_records ORDER BY created_at DESC')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['type'], relations.OPERATION.CREATE.value)

    @test_utils.unittest_run_loop
    async def test_wrong_storage(self):
        operation_create = objects.OperationCreate(owner_id=self.operation_move.owner_id,
                                                   item_id=self.operation_move.item_id,
                                                   storage_id=1,
                                                   data={'a': 'b'},
                                                   base_type='base-type',
                                                   full_type='full-type',
                                                   operation_type='#test')

        await operations.apply_create(db.sql, uuid.uuid4(), operation_create)

        operation_move_2 = objects.OperationChangeStorage(item_id=self.operation_move.item_id,
                                                          owner_id=self.operation_move.owner_id,
                                                          old_storage_id=666,
                                                          new_storage_id=2,
                                                          operation_type='#test')

        with self.assertRaises(exceptions.CanNotChangeItemStorage):
            await operations.apply_change_storage(db.sql, uuid.uuid4(), operation_move_2)

        result = await db.sql('SELECT * FROM items ORDER BY created_at DESC')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['id'], self.operation_move.item_id)
        self.assertEqual(result[0]['storage'], operation_create.storage_id)

        result = await db.sql('SELECT * FROM log_records ORDER BY created_at DESC')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['type'], relations.OPERATION.CREATE.value)

    @test_utils.unittest_run_loop
    async def test_success(self):
        operation_create = objects.OperationCreate(owner_id=self.operation_move.owner_id,
                                                   item_id=self.operation_move.item_id,
                                                   storage_id=1,
                                                   data={'a': 'b'},
                                                   base_type='base-type',
                                                   full_type='full-type',
                                                   operation_type='#test')

        await operations.apply_create(db.sql, uuid.uuid4(), operation_create)

        await operations.apply_change_storage(db.sql, uuid.uuid4(), self.operation_move)

        result = await db.sql('SELECT * FROM items ORDER BY created_at DESC')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['id'], self.operation_move.item_id)
        self.assertEqual(result[0]['storage'], self.operation_move.new_storage_id)

        result = await db.sql('SELECT * FROM log_records ORDER BY created_at DESC')

        self.assertEqual(len(result), 2)

        self.assertEqual(result[0]['item'], self.operation_move.item_id)
        self.assertEqual(result[0]['type'], relations.OPERATION.CHANGE_STORAGE.value)
        self.assertEqual(result[0]['data'], {'owner_id': self.operation_move.owner_id,
                                             'old_storage_id': 1,
                                             'new_storage_id': 5,
                                             'operation_type': '#test'})

        self.assertEqual(result[1]['type'], relations.OPERATION.CREATE.value)


class ApplyTests(helpers.BaseTests):

    def setUp(self):
        super().setUp()

        self.item_1_id = uuid.uuid4()
        self.item_2_id = uuid.uuid4()
        self.item_3_id = uuid.uuid4()

        self.operation = objects.OperationCreate(owner_id=3,
                                                 item_id=self.item_3_id,
                                                 storage_id=1,
                                                 data=None,
                                                 base_type='base-type',
                                                 full_type='full-type',
                                                 operation_type='#test')

        self.operations = [objects.OperationCreate(owner_id=1,
                                                   item_id=self.item_1_id,
                                                   storage_id=0,
                                                   data=None,
                                                   operation_type='#test',
                                                   base_type='base-type',
                                                   full_type='full-type'),
                           objects.OperationCreate(owner_id=2,
                                                   item_id=self.item_2_id,
                                                   storage_id=0,
                                                   data=None,
                                                   operation_type='#test',
                                                   base_type='base-type',
                                                   full_type='full-type'),
                           objects.OperationDestroy(owner_id=2,
                                                    item_id=self.item_2_id,
                                                    operation_type='#test'),
                           self.operation,
                           objects.OperationChangeOwner(item_id=self.item_1_id,
                                                        old_owner_id=1,
                                                        new_owner_id=3,
                                                        new_storage_id=4,
                                                        operation_type='#test'),
                           objects.OperationChangeStorage(item_id=self.item_1_id,
                                                          owner_id=3,
                                                          old_storage_id=4,
                                                          new_storage_id=1,
                                                          operation_type='#test'),
                           objects.OperationDestroy(owner_id=3,
                                                    item_id=self.item_3_id,
                                                    operation_type='#test')]

    @test_utils.unittest_run_loop
    async def test_success(self):

        await operations.apply(self.operations)

        result = await db.sql('SELECT * FROM items ORDER BY updated_at DESC')

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], self.item_1_id)
        self.assertEqual(result[0]['owner'], 3)

        result = await db.sql('SELECT * FROM log_records ORDER BY created_at ASC')

        self.assertEqual([(row['item'], row['type'], row['data']) for row in result],
                         [(self.item_1_id, relations.OPERATION.CREATE.value, {'operation_type': '#test',
                                                                              'owner_id': 1,
                                                                              'storage_id': 0,
                                                                              'item': None,
                                                                              'base_type': 'base-type',
                                                                              'full_type': 'full-type'}),
                          (self.item_2_id, relations.OPERATION.CREATE.value, {'owner_id': 2,
                                                                              'storage_id': 0,
                                                                              'operation_type':
                                                                              '#test',
                                                                              'item': None,
                                                                              'base_type': 'base-type',
                                                                              'full_type': 'full-type'}),
                          (self.item_2_id, relations.OPERATION.DESTROY.value, {'owner_id': 2, 'operation_type': '#test'}),
                          (self.item_3_id, relations.OPERATION.CREATE.value, {'item': None,
                                                                              'operation_type': '#test',
                                                                              'owner_id': 3,
                                                                              'storage_id': 1,
                                                                              'base_type': 'base-type',
                                                                              'full_type': 'full-type'}),
                          (self.item_1_id, relations.OPERATION.CHANGE_OWNER.value, {'operation_type': '#test', 'old_owner_id': 1, 'new_owner_id': 3, 'new_storage_id': 4}),
                          (self.item_1_id, relations.OPERATION.CHANGE_STORAGE.value, {'operation_type': '#test', 'owner_id': 3, 'old_storage_id': 4, 'new_storage_id': 1}),
                          (self.item_3_id, relations.OPERATION.DESTROY.value, {'operation_type': '#test', 'owner_id': 3})])


        self.assertEqual(len(set([row['transaction'] for row in result])), 1)

    @test_utils.unittest_run_loop
    async def test_rollback(self):

        await operations.apply_create(db.sql, uuid.uuid4(), self.operation)

        with self.assertRaises(exceptions.OperationsError):
            await operations.apply(self.operations)

        result = await db.sql('SELECT * FROM items ORDER BY updated_at DESC')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['id'], self.operation.item_id)
        self.assertEqual(result[0]['owner'], 3)

        result = await db.sql('SELECT * FROM log_records ORDER BY created_at DESC')

        self.assertEqual(result[0]['item'], self.operation.item_id)
        self.assertEqual(result[0]['type'], relations.OPERATION.CREATE.value)


class LoadItemsTests(helpers.BaseTests):

    def setUp(self):
        super().setUp()

        self.item_1_id = uuid.uuid4()
        self.item_2_id = uuid.uuid4()
        self.item_3_id = uuid.uuid4()

        self.operations = [objects.OperationCreate(owner_id=1,
                                                   item_id=self.item_1_id,
                                                   storage_id=0,
                                                   data={'a': 1},
                                                   operation_type='#test',
                                                   base_type='base-type',
                                                   full_type='full-type'),
                           objects.OperationCreate(owner_id=2,
                                                   item_id=self.item_2_id,
                                                   storage_id=1,
                                                   data={'b': 2},
                                                   operation_type='#test',
                                                   base_type='base-type',
                                                   full_type='full-type'),
                           objects.OperationCreate(owner_id=3,
                                                   item_id=self.item_3_id,
                                                   storage_id=0,
                                                   data={'c': 3},
                                                   operation_type='#test',
                                                   base_type='base-type',
                                                   full_type='full-type'),
                           objects.OperationChangeOwner(item_id=self.item_1_id,
                                                        old_owner_id=1,
                                                        new_owner_id=3,
                                                        new_storage_id=1,
                                                        operation_type='#test')]

    @test_utils.unittest_run_loop
    async def test_no_items(self):

        await operations.apply(self.operations)

        items = await operations.load_items(1)

        self.assertEqual(items, [])

    @test_utils.unittest_run_loop
    async def test_has_items(self):

        await operations.apply(self.operations)

        items = await operations.load_items(3)

        self.assertCountEqual(items, [objects.Item(id=self.item_1_id, owner_id=3, storage_id=1, data={'a': 1}),
                                      objects.Item(id=self.item_3_id, owner_id=3, storage_id=0, data={'c': 3})])


class HasItemsTests(helpers.BaseTests):

    def setUp(self):
        super().setUp()

        self.item_1_id = uuid.uuid4()
        self.item_2_id = uuid.uuid4()
        self.item_3_id = uuid.uuid4()

        self.operations = [objects.OperationCreate(owner_id=1,
                                                   item_id=self.item_1_id,
                                                   storage_id=0,
                                                   data={'a': 1},
                                                   operation_type='#test',
                                                   base_type='base-type',
                                                   full_type='full-type'),
                           objects.OperationCreate(owner_id=2,
                                                   item_id=self.item_2_id,
                                                   storage_id=1,
                                                   data={'b': 2},
                                                   operation_type='#test',
                                                   base_type='base-type',
                                                   full_type='full-type'),
                           objects.OperationCreate(owner_id=3,
                                                   item_id=self.item_3_id,
                                                   storage_id=0,
                                                   data={'c': 3},
                                                   operation_type='#test',
                                                   base_type='base-type',
                                                   full_type='full-type'),
                           objects.OperationChangeOwner(item_id=self.item_1_id,
                                                        old_owner_id=1,
                                                        new_owner_id=3,
                                                        new_storage_id=0,
                                                        operation_type='#test')]

    @test_utils.unittest_run_loop
    async def test_no_items(self):
        await operations.apply(self.operations)

        has = await operations.has_items(3, items_ids=[])

        self.assertTrue(has)

    @test_utils.unittest_run_loop
    async def test_no_items_found(self):
        await operations.apply(self.operations)

        has = await operations.has_items(3, items_ids=[uuid.uuid4()])

        self.assertFalse(has)

    @test_utils.unittest_run_loop
    async def test_wrong_owner(self):
        await operations.apply(self.operations)

        has = await operations.has_items(3, items_ids=[self.item_2_id])

        self.assertFalse(has)

    @test_utils.unittest_run_loop
    async def test_has(self):
        await operations.apply(self.operations)

        has = await operations.has_items(2, items_ids=[self.item_2_id])

        self.assertTrue(has)

    @test_utils.unittest_run_loop
    async def test_has_multiple(self):
        await operations.apply(self.operations)

        has = await operations.has_items(3, items_ids=[self.item_1_id, self.item_3_id])

        self.assertTrue(has)


    @test_utils.unittest_run_loop
    async def test_not_all(self):
        await operations.apply(self.operations)

        has = await operations.has_items(3, items_ids=[self.item_1_id, self.item_3_id, self.item_2_id])

        self.assertFalse(has)


class GetItemLogsTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_logs(self):
        log = await operations.get_item_logs(item_id=uuid.uuid4())
        self.assertEqual(log, [])

    @test_utils.unittest_run_loop
    async def test_has_logs(self):

        transactions = [uuid.uuid4(), uuid.uuid4(), uuid.uuid4()]
        items = [uuid.uuid4(), uuid.uuid4(), uuid.uuid4()]

        await operations.log(db.sql,
                             transaction_id=transactions[0],
                             item_id=items[0],
                             data={'a': 1},
                             type=relations.OPERATION.CREATE)

        await operations.log(db.sql,
                             transaction_id=transactions[0],
                             item_id=items[1],
                             data={'a': 2},
                             type=relations.OPERATION.DESTROY)

        await operations.log(db.sql,
                             transaction_id=transactions[1],
                             item_id=items[0],
                             data={'a': 3},
                             type=relations.OPERATION.CHANGE_OWNER)

        await operations.log(db.sql,
                             transaction_id=transactions[2],
                             item_id=items[2],
                             data={'a': 4},
                             type=relations.OPERATION.CHANGE_STORAGE)

        await operations.log(db.sql,
                             transaction_id=transactions[2],
                             item_id=items[0],
                             data={'a': 5},
                             type=relations.OPERATION.CHANGE_STORAGE)

        log = await operations.get_item_logs(item_id=items[0])

        self.assertEqual([record.data['a'] for record in log],
                         [1, 3, 5])

    @test_utils.unittest_run_loop
    async def test_load_fields(self):

        transaction = uuid.uuid4()
        item_id = uuid.uuid4()

        await operations.log(db.sql,
                             transaction_id=transaction,
                             item_id=item_id,
                             data={'a': 1},
                             type=relations.OPERATION.CREATE)

        log = await operations.get_item_logs(item_id=item_id)

        self.assertEqual(log[0].transaction, transaction)
        self.assertEqual(log[0].item_id, item_id)
        self.assertEqual(log[0].type, relations.OPERATION.CREATE)
        self.assertEqual(log[0].data, {'a': 1})
