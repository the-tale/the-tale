# coding: utf-8

import time

from the_tale.common.utils import testcase

from the_tale.collections.prototypes import CollectionPrototype, KitPrototype, ItemPrototype
from the_tale.collections.container import ItemsContainer
from the_tale.collections.storage import items_storage


class ItemsContainerTests(testcase.TestCase):

    def setUp(self):
        super(ItemsContainerTests, self).setUp()

        self.container = ItemsContainer()

        self.collection_1 = CollectionPrototype.create(caption=u'collection_1', description=u'description_1')
        self.collection_2 = CollectionPrototype.create(caption=u'collection_2', description=u'description_2', approved=True)

        self.kit_1 = KitPrototype.create(collection=self.collection_1, caption=u'kit_1', description=u'description_1')
        self.kit_2 = KitPrototype.create(collection=self.collection_2, caption=u'kit_2', description=u'description_2')

        self.item_1_1 = ItemPrototype.create(kit=self.kit_1, caption=u'item_1_1', text=u'text_1_1')
        self.item_1_2 = ItemPrototype.create(kit=self.kit_1, caption=u'item_1_2', text=u'text_1_2', approved=True)
        self.item_2_1 = ItemPrototype.create(kit=self.kit_2, caption=u'item_2_1', text=u'text_2_1', approved=True)


    def test_serialize(self):
        self.container.add_item(self.item_1_2)
        self.container.add_item(self.item_2_1)
        self.assertEqual(self.container.serialize(), ItemsContainer.deserialize(None, self.container.serialize()).serialize())


    def test_add_item(self):

        old_time = time.time()

        self.assertFalse(self.container.updated)
        self.assertFalse(self.container.has_item(self.item_1_2))

        self.container.add_item(self.item_1_2)

        self.assertTrue(self.container.updated)
        self.assertTrue(self.container.has_item(self.item_1_2))

        self.assertTrue(old_time < self.container.items[self.item_1_2.id])


    def test_last_items(self):
        self.container.add_item(self.item_2_1)
        self.container.add_item(self.item_1_1)
        self.container.add_item(self.item_1_2)

        self.assertEqual([item.id for item in self.container.last_items(number=2)],
                         [self.item_1_2.id, self.item_2_1.id])


    def test_last_items__no_item_in_sotrage(self):
        self.container.add_item(self.item_2_1)
        self.container.add_item(self.item_1_1)
        self.container.add_item(self.item_1_2)

        self.item_1_2._model.delete()

        items_storage.refresh()

        self.assertEqual([item.id for item in self.container.last_items(number=2)],
                         [self.item_2_1.id])

        items_storage[self.item_1_1.id].approved = True

        self.assertEqual([item.id for item in self.container.last_items(number=2)],
                         [self.item_1_1.id, self.item_2_1.id])


    def test_has_item(self):
        self.assertFalse(self.item_1_1.approved)
        self.assertTrue(self.item_1_2.approved)

        self.container.add_item(self.item_1_1)
        self.container.add_item(self.item_1_2)

        self.assertTrue(self.container.has_item(self.item_1_1))
        self.assertTrue(self.container.has_item(self.item_1_2))
