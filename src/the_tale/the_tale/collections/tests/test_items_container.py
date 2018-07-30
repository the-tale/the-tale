
import smart_imports

smart_imports.all()


class ItemsContainerTests(utils_testcase.TestCase):

    def setUp(self):
        super(ItemsContainerTests, self).setUp()

        self.container = container.ItemsContainer()

        self.collection_1 = prototypes.CollectionPrototype.create(caption='collection_1', description='description_1')
        self.collection_2 = prototypes.CollectionPrototype.create(caption='collection_2', description='description_2', approved=True)

        self.kit_1 = prototypes.KitPrototype.create(collection=self.collection_1, caption='kit_1', description='description_1')
        self.kit_2 = prototypes.KitPrototype.create(collection=self.collection_2, caption='kit_2', description='description_2')

        self.item_1_1 = prototypes.ItemPrototype.create(kit=self.kit_1, caption='item_1_1', text='text_1_1')
        self.item_1_2 = prototypes.ItemPrototype.create(kit=self.kit_1, caption='item_1_2', text='text_1_2', approved=True)
        self.item_2_1 = prototypes.ItemPrototype.create(kit=self.kit_2, caption='item_2_1', text='text_2_1', approved=True)

    def test_serialize(self):
        self.container.add_item(self.item_1_2)
        self.container.add_item(self.item_2_1)
        self.assertEqual(self.container.serialize(), container.ItemsContainer.deserialize(None, self.container.serialize()).serialize())

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

        storage.items.refresh()

        self.assertEqual([item.id for item in self.container.last_items(number=2)],
                         [self.item_2_1.id])

        storage.items[self.item_1_1.id].approved = True

        self.assertEqual([item.id for item in self.container.last_items(number=2)],
                         [self.item_1_1.id, self.item_2_1.id])

    def test_has_item(self):
        self.assertFalse(self.item_1_1.approved)
        self.assertTrue(self.item_1_2.approved)

        self.container.add_item(self.item_1_1)
        self.container.add_item(self.item_1_2)

        self.assertTrue(self.container.has_item(self.item_1_1))
        self.assertTrue(self.container.has_item(self.item_1_2))
