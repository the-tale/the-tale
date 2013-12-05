# coding: utf-8

import collections

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user
from the_tale.game.logic import create_test_map

from the_tale.collections.prototypes import CollectionPrototype, KitPrototype, ItemPrototype, AccountItemsPrototype
from the_tale.collections.logic import get_items_count, get_collections_statistics


class LogicTests(testcase.TestCase):

    def setUp(self):
        super(LogicTests, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')
        self.account_1 = AccountPrototype.get_by_id(account_id)

        self.account_1_items = AccountItemsPrototype.get_by_account_id(self.account_1.id)

        self.collection_1 = CollectionPrototype.create(caption=u'collection_1', description=u'description_1')
        self.collection_2 = CollectionPrototype.create(caption=u'collection_2', description=u'description_2', approved=True)

        self.kit_1 = KitPrototype.create(collection=self.collection_1, caption=u'kit_1', description=u'description_1')
        self.kit_2 = KitPrototype.create(collection=self.collection_2, caption=u'kit_2', description=u'description_2', approved=True)
        self.kit_3 = KitPrototype.create(collection=self.collection_2, caption=u'kit_3', description=u'description_3', approved=True)

        self.item_1_1 = ItemPrototype.create(kit=self.kit_1, caption=u'item_1_1', text=u'text_1_1', approved=False)
        self.item_1_2 = ItemPrototype.create(kit=self.kit_1, caption=u'item_1_2', text=u'text_1_2', approved=True)
        self.item_2_1 = ItemPrototype.create(kit=self.kit_2, caption=u'item_2_1', text=u'text_2_1', approved=True)
        self.item_2_2 = ItemPrototype.create(kit=self.kit_2, caption=u'item_2_2', text=u'text_2_2', approved=False)
        self.item_3_1 = ItemPrototype.create(kit=self.kit_3, caption=u'item_3_1', text=u'text_3_1', approved=True)


    def test_get_items_count(self):
        self.assertEqual(get_items_count(ItemPrototype._db_all()),
                         (collections.Counter({self.kit_2.id: 1, self.kit_3.id: 1}), {self.collection_2.id: 2}))

    def test_get_items_count__with_account(self):
        self.account_1_items.add_item(self.item_3_1)
        self.account_1_items.save()

        self.assertEqual(get_items_count(ItemPrototype._db_filter(id__in=self.account_1_items.items_ids())),
                         (collections.Counter({self.kit_3.id: 1}), {self.collection_2.id: 1}))

    def test_get_collections_statistics__no_account(self):
        self.assertEqual(get_collections_statistics(None),
                         {'total_items_in_collections': {self.collection_2.id: 2},
                          'total_items_in_kits': collections.Counter({self.kit_2.id: 1, self.kit_3.id: 1}),
                          'account_items_in_collections': {},
                          'account_items_in_kits': {},
                          'total_items': 2,
                          'account_items': 0})

    def test_get_collections_statistics__with_account(self):

        self.account_1_items.add_item(self.item_3_1)
        self.account_1_items.save()

        self.assertEqual(get_collections_statistics(self.account_1_items),
                         {'total_items_in_collections': {self.collection_2.id: 2},
                          'total_items_in_kits': collections.Counter({self.kit_2.id: 1, self.kit_3.id: 1}),
                          'account_items_in_collections': {self.collection_2.id: 1},
                          'account_items_in_kits': collections.Counter({self.kit_3.id: 1}),
                          'total_items': 2,
                          'account_items': 1})
