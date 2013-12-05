# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user
from the_tale.accounts.personal_messages.prototypes import MessagePrototype

from the_tale.collections.prototypes import CollectionPrototype, KitPrototype, ItemPrototype, AccountItemsPrototype, GiveItemTaskPrototype
from the_tale.collections.workers.environment import workers_environment


from the_tale.game.logic import create_test_map



class ItemsManagerTests(testcase.TestCase):

    def setUp(self):
        super(ItemsManagerTests, self).setUp()

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

        self.account_1_items.add_item(self.item_1_2)
        self.account_1_items.save()

        self.worker = workers_environment.items_manager
        self.worker.initialize()

    def test_add_items__not_tasks(self):
        self.worker.add_items()
        self.account_1_items.reload()
        self.assertEqual(len(self.account_1_items.items), 1)

    def test_add_items(self):
        GiveItemTaskPrototype.create(account_id=self.account_1.id, item_id=self.item_2_1.id)

        self.assertFalse(self.account_1_items.has_item(self.item_2_1))

        self.worker.add_items()

        self.account_1_items.reload()

        self.assertTrue(self.account_1_items.has_item(self.item_2_1))
        self.assertEqual(GiveItemTaskPrototype._db_count(), 0)
