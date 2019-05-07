
import smart_imports

smart_imports.all()


class StorageClient(tt_api_storage.Client):

    def protobuf_to_item(self, pb_item, cards=None):
        if cards is None:
            cards = types.CARD

        id = uuid.UUID(pb_item.id)
        card = objects.Card.deserialize(uid=id,
                                        data=s11n.from_json(pb_item.data),
                                        storage=relations.STORAGE(pb_item.storage_id),
                                        cards=cards)
        return id, card

    def Create(self, owner_id, card, storage):
        return tt_protocol_storage_pb2.OperationCreate(item_id=card.uid.hex,
                                                       owner_id=owner_id,
                                                       storage_id=storage.value,
                                                       base_type=card.item_base_type,
                                                       full_type=card.item_full_type,
                                                       data=s11n.to_json(card.serialize()))

    def Destroy(self, owner_id, card):
        return tt_protocol_storage_pb2.OperationDestroy(item_id=card.uid.hex,
                                                        owner_id=owner_id)

    def ChangeOwner(self, old_owner_id, new_owner_id, card_id, new_storage):
        return tt_protocol_storage_pb2.OperationChangeOwner(item_id=card_id.hex,
                                                            old_owner_id=old_owner_id,
                                                            new_owner_id=new_owner_id,
                                                            new_storage_id=new_storage.value)

    def ChangeStorage(self, owner_id, card, old_storage, new_storage):
        return tt_protocol_storage_pb2.OperationChangeStorage(item_id=card.uid.hex,
                                                              owner_id=owner_id,
                                                              old_storage_id=old_storage.value,
                                                              new_storage_id=new_storage.value)


storage = StorageClient(entry_point=conf.settings.TT_STORAGE_ENTRY_POINT)
