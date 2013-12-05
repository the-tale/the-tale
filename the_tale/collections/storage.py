# coding: utf-8


from the_tale.common.utils.storage import create_storage_class

from the_tale.collections.prototypes import CollectionPrototype, KitPrototype, ItemPrototype
from the_tale.collections import exceptions


class CollectionsStorage(create_storage_class('collections change time', CollectionPrototype, exceptions.CollectionsError)):
    pass

class KitsStorage(create_storage_class('kits change time', KitPrototype, exceptions.CollectionsError)):
    pass

class ItemsStorage(create_storage_class('items change time', ItemPrototype, exceptions.CollectionsError)):
    pass


collections_storage = CollectionsStorage()
kits_storage = KitsStorage()
items_storage = ItemsStorage()
