
from . import relations


class Item:
    __slots__ = ('id', 'owner_id', 'storage_id', 'data')

    def __init__(self, id, owner_id, storage_id, data):
        self.id = id
        self.owner_id = owner_id
        self.storage_id = storage_id
        self.data = data

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.id == other.id and
                self.owner_id == other.owner_id and
                self.storage_id == other.storage_id and
                self.data == other.data)

    def __ne__(self, other):
        return not self.__eq__(other)


class Operation:
    __slots__ = ('operation_type', )
    TYPE = NotImplemented

    def __init__(self, operation_type):
        self.operation_type = operation_type


class OperationCreate(Operation):
    __slots__ = ('owner_id', 'item_id', 'storage_id', 'data', 'base_type', 'full_type')

    TYPE = relations.OPERATION.CREATE

    def __init__(self, owner_id, item_id, storage_id, data, base_type, full_type, **kwargs):
        super().__init__(**kwargs)
        self.owner_id = owner_id
        self.item_id = item_id
        self.storage_id = storage_id
        self.data = data
        self.base_type = base_type
        self.full_type = full_type


class OperationDestroy(Operation):
    __slots__ = ('item_id', 'owner_id')

    TYPE = relations.OPERATION.DESTROY

    def __init__(self, item_id, owner_id, **kwargs):
        super().__init__(**kwargs)
        self.item_id = item_id
        self.owner_id = owner_id


class OperationChangeOwner(Operation):
    __slots__ = ('item_id', 'old_owner_id', 'new_owner_id', 'new_storage_id')

    TYPE = relations.OPERATION.CHANGE_OWNER

    def __init__(self, item_id, old_owner_id, new_owner_id, new_storage_id, **kwargs):
        super().__init__(**kwargs)
        self.item_id = item_id
        self.old_owner_id = old_owner_id
        self.new_owner_id = new_owner_id
        self.new_storage_id = new_storage_id


class OperationChangeStorage(Operation):
    __slots__ = ('item_id', 'owner_id', 'old_storage_id', 'new_storage_id')

    TYPE = relations.OPERATION.CHANGE_STORAGE

    def __init__(self, item_id, owner_id, old_storage_id, new_storage_id, **kwargs):
        super().__init__(**kwargs)
        self.item_id = item_id
        self.owner_id = owner_id
        self.old_storage_id = old_storage_id
        self.new_storage_id = new_storage_id


class LogRecord:
    __slots__ = ('id', 'transaction', 'item_id', 'type', 'data', 'created_at')

    def __init__(self, id, transaction, item_id, type, data, created_at):
        self.id = id
        self.transaction = transaction
        self.item_id = item_id
        self.type = type
        self.data = data
        self.created_at = created_at

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                all(getattr(self, name) == getattr(other, name) for name in self.__slots__))

    def __ne__(self, other):
        return not self.__eq__(other)
