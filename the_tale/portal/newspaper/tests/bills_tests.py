# coding: utf-8
import mock
import datetime

from common.utils.testcase import TestCase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.logic import create_test_map

from game.bills.prototypes import BillPrototype, VotePrototype
from game.bills.bills import PlaceRenaming
from game.bills.conf import bills_settings

from portal.newspaper.models import NewspaperEvent, NEWSPAPER_EVENT_TYPE
from portal.newspaper.prototypes import NewspaperEventPrototype


class TestBillsEvents(TestCase):

    def setUp(self):
        self.place1, self.place2, self.place3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user1', 'test_user1@test.com', '111111')
        self.account1 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user2', 'test_user2@test.com', '111111')
        self.account2 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user3', 'test_user3@test.com', '111111')
        self.account3 = AccountPrototype.get_by_id(account_id)

        from forum.models import Category, SubCategory

        forum_category = Category.objects.create(caption='category-1', slug='category-1')
        SubCategory.objects.create(caption=bills_settings.FORUM_CATEGORY_SLUG + '-caption',
                                   slug=bills_settings.FORUM_CATEGORY_SLUG,
                                   category=forum_category)

    def create_place_renaming_bill(self, index):
        bill_data = PlaceRenaming(place_id=self.place1.id, base_name='new_name_%d' % index)
        return BillPrototype.create(self.account1, 'bill-%d-caption' % index, 'bill-%d-rationale' % index, bill_data)

    def test_initialize(self):
        self.assertEqual(NewspaperEvent.objects.all().count(),0)

    def test_bill_create(self):
        bill = self.create_place_renaming_bill(1)
        self.assertEqual(NewspaperEvent.objects.all().count(), 1)
        event = NewspaperEventPrototype(NewspaperEvent.objects.all().order_by('created_at')[0])
        self.assertEqual(event.data.TYPE, NEWSPAPER_EVENT_TYPE.BILL_CREATED)
        self.assertEqual(event.data.bill_id, bill.id)
        self.assertEqual(event.data.bill_type, bill.type)
        self.assertEqual(event.data.caption, bill.caption)

    def test_bill_edited(self):
        bill = self.create_place_renaming_bill(1)
        form = PlaceRenaming.UserForm({'caption': 'new-caption',
                                       'rationale': 'new-rationale',
                                       'place': self.place2.id,
                                       'new_name': 'new-new-name'})

        self.assertTrue(form.is_valid())
        bill.update(form)

        self.assertEqual(NewspaperEvent.objects.all().count(), 2)

        bill = BillPrototype.get_by_id(bill.id)
        event = NewspaperEventPrototype(NewspaperEvent.objects.all().order_by('created_at')[1])

        self.assertEqual(event.data.TYPE, NEWSPAPER_EVENT_TYPE.BILL_EDITED)
        self.assertEqual(event.data.bill_id, bill.id)
        self.assertEqual(event.data.bill_type, bill.type)
        self.assertEqual(event.data.caption, bill.caption)

    @mock.patch('game.bills.conf.bills_settings.MIN_VOTES_NUMBER', 2)
    @mock.patch('game.bills.prototypes.BillPrototype.time_before_end_step', datetime.timedelta(seconds=0))
    def test_rejected(self):
        bill = self.create_place_renaming_bill(1)
        bill.approved_by_moderator = True
        bill.save()

        self.assertFalse(bill.apply())

        self.assertEqual(NewspaperEvent.objects.all().count(), 2)

        event = NewspaperEventPrototype(NewspaperEvent.objects.all().order_by('created_at')[1])

        self.assertEqual(event.data.TYPE, NEWSPAPER_EVENT_TYPE.BILL_PROCESSED)
        self.assertEqual(event.data.bill_id, bill.id)
        self.assertEqual(event.data.bill_type, bill.type)
        self.assertEqual(event.data.caption, bill.caption)
        self.assertEqual(event.data.accepted, False)


    @mock.patch('game.bills.conf.bills_settings.MIN_VOTES_NUMBER', 2)
    @mock.patch('game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('game.bills.prototypes.BillPrototype.time_before_end_step', datetime.timedelta(seconds=0))
    def test_accepted(self):
        bill = self.create_place_renaming_bill(1)
        bill.approved_by_moderator = True
        bill.save()

        VotePrototype.create(self.account2, bill, False)
        VotePrototype.create(self.account3, bill, True)

        self.assertTrue(bill.apply())

        self.assertEqual(NewspaperEvent.objects.all().count(), 2)

        event = NewspaperEventPrototype(NewspaperEvent.objects.all().order_by('created_at')[1])

        self.assertEqual(event.data.TYPE, NEWSPAPER_EVENT_TYPE.BILL_PROCESSED)
        self.assertEqual(event.data.bill_id, bill.id)
        self.assertEqual(event.data.bill_type, bill.type)
        self.assertEqual(event.data.caption, bill.caption)
        self.assertEqual(event.data.accepted, True)
