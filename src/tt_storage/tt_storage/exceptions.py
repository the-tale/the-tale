
from tt_web import exceptions


class StorageError(exceptions.BaseError):
    pass


class OperationsError(StorageError):
    pass


class ItemAlreadyCreated(OperationsError):
    MESSAGE = 'can not create item {item_id} for owner {owner_id}'


class CanNotDeleteItem(OperationsError):
    MESSAGE = 'Can not delete item {item_id} from owner {owner_id}'


class CanNotChangeItemOwner(OperationsError):
    MESSAGE = 'Can not change item {item_id} owner from {old_owner_id} to {new_owner_id}'


class CanNotChangeItemOwnerSameOwner(OperationsError):
    MESSAGE = 'Can not change item {item_id} ownwer {owner_id} to same'


class CanNotChangeItemStorage(OperationsError):
    MESSAGE = 'Can not move item {item_id} from storage {old_storage_id} to storage {new_storage_id}'


class UnknownOperationTypeInProtobuf(OperationsError):
    MESSAGE = 'Unknown operation type in protobuf: "{type}"'
