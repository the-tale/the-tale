# coding: utf-8
import uuid
import random

from the_tale.common.utils import testcase

from dext.settings import settings

from the_tale.game.logic import create_test_map

from the_tale.game.map.places.models import Place
from the_tale.game.map.places.storage import PlacesStorage, resource_exchange_storage
from the_tale.game.map.places.prototypes import ResourceExchangePrototype
from the_tale.game.map.places.relations import RESOURCE_EXCHANGE_TYPE
from the_tale.game.map.places.exceptions import PlacesException

class PlacesStorageTest(testcase.TestCase):

    def setUp(self):
        super(PlacesStorageTest, self).setUp()
        self.p1, self.p2, self.p3 = create_test_map()
        self.storage = PlacesStorage()
        self.storage.sync()

    def test_initialization(self):
        storage = PlacesStorage()
        self.assertEqual(storage._data, {})
        self.assertEqual(storage._version, None)

    def test_sync(self):
        self.assertEqual(len(self.storage._data), 3)
        self.assertTrue(self.storage._version > 0)

        place = Place.objects.get(id=self.p1.id)
        place.name = '!!!'
        place.save()

        self.storage.sync()
        self.assertFalse(self.storage[self.p1.id].name == '!!!')

        self.storage.sync(force=True)
        self.assertTrue(self.storage[self.p1.id].name == '!!!')

    def test_sync_after_settings_update(self):
        self.assertEqual(len(self.storage._data), 3)
        self.assertTrue(self.storage._version > 0)

        place = Place.objects.get(id=self.p1.id)
        place.name = '!!!'
        place.save()

        self.storage.sync()
        self.assertFalse(self.storage[self.p1.id].name == '!!!')

        settings[self.storage.SETTINGS_KEY] = uuid.uuid4().hex

        self.storage.sync()
        self.assertTrue(self.storage[self.p1.id].name == '!!!')


    def test_getitem_wrong_id(self):
        self.assertRaises(PlacesException, self.storage.__getitem__, 666)

    def test_getitem(self):
        self.assertEqual(self.storage[self.p1.id].id, self.p1.id)

    def test_get(self):
        self.assertEqual(self.storage.get(666, self.p2).id, self.p2.id)
        self.assertEqual(self.storage.get(self.p3.id, self.p1).id, self.p3.id)

    def test_all(self):
        self.assertEqual(len(self.storage.all()), 3)

    def test_random_place(self):
        places = set([self.p1.id, self.p2.id, self.p3.id])

        for i in xrange(100):
            places.discard(self.storage.random_place().id)

        self.assertFalse(places)

    def test_contains(self):
        self.assertTrue(self.p1.id in self.storage)
        self.assertFalse(666 in self.storage)



class ResourceExchangeStorageTests(testcase.TestCase):

    def setUp(self):
        super(ResourceExchangeStorageTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        self.resource_1 = random.choice(RESOURCE_EXCHANGE_TYPE.records)
        self.resource_2 = random.choice(RESOURCE_EXCHANGE_TYPE.records)

    def test_create(self):
        self.assertEqual(len(resource_exchange_storage.all()), 0)

        old_version = resource_exchange_storage._version

        exchange = ResourceExchangePrototype.create(place_1=self.place_1,
                                                    place_2=self.place_2,
                                                    resource_1=self.resource_1,
                                                    resource_2=self.resource_2,
                                                    bill=None)

        self.assertEqual(len(resource_exchange_storage.all()), 1)

        self.assertEqual(exchange.id, resource_exchange_storage.all()[0].id)
        self.assertNotEqual(old_version, resource_exchange_storage._version)

    def test_get_exchanges_for_place__no(self):
        self.assertEqual(resource_exchange_storage.get_exchanges_for_place(self.place_2), [])

    def test_get_exchanges_for_place__multiple(self):
        exchange_1 = ResourceExchangePrototype.create(place_1=self.place_1,
                                                      place_2=self.place_2,
                                                      resource_1=self.resource_1,
                                                      resource_2=self.resource_2,
                                                      bill=None)

        ResourceExchangePrototype.create(place_1=self.place_1,
                                         place_2=self.place_3,
                                         resource_1=self.resource_1,
                                         resource_2=self.resource_2,
                                         bill=None)

        exchange_3 = ResourceExchangePrototype.create(place_1=self.place_2,
                                                      place_2=self.place_3,
                                                      resource_1=self.resource_1,
                                                      resource_2=self.resource_2,
                                                      bill=None)

        self.assertEqual(set(exchange.id for exchange in resource_exchange_storage.get_exchanges_for_place(self.place_2)),
                         set((exchange_1.id, exchange_3.id)))


    def test_get_exchanges_for_bill_id_no(self):
        self.assertEqual(resource_exchange_storage.get_exchange_for_bill_id(666), None)

    def test_get_exchanges_for_bill_id__exists(self):
        from the_tale.accounts.prototypes import AccountPrototype
        from the_tale.accounts.logic import register_user

        from the_tale.forum.models import Category, SubCategory
        from the_tale.game.bills.conf import bills_settings
        from the_tale.game.bills import bills
        from the_tale.game.bills.prototypes import BillPrototype

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        account = AccountPrototype.get_by_id(account_id)

        forum_category = Category.objects.create(caption='category-1', slug='category-1')
        SubCategory.objects.create(caption=bills_settings.FORUM_CATEGORY_UID + '-caption',
                                   uid=bills_settings.FORUM_CATEGORY_UID,
                                   category=forum_category)

        bill_data = bills.PlaceRenaming(place_id=self.place_1.id, base_name='new_name')
        bill = BillPrototype.create(account, 'bill-caption', 'bill-rationale', bill_data)

        ResourceExchangePrototype.create(place_1=self.place_1,
                                         place_2=self.place_2,
                                         resource_1=self.resource_1,
                                         resource_2=self.resource_2,
                                         bill=None)

        exchange_2 = ResourceExchangePrototype.create(place_1=self.place_1,
                                                      place_2=self.place_3,
                                                      resource_1=self.resource_1,
                                                      resource_2=self.resource_2,
                                                      bill=bill)

        ResourceExchangePrototype.create(place_1=self.place_2,
                                         place_2=self.place_3,
                                         resource_1=self.resource_1,
                                         resource_2=self.resource_2,
                                         bill=None)

        self.assertEqual(exchange_2.id, resource_exchange_storage.get_exchange_for_bill_id(bill.id).id)
