# coding: utf-8


from the_tale.common.utils import storage

from the_tale.collections.prototypes import CollectionPrototype, KitPrototype, ItemPrototype
from the_tale.collections import exceptions


class CollectionsStorage(storage.Storage):
    SETTINGS_KEY = 'collections change time'
    EXCEPTION = exceptions.CollectionsError
    PROTOTYPE = CollectionPrototype

    def get_form_choices(self):
        return [('', '----')] +  [(c.id, c.caption) for c in self.all()]


class KitsStorage(storage.Storage):
    SETTINGS_KEY = 'kits change time'
    EXCEPTION = exceptions.CollectionsError
    PROTOTYPE = KitPrototype

    def get_form_choices(self):
        return [('', '----')] +  [(k.id, k.caption) for k in self.all()]


class ItemsStorage(storage.Storage):
    SETTINGS_KEY = 'items change time'
    EXCEPTION = exceptions.CollectionsError
    PROTOTYPE = ItemPrototype

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
