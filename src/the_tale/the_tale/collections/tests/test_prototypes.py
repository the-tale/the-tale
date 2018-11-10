
import smart_imports

smart_imports.all()


class PrototypeTestsBase(utils_testcase.TestCase):

    def setUp(self):
        super(PrototypeTestsBase, self).setUp()

        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.account_1_items = prototypes.AccountItemsPrototype.get_by_account_id(self.account_1.id)

        self.collection_1 = prototypes.CollectionPrototype.create(caption='collection_1', description='description_1')
        self.collection_2 = prototypes.CollectionPrototype.create(caption='collection_2', description='description_2', approved=True)

        self.kit_1 = prototypes.KitPrototype.create(collection=self.collection_1, caption='kit_1', description='description_1')

        self.kit_2 = prototypes.KitPrototype.create(collection=self.collection_2, caption='kit_2', description='description_2', approved=True)
        self.kit_3 = prototypes.KitPrototype.create(collection=self.collection_2, caption='kit_3', description='description_3', approved=True)

        self.item_1_1 = prototypes.ItemPrototype.create(kit=self.kit_1, caption='item_1_1', text='text_1_1', approved=False)
        self.item_1_2 = prototypes.ItemPrototype.create(kit=self.kit_1, caption='item_1_2', text='text_1_2', approved=True)
        self.item_2_1 = prototypes.ItemPrototype.create(kit=self.kit_2, caption='item_2_1', text='text_2_1', approved=True)
        self.item_2_2 = prototypes.ItemPrototype.create(kit=self.kit_2, caption='item_2_2', text='text_2_2', approved=False)
        self.item_3_1 = prototypes.ItemPrototype.create(kit=self.kit_3, caption='item_3_1', text='text_3_1', approved=True)


class CollectionPrototypeTests(PrototypeTestsBase):

    def test_create(self):
        self.assertTrue(self.collection_1.id in storage.collections)
        self.assertTrue(self.collection_2.id in storage.collections)

        with self.check_changed(lambda: storage.collections.version):
            collection = prototypes.CollectionPrototype.create(caption='collection_3', description='description_3')

        self.assertTrue(collection.id in storage.collections)

    def test_save(self):
        with self.check_changed(lambda: storage.collections.version):
            self.collection_1.save()

    def test_save__not_from_storage(self):
        self.assertRaises(exceptions.SaveNotRegisteredCollectionError, prototypes.CollectionPrototype.get_by_id(self.collection_1.id).save)


class KitPrototypeTests(PrototypeTestsBase):

    def test_create(self):
        self.assertTrue(self.kit_1.id in storage.kits)
        self.assertTrue(self.kit_2.id in storage.kits)

        with self.check_changed(lambda: storage.kits.version):
            kit = prototypes.KitPrototype.create(collection=self.collection_2, caption='kit_3', description='description_3')

        self.assertTrue(kit.id in storage.kits)

    def test_save(self):
        with self.check_changed(lambda: storage.kits.version):
            self.kit_1.save()

    def test_save__not_from_storage(self):
        self.assertRaises(exceptions.SaveNotRegisteredKitError, prototypes.KitPrototype.get_by_id(self.kit_1.id).save)


class ItemPrototypeTests(PrototypeTestsBase):

    def test_create(self):
        self.assertTrue(self.item_1_1.id in storage.items)
        self.assertTrue(self.item_1_2.id in storage.items)

        with self.check_changed(lambda: storage.items.version):
            item = prototypes.ItemPrototype.create(kit=self.kit_2, caption='item_3', text='description_3')

        self.assertTrue(item.id in storage.items)

    def test_save(self):
        with self.check_changed(lambda: storage.items.version):
            self.item_1_1.save()

    def test_save__not_from_storage(self):
        self.assertRaises(exceptions.SaveNotRegisteredItemError, prototypes.ItemPrototype.get_by_id(self.item_1_1.id).save)


class AccountItemsPrototypeTests(PrototypeTestsBase):

    def test_give_item(self):
        with self.check_not_changed(prototypes.GiveItemTaskPrototype._db_count):
            self.account_1_items.give_item(self.account_1.id, self.item_1_1)

    # change tests order to fix sqlite segmentation fault
    def test_1_give_item__unapproved(self):
        with self.check_delta(prototypes.GiveItemTaskPrototype._db_count, 1):
            self.account_1_items.give_item(self.account_1.id, self.item_1_2)

    def test_add_item(self):
        self.assertFalse(self.account_1_items.has_item(self.item_1_2))
        self.account_1_items.add_item(self.item_1_2)
        self.assertTrue(self.account_1_items.has_item(self.item_1_2))
