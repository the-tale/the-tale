# coding: utf-8


from the_tale.common.utils.storage import create_storage_class

from the_tale.collections.prototypes import CollectionPrototype, KitPrototype, ItemPrototype
from the_tale.collections import exceptions


class CollectionsStorage(create_storage_class('collections change time', CollectionPrototype, exceptions.CollectionsError)):
    pass

class KitsStorage(create_storage_class('kits change time', KitPrototype, exceptions.CollectionsError)):
    pass

class ItemsStorage(create_storage_class('items change time', ItemPrototype, exceptions.CollectionsError)):

    def form_choices(self):
        self.sync()

        choices = []

        for kit in kits_storage.all():
            items = []

            for item in self.all():
                if item.kit_id == kit.id:
                    items.append((item.id, item.caption))

            choices.append((kit.caption, sorted(items, key=lambda record: record[1])))

        return sorted(choices)


collections_storage = CollectionsStorage()
kits_storage = KitsStorage()
items_storage = ItemsStorage()
