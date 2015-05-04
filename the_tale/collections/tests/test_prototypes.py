# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user
from the_tale.game.logic import create_test_map

from the_tale.collections.prototypes import CollectionPrototype, KitPrototype, ItemPrototype, AccountItemsPrototype, GiveItemTaskPrototype
from the_tale.collections.storage import collections_storage, kits_storage, items_storage
from the_tale.collections import exceptions


class PrototypeTestsBase(testcase.TestCase):

    def setUp(self):
        super(PrototypeTestsBase, self).setUp()

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


class CollectionPrototypeTests(PrototypeTestsBase):

    def test_create(self):
        self.assertTrue(self.collection_1.id in collections_storage)
        self.assertTrue(self.collection_2.id in collections_storage)

        with self.check_changed(lambda: collections_storage.version):
            collection = CollectionPrototype.create(caption=u'collection_3', description=u'description_3')

        self.assertTrue(collection.id in collections_storage)

    def test_save(self):
        with self.check_changed(lambda: collections_storage.version):
            self.collection_1.save()

    def test_save__not_from_storage(self):
        self.assertRaises(exceptions.SaveNotRegisteredCollectionError, CollectionPrototype.get_by_id(self.collection_1.id).save)


class KitPrototypeTests(PrototypeTestsBase):

    def test_create(self):
        self.assertTrue(self.kit_1.id in kits_storage)
        self.assertTrue(self.kit_2.id in kits_storage)

        with self.check_changed(lambda: kits_storage.version):
            kit = KitPrototype.create(collection=self.collection_2, caption=u'kit_3', description=u'description_3')

        self.assertTrue(kit.id in kits_storage)

    def test_save(self):
        with self.check_changed(lambda: kits_storage.version):
            self.kit_1.save()

    def test_save__not_from_storage(self):
        self.assertRaises(exceptions.SaveNotRegisteredKitError, KitPrototype.get_by_id(self.kit_1.id).save)


class ItemPrototypeTests(PrototypeTestsBase):

    def test_create(self):
        self.assertTrue(self.item_1_1.id in items_storage)
        self.assertTrue(self.item_1_2.id in items_storage)

        with self.check_changed(lambda: items_storage.version):
            item = ItemPrototype.create(kit=self.kit_2, caption=u'item_3', text=u'description_3')

        self.assertTrue(item.id in items_storage)

    def test_save(self):
        with self.check_changed(lambda: items_storage.version):
            self.item_1_1.save()

    def test_save__not_from_storage(self):
        self.assertRaises(exceptions.SaveNotRegisteredItemError, ItemPrototype.get_by_id(self.item_1_1.id).save)



class AccountItemsPrototypeTests(PrototypeTestsBase):

    def test_give_item(self):
        with self.check_not_changed(GiveItemTaskPrototype._db_count):
            self.account_1_items.give_item(self.account_1.id, self.item_1_1)

    # change tests order to fix sqlite segmentation fault
    def test_1_give_item__unapproved(self):
        with self.check_delta(GiveItemTaskPrototype._db_count, 1):
            self.account_1_items.give_item(self.account_1.id, self.item_1_2)

    def test_add_item(self):
        self.assertFalse(self.account_1_items.has_item(self.item_1_2))
        self.account_1_items.add_item(self.item_1_2)
        self.assertTrue(self.account_1_items.has_item(self.item_1_2))
