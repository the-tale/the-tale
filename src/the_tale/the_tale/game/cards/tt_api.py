import uuid

from django.conf import settings as project_settings

from dext.common.utils.urls import url
from dext.common.utils import s11n

from tt_protocol.protocol import storage_pb2

from the_tale.common.utils import tt_api

from the_tale.game.cards import effects
from the_tale.game.cards import conf

from . import objects


def change_cards(account_id, operation_type, to_add=(), to_remove=()):
    operations = []

    for card in to_remove:
        operations.append(storage_pb2.Operation(destroy=storage_pb2.OperationDestroy(item_id=card.uid.hex,
                                                                                     owner_id=account_id,
                                                                                     operation_type=operation_type)))

    for card in to_add:
        operations.append(storage_pb2.Operation(create=storage_pb2.OperationCreate(item_id=card.uid.hex,
                                                                                   owner_id=account_id,
                                                                                   storage_id=conf.FAST_STORAGE,
                                                                                   base_type=card.item_base_type,
                                                                                   full_type=card.item_full_type,
                                                                                   data=s11n.to_json(card.serialize()),
                                                                                   operation_type=operation_type)))

    tt_api.sync_request(url=conf.settings.TT_APPLY_URL,
                        data=storage_pb2.ApplyRequest(operations=operations),
                        AnswerType=storage_pb2.ApplyResponse)


def change_cards_owner(old_owner_id, new_owner_id, operation_type, new_storage_id, cards_ids):
    operations = []

    for card_id in cards_ids:
        operations.append(storage_pb2.Operation(change_owner=storage_pb2.OperationChangeOwner(item_id=card_id.hex,
                                                                                              old_owner_id=old_owner_id,
                                                                                              new_owner_id=new_owner_id,
                                                                                              new_storage_id=new_storage_id,
                                                                                              operation_type=operation_type)))

    tt_api.sync_request(url=conf.settings.TT_APPLY_URL,
                        data=storage_pb2.ApplyRequest(operations=operations),
                        AnswerType=storage_pb2.ApplyResponse)



def change_cards_storage(account_id, operation_type, cards, old_storage_id, new_storage_id):
    operations = []

    for card in cards:
        operations.append(storage_pb2.Operation(change_storage=storage_pb2.OperationChangeStorage(item_id=card.uid.hex,
                                                                                                  owner_id=account_id,
                                                                                                  old_storage_id=old_storage_id,
                                                                                                  new_storage_id=new_storage_id,
                                                                                                  operation_type=operation_type)))

    tt_api.sync_request(url=conf.settings.TT_APPLY_URL,
                        data=storage_pb2.ApplyRequest(operations=operations),
                        AnswerType=storage_pb2.ApplyResponse)



def load_cards(account_id):
    answer = tt_api.sync_request(url=conf.settings.TT_GET_ITEMS_URL,
                                 data=storage_pb2.GetItemsRequest(owner_id=account_id),
                                 AnswerType=storage_pb2.GetItemsResponse)

    cards = {}

    for item in answer.items:
        id = uuid.UUID(item.id)
        cards[id] = objects.Card.deserialize(uid=id,
                                             data=s11n.from_json(item.data),
                                             in_storage=(item.storage_id==conf.ARCHIVE_STORAGE))

    return cards


def has_cards(account_id, cards_ids):
    answer = tt_api.sync_request(url=conf.settings.TT_HAS_ITEMS_URL,
                                 data=storage_pb2.HasItemsRequest(owner_id=account_id, items_ids=[id.hex for id in cards_ids]),
                                 AnswerType=storage_pb2.HasItemsResponse)
    return answer.has


def debug_clear_service():
    if project_settings.TESTS_RUNNING:
        tt_api.sync_request(url=conf.settings.TT_DEBUG_CLEAR_SERVICE_URL,
                            data=storage_pb2.DebugClearServiceRequest(),
                            AnswerType=storage_pb2.DebugClearServiceResponse)
