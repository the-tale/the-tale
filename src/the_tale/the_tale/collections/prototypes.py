# coding: utf-8

from the_tale.common.utils.prototypes import BasePrototype
from the_tale.common.utils.decorators import lazy_property
from the_tale.common.utils import bbcode

from the_tale.accounts.prototypes import AccountPrototype

from the_tale.collections.models import Collection, Kit, Item, AccountItems, GiveItemTask
from the_tale.collections.container import ItemsContainer
from the_tale.collections import exceptions


class CollectionPrototype(BasePrototype):
    _model_class = Collection
    _readonly = ('id', 'created_at', 'updated_at')
    _bidirectional = ('caption', 'description', 'approved', )
    _get_by = ('id', )

    CAPTION_MAX_LENGTH = Collection.CAPTION_MAX_LENGTH
    DESCRIPTION_MAX_LENGTH = Collection.DESCRIPTION_MAX_LENGTH

    @classmethod
    def approved_collections(cls):
        return cls.from_query(cls._db_filter(approved=True))

    @classmethod
    def all_collections(cls):
        return cls._db_all()

    @property
    def description_html(self): return bbcode.render(self.description)

    @classmethod
    def create(cls, caption, description, approved=False):
        from the_tale.collections.storage import collections_storage

        model = cls._model_class.objects.create(caption=caption,
                                                description=description,
                                                approved=approved)

        prototype = cls(model=model)

        collections_storage.add_item(prototype.id, prototype)
        collections_storage.update_version()

        return prototype

    def save(self):
        from the_tale.collections.storage import collections_storage

        if id(self) != id(collections_storage[self.id]):
            raise exceptions.SaveNotRegisteredCollectionError(collection=self)

        super(CollectionPrototype, self).save()

        collections_storage.update_version()


class KitPrototype(BasePrototype):
    _model_class = Kit
    _readonly = ('id', 'created_at', 'updated_at')
    _bidirectional = ('approved', 'caption', 'description', 'collection_id')
    _get_by = ('id', 'collection_id')

    CAPTION_MAX_LENGTH = Kit.CAPTION_MAX_LENGTH
    DESCRIPTION_MAX_LENGTH = Kit.DESCRIPTION_MAX_LENGTH

    @classmethod
    def approved_kits(cls):
        return cls.from_query(cls._db_filter(approved=True).order_by('caption'))

    @classmethod
    def all_kits(cls):
        return cls._db_all()

    @property
    def description_html(self): return bbcode.render(self.description)

    @property
    def collection(self):
        from the_tale.collections.storage import collections_storage
        return collections_storage[self.collection_id]

    @classmethod
    def create(cls, collection, caption, description, approved=False):
        from the_tale.collections.storage import kits_storage

        model = cls._model_class.objects.create(collection=collection._model,
                                                caption=caption,
                                                description=description,
                                                approved=approved)

        prototype = cls(model=model)

        kits_storage.add_item(prototype.id, prototype)
        kits_storage.update_version()

        return prototype

    def save(self):
        from the_tale.collections.storage import kits_storage

        if id(self) != id(kits_storage[self.id]):
            raise exceptions.SaveNotRegisteredKitError(kit=self)

        super(KitPrototype, self).save()

        kits_storage.update_version()




class ItemPrototype(BasePrototype):
    _model_class = Item
    _readonly = ('id', 'created_at', 'updated_at')
    _bidirectional = ('approved',  'caption', 'text', 'kit_id')
    _get_by = ('id', 'kit_id')

    CAPTION_MAX_LENGTH = Item.CAPTION_MAX_LENGTH

    @property
    def kit(self):
        from the_tale.collections.storage import kits_storage
        return kits_storage[self.kit_id]

    @property
    def text_html(self): return bbcode.render(self.text)

    @classmethod
    def create(cls, kit, caption, text, approved=False):
        from the_tale.collections.storage import items_storage

        model = cls._model_class.objects.create(kit=kit._model,
                                                caption=caption,
                                                text=text,
                                                approved=approved)

        prototype = cls(model=model)

        items_storage.add_item(prototype.id, prototype)
        items_storage.update_version()

        return prototype

    def save(self):
        from the_tale.collections.storage import items_storage

        if id(self) != id(items_storage[self.id]):
            raise exceptions.SaveNotRegisteredItemError(item=self)

        super(ItemPrototype, self).save()

        items_storage.update_version()



class AccountItemsPrototype(BasePrototype):
    _model_class = AccountItems
    _readonly = ('id', 'account_id')
    _bidirectional = ()
    _get_by = ('id', 'account_id')
    _serialization_proxies = (('items', ItemsContainer, None),)

    @lazy_property
    def account(self): return AccountPrototype(model=self._model.account)

    @classmethod
    def create(cls, account):
        return cls(model=cls._db_create(account=account._model))

    @classmethod
    def give_item(cls, account_id, item):
        if not item.approved:
            return
        GiveItemTaskPrototype.create(account_id=account_id, item_id=item.id)

    def add_item(self, item, notify=False):
        self.items.add_item(item)

    def has_item(self, item):
        return self.items.has_item(item)

    def timestamp_for(self, achievement):
        return self.achievements.timestamp_for(achievement)

    def items_ids(self): return self.items.items_ids()

    def last_items(self, number): return self.items.last_items(number=number)

    def get_items_count(self):
        return self.items.approved_items_count()


class GiveItemTaskPrototype(BasePrototype):
    _model_class = GiveItemTask
    _readonly = ('id', 'account_id', 'item_id')
    _bidirectional = ()
    _get_by = ()

    @classmethod
    def create(cls, account_id, item_id):
        return cls(model=cls._db_create(account_id=account_id,
                                        item_id=item_id))

    def remove(self):
        self._model.delete()
