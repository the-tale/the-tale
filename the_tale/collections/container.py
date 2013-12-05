# coding: utf-8

import time


class ItemsContainer(object):

    __slots__ = ('updated', 'items')

    def __init__(self):
        self.updated = False
        self.items = {}

    def serialize(self):
        return {'items': self.items.items()}

    @classmethod
    def deserialize(cls, prototype, data):
        obj = cls()
        obj.items = dict(data.get('items', ()))
        return obj

    def add_item(self, item):

        if item.id in self.items:
            return

        self.updated = True
        self.items[item.id] = time.time()

    def has_item(self, item):
        return item.id in self.items

    def timestamp_for(self, item):
        return self.items.get(item.id)

    def items_ids(self): return self.items.iterkeys()

    def __len__(self):
         return len(self.items)

    def approved_items_count(self):
        from the_tale.collections.storage import items_storage
        return len([item_id for item_id in self.items.itervalues() if items_storage[item_id].approved])

    def last_items(self, number):
        from the_tale.collections.storage import items_storage

        items_ids = zip(*sorted((-item_time, item_id)
                                for item_id, item_time in self.items.iteritems()))

        if items_ids:
            items_ids = items_ids[1]

        MAXIMUM_UNAPPROVED_ITEMS = 5

        candidates = {item_id:items_storage[item_id] for item_id in items_ids[:number+MAXIMUM_UNAPPROVED_ITEMS] if items_storage[item_id].approved}

        result = []

        for item_id in items_ids:
            if item_id in candidates:
                result.append(candidates[item_id])
            if len(result) == number:
                break

        return result
