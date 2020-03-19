
import smart_imports

smart_imports.all()


class CollectionPrototype(utils_prototypes.BasePrototype):
    _model_class = models.Collection
    _readonly = ('id', 'created_at', 'updated_at')
    _bidirectional = ('caption', 'description', 'approved', )
    _get_by = ('id', )

    CAPTION_MAX_LENGTH = models.Collection.CAPTION_MAX_LENGTH
    DESCRIPTION_MAX_LENGTH = models.Collection.DESCRIPTION_MAX_LENGTH

    @classmethod
    def approved_collections(cls):
        return cls.from_query(cls._db_filter(approved=True))

    @classmethod
    def all_collections(cls):
        return cls._db_all()

    @property
    def description_html(self): return bbcode_renderers.default.render(self.description)

    @classmethod
    def create(cls, caption, description, approved=False):
        from . import storage

        model = cls._model_class.objects.create(caption=caption,
                                                description=description,
                                                approved=approved)

        prototype = cls(model=model)

        storage.collections.add_item(prototype.id, prototype)
        storage.collections.update_version()

        return prototype

    def save(self):
        from . import storage

        if id(self) != id(storage.collections[self.id]):
            raise exceptions.SaveNotRegisteredCollectionError(collection=self)

        super(CollectionPrototype, self).save()

        storage.collections.update_version()


class KitPrototype(utils_prototypes.BasePrototype):
    _model_class = models.Kit
    _readonly = ('id', 'created_at', 'updated_at')
    _bidirectional = ('approved', 'caption', 'description', 'collection_id')
    _get_by = ('id', 'collection_id')

    CAPTION_MAX_LENGTH = models.Kit.CAPTION_MAX_LENGTH
    DESCRIPTION_MAX_LENGTH = models.Kit.DESCRIPTION_MAX_LENGTH

    @classmethod
    def approved_kits(cls):
        return cls.from_query(cls._db_filter(approved=True).order_by('caption'))

    @classmethod
    def all_kits(cls):
        return cls._db_all()

    @property
    def description_html(self): return bbcode_renderers.default.render(self.description)

    @property
    def collection(self):
        from . import storage

        return storage.collections[self.collection_id]

    @classmethod
    def create(cls, collection, caption, description, approved=False):
        from . import storage

        model = cls._model_class.objects.create(collection=collection._model,
                                                caption=caption,
                                                description=description,
                                                approved=approved)

        prototype = cls(model=model)

        storage.kits.add_item(prototype.id, prototype)
        storage.kits.update_version()

        return prototype

    def save(self):
        from . import storage

        if id(self) != id(storage.kits[self.id]):
            raise exceptions.SaveNotRegisteredKitError(kit=self)

        super(KitPrototype, self).save()

        storage.kits.update_version()


class ItemPrototype(utils_prototypes.BasePrototype):
    _model_class = models.Item
    _readonly = ('id', 'created_at', 'updated_at')
    _bidirectional = ('approved', 'caption', 'text', 'kit_id')
    _get_by = ('id', 'kit_id')

    CAPTION_MAX_LENGTH = models.Item.CAPTION_MAX_LENGTH

    @property
    def kit(self):
        from . import storage

        return storage.kits[self.kit_id]

    @property
    def text_html(self): return bbcode_renderers.default.render(self.text)

    @classmethod
    def create(cls, kit, caption, text, approved=False):
        from . import storage

        model = cls._model_class.objects.create(kit=kit._model,
                                                caption=caption,
                                                text=text,
                                                approved=approved)

        prototype = cls(model=model)

        storage.items.add_item(prototype.id, prototype)
        storage.items.update_version()

        return prototype

    def save(self):
        from . import storage

        if id(self) != id(storage.items[self.id]):
            raise exceptions.SaveNotRegisteredItemError(item=self)

        super(ItemPrototype, self).save()

        storage.items.update_version()


class AccountItemsPrototype(utils_prototypes.BasePrototype):
    _model_class = models.AccountItems
    _readonly = ('id', 'account_id')
    _bidirectional = ()
    _get_by = ('id', 'account_id')
    _serialization_proxies = (('items', container.ItemsContainer, None),)

    @utils_decorators.lazy_property
    def account(self): return accounts_prototypes.AccountPrototype(model=self._model.account)

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


class GiveItemTaskPrototype(utils_prototypes.BasePrototype):
    _model_class = models.GiveItemTask
    _readonly = ('id', 'account_id', 'item_id')
    _bidirectional = ()
    _get_by = ()

    @classmethod
    def create(cls, account_id, item_id):
        return cls(model=cls._db_create(account_id=account_id,
                                        item_id=item_id))

    def remove(self):
        self._model.delete()
