
import uuid

import psycopg2
from psycopg2.extras import Json as PGJson

from tt_web import postgresql as db

from . import objects
from . import exceptions


async def log(execute, transaction_id, item_id, data, type):
    await execute('''INSERT INTO log_records (transaction, item, data, type, created_at)
                     VALUES (%(transaction_id)s, %(item_id)s, %(data)s, %(type)s, NOW())''',
                  {'transaction_id': transaction_id,
                   'item_id': item_id,
                   'type': type.value,
                   'data': PGJson(data)})


async def apply(operations):
    await db.transaction(_apply, {'operations': operations})


async def _apply(execute, arguments):
    transaction_id = uuid.uuid4()

    for operation in arguments['operations']:
        await OPERATIONS[operation.__class__](execute, transaction_id, operation)


async def apply_create(execute, transaction_id, operation):
    try:
        await execute('''INSERT INTO items (id, owner, storage, data, base_type, full_type, created_at, updated_at)
                         VALUES (%(id)s, %(owner)s, %(storage)s, %(data)s, %(base_type)s, %(full_type)s, NOW(), NOW())''',
                      {'id': operation.item_id,
                       'owner': operation.owner_id,
                       'storage': operation.storage_id,
                       'data': PGJson(operation.data),
                       'base_type': operation.base_type,
                       'full_type': operation.full_type})
    except psycopg2.IntegrityError:
        raise exceptions.ItemAlreadyCreated(item_id=operation.item_id,
                                            owner_id=operation.owner_id)

    await log(execute,
              transaction_id=transaction_id,
              item_id=operation.item_id,
              type=operation.TYPE,
              data={'item': operation.data,
                    'base_type': operation.base_type,
                    'full_type': operation.full_type,
                    'owner_id': operation.owner_id,
                    'storage_id': operation.storage_id,
                    'operation_type': operation.operation_type})


async def apply_destroy(execute, transaction_id, operation):
    result = await execute('DELETE FROM items WHERE id=%(id)s AND owner=%(owner)s RETURNING id',
                           {'id': operation.item_id, 'owner': operation.owner_id})

    if not result:
        raise exceptions.CanNotDeleteItem(item_id=operation.item_id,
                                          owner_id=operation.owner_id)

    await log(execute,
              transaction_id=transaction_id,
              item_id=operation.item_id,
              type=operation.TYPE,
              data={'owner_id': operation.owner_id,
                    'operation_type': operation.operation_type})


async def apply_change_owner(execute, transaction_id, operation):

    if operation.old_owner_id == operation.new_owner_id:
        raise exceptions.CanNotChangeItemOwnerSameOwner(item_id=operation.item_id, owner_id=operation.old_owner_id)

    result = await execute('UPDATE items SET owner=%(new_owner)s, storage=%(new_storage)s WHERE id=%(id)s AND owner=%(old_owner)s RETURNING id',
                           {'id': operation.item_id, 'old_owner': operation.old_owner_id, 'new_owner': operation.new_owner_id, 'new_storage': operation.new_storage_id})

    if not result:
        raise exceptions.CanNotChangeItemOwner(item_id=operation.item_id,
                                               old_owner_id=operation.old_owner_id,
                                               new_owner_id=operation.new_owner_id)


    await log(execute,
              transaction_id=transaction_id,
              item_id=operation.item_id,
              type=operation.TYPE,
              data={'old_owner_id': operation.old_owner_id,
                    'new_owner_id': operation.new_owner_id,
                    'new_storage_id': operation.new_storage_id,
                    'operation_type': operation.operation_type})


async def apply_change_storage(execute, transaction_id, operation):

    result = await execute('UPDATE items SET storage=%(new_storage)s WHERE id=%(id)s AND owner=%(owner)s AND storage=%(old_storage)s RETURNING id',
                           {'id': operation.item_id, 'owner': operation.owner_id, 'old_storage': operation.old_storage_id, 'new_storage': operation.new_storage_id})

    if not result:
        result = await execute('SELECT 1 FROM items WHERE id=%(id)s AND owner=%(owner)s AND storage=%(new_storage)s',
                               {'id': operation.item_id, 'owner': operation.owner_id, 'new_storage': operation.new_storage_id})
        if result:
            return

        raise exceptions.CanNotChangeItemStorage(item_id=operation.item_id,
                                                 old_storage_id=operation.old_storage_id,
                                                 new_storage_id=operation.new_storage_id)


    await log(execute,
              transaction_id=transaction_id,
              item_id=operation.item_id,
              type=operation.TYPE,
              data={'owner_id': operation.owner_id,
                    'old_storage_id': operation.old_storage_id,
                    'new_storage_id': operation.new_storage_id,
                    'operation_type': operation.operation_type})



async def load_items(owner_id):
    result = await db.sql('SELECT id, owner, storage, data FROM items WHERE owner=%(owner)s', {'owner': owner_id})
    return [objects.Item(id=row['id'], owner_id=owner_id, storage_id=row['storage'], data=row['data']) for row in result]


async def has_items(owner_id, items_ids):
    result = await db.sql('SELECT 1 FROM items WHERE owner=%(owner)s AND id = ANY (%(items_ids)s)',
                          {'owner': owner_id, 'items_ids': items_ids})
    return len(result) == len(items_ids)



async def clean_database():
    await db.sql('DELETE FROM log_records')
    await db.sql('DELETE FROM items')


OPERATIONS = {objects.OperationCreate: apply_create,
              objects.OperationDestroy: apply_destroy,
              objects.OperationChangeOwner: apply_change_owner,
              objects.OperationChangeStorage: apply_change_storage}
