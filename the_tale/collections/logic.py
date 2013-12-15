# coding: utf-8

import collections


from the_tale.collections.storage import items_storage, kits_storage


def get_items_count(items):

    items = (item
             for item in items
             if item.approved and item.kit.approved and item.kit.collection)

    items_in_kits = collections.Counter(item.kit_id for item in items)

    kits_in_collections = [(kit.id, kit.collection_id)
                           for kit in kits_storage.all()
                           if kit.approved and kit.collection.approved]

    items_in_collections = {}

    for kit_id, collection_id in kits_in_collections:
        items_in_collections[collection_id] = items_in_collections.get(collection_id, 0) + items_in_kits[kit_id]

    return items_in_kits, items_in_collections


def get_collections_statistics(account_items):

    statistics = {'total_items_in_collections': {},
                  'total_items_in_kits': {},
                  'account_items_in_collections': {},
                  'account_items_in_kits': {},
                  'total_items': 0,
                  'account_items': 0}

    items_in_kits, items_in_collections = get_items_count(items_storage.all())
    statistics['total_items_in_kits'] = items_in_kits
    statistics['total_items_in_collections'] = items_in_collections
    statistics['total_items'] = sum(items_in_collections.values())

    if account_items:
        items_in_kits, items_in_collections = get_items_count(item for item in items_storage.all() if item.id in account_items.items_ids())
        statistics['account_items_in_kits'] = items_in_kits
        statistics['account_items_in_collections'] = items_in_collections
        statistics['account_items'] = sum(items_in_collections.values())

    return statistics
