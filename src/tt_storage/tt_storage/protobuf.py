
from tt_protocol.protocol import storage_pb2

from tt_web import s11n

from . import objects
from . import exceptions


def to_operation(pb_operation):
    if pb_operation.HasField('create'):
        return _to_operation_create(pb_operation.create)

    if pb_operation.HasField('destroy'):
        return _to_operation_destroy(pb_operation.destroy)

    if pb_operation.HasField('change_owner'):
        return _to_operation_change_owner(pb_operation.change_owner)

    if pb_operation.HasField('change_storage'):
        return _to_operation_change_storage(pb_operation.change_storage)

    raise exceptions.UnknownOperationTypeInProtobuf(type=pb_operation.WhichOneof('operation'))


def _to_operation_create(pb_operation):
    return objects.OperationCreate(owner_id=pb_operation.owner_id,
                                   item_id=pb_operation.item_id,
                                   data=s11n.from_json(pb_operation.data),
                                   base_type=pb_operation.base_type,
                                   full_type=pb_operation.full_type,
                                   operation_type=pb_operation.operation_type,
                                   storage_id=pb_operation.storage_id)


def _to_operation_destroy(pb_operation):
    return objects.OperationDestroy(item_id=pb_operation.item_id,
                                    owner_id=pb_operation.owner_id,
                                    operation_type=pb_operation.operation_type)


def _to_operation_change_owner(pb_operation):
    return objects.OperationChangeOwner(item_id=pb_operation.item_id,
                                        old_owner_id=pb_operation.old_owner_id,
                                        new_owner_id=pb_operation.new_owner_id,
                                        operation_type=pb_operation.operation_type,
                                        new_storage_id=pb_operation.new_storage_id)


def _to_operation_change_storage(pb_operation):
    return objects.OperationChangeStorage(item_id=pb_operation.item_id,
                                          owner_id=pb_operation.owner_id,
                                          old_storage_id=pb_operation.old_storage_id,
                                          new_storage_id=pb_operation.new_storage_id,
                                          operation_type=pb_operation.operation_type)


def from_item(item):
    return storage_pb2.Item(id=item.id.hex,
                            owner_id=item.owner_id,
                            storage_id=item.storage_id,
                            data=s11n.to_json(item.data))
