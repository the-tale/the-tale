# coding: utf-8

import collections


from the_tale.collections.prototypes import KitPrototype, ItemPrototype


def get_items_count(items_query):
    items_in_kits = collections.Counter(items_query.filter(approved=True, kit__approved=True, kit__collection__approved=True).values_list('kit', flat=True))

    kits_in_collections = KitPrototype._db_filter(approved=True, collection__approved=True, ).values_list('id', 'collection')

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

    items_in_kits, items_in_collections = get_items_count(ItemPrototype._db_all())
    statistics['total_items_in_kits'] = items_in_kits
    statistics['total_items_in_collections'] = items_in_collections
    statistics['total_items'] = sum(items_in_collections.values())

    if account_items:
        items_in_kits, items_in_collections = get_items_count(ItemPrototype._db_filter(id__in=account_items.items_ids()))
        statistics['account_items_in_kits'] = items_in_kits
        statistics['account_items_in_collections'] = items_in_collections
        statistics['account_items'] = sum(items_in_collections.values())

    return statistics
