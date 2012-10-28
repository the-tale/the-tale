# coding: utf-8
import mock
import datetime

from dext.utils import s11n

from textgen.words import Noun

from common.utils.testcase import TestCase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from forum.models import Post, Thread, MARKUP_METHOD

from game.logic import create_test_map

from game.bills.models import Bill, Vote, BILL_STATE
from game.bills.prototypes import BillPrototype, VotePrototype
from game.bills.bills import PlaceRenaming
from game.bills.conf import bills_settings
from game.bills.exceptions import BillException

from game.map.places.storage import places_storage


class BaseTestPrototypes(TestCase):

    NAME_FORMS = (u'new_name_1',
                  u'new_name_2',
                  u'new_name_3',
                  u'new_name_4',
                  u'new_name_5',
                  u'new_name_6',
                  u'new_name_7',
                  u'new_name_8',
                  u'new_name_9',
                  u'new_name_10',
                  u'new_name_11',
                  u'new_name_12')


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


class TestPrototype(BaseTestPrototypes):

    def setUp(self):
        super(TestPrototype, self).setUp()

        self.bill = self.create_place_renaming_bill(1)

    def create_place_renaming_bill(self, index):
        bill_data = PlaceRenaming(place_id=self.place1.id, base_name='new_name_%d' % index)
        return BillPrototype.create(self.account1, 'bill-%d-caption' % index, 'bill-%d-rationale' % index, bill_data)

    def test_create(self):
        self.assertEqual(self.bill.caption, 'bill-1-caption')
        self.assertEqual(self.bill.rationale, 'bill-1-rationale')
        self.assertEqual(self.bill.approved_by_moderator, False)
        self.assertEqual(self.bill.votes_for, 1)
        self.assertEqual(self.bill.votes_against, 0)
        self.assertEqual(Post.objects.all().count(), 1)
        self.assertEqual(Post.objects.all()[0].markup_method, MARKUP_METHOD.POSTMARKUP)


    def test_update(self):
        VotePrototype.create(self.account2, self.bill, True)
        VotePrototype.create(self.account3, self.bill, False)
        self.bill.recalculate_votes()
        self.bill.approved_by_moderator = True
        self.bill.save()

        old_updated_at = self.bill.updated_at

        self.assertEqual(self.bill.votes_for, 2)
        self.assertEqual(self.bill.votes_against, 1)
        self.assertEqual(Vote.objects.all().count(), 3)
        self.assertEqual(self.bill.caption, 'bill-1-caption')
        self.assertEqual(self.bill.rationale, 'bill-1-rationale')
        self.assertEqual(self.bill.approved_by_moderator, True)
        self.assertEqual(self.bill.data.base_name, 'new_name_1')
        self.assertEqual(self.bill.data.place_id, self.place1.id)
        self.assertEqual(Post.objects.all().count(), 1)

        form = PlaceRenaming.UserForm({'caption': 'new-caption',
                                       'rationale': 'new-rationale',
                                       'place': self.place2.id,
                                       'new_name': 'new-new-name'})

        self.assertTrue(form.is_valid())

        self.bill.update(form)

        self.bill = BillPrototype.get_by_id(self.bill.id)

        self.assertTrue(old_updated_at < self.bill.updated_at)
        self.assertTrue(self.bill.state.is_voting)
        self.assertEqual(self.bill.votes_for, 1)
        self.assertEqual(self.bill.votes_against, 0)
        self.assertEqual(Vote.objects.all().count(), 1)
        self.assertEqual(self.bill.caption, 'new-caption')
        self.assertEqual(self.bill.rationale, 'new-rationale')
        self.assertEqual(self.bill.approved_by_moderator, False)
        self.assertEqual(self.bill.data.base_name, 'new-new-name')
        self.assertEqual(self.bill.data.place_id, self.place2.id)
        self.assertEqual(Post.objects.all().count(), 2)

    def test_update_by_moderator(self):
        self.assertEqual(self.bill.approved_by_moderator, False)

        self.assertEqual(self.bill.data.name_forms.forms, tuple([u'new_name_1']*12))

        noun = Noun(normalized=self.bill.data.base_name.lower(),
                    forms=self.NAME_FORMS,
                    properties=(u'мр',))

        form = PlaceRenaming.ModeratorForm({'approved': True,
                                            'name_forms': s11n.to_json(noun.serialize()) })

        self.assertTrue(form.is_valid())

        self.bill.update_by_moderator(form)

        self.bill = BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(self.bill.state.is_voting)
        self.assertEqual(self.bill.approved_by_moderator, True)
        self.assertEqual(self.bill.data.name_forms.forms, self.NAME_FORMS)

    def test_remove(self):
        self.assertEqual(Thread.objects.all().count(), 1)
        self.assertEqual(Bill.objects.all().count(), 1)

        self.bill.remove()

        self.assertEqual(Thread.objects.all().count(), 0)
        self.assertEqual(Bill.objects.all().count(), 0)


class TestPrototypeApply(BaseTestPrototypes):

    def setUp(self):
        super(TestPrototypeApply, self).setUp()

        bill_data = PlaceRenaming(place_id=self.place1.id, base_name='new_name_1')
        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', bill_data)

        self.bill.approved_by_moderator = True
        self.bill.save()

    def check_place(self, place_id, name, name_forms):
        self.assertEqual(places_storage[place_id].name, name)
        self.assertEqual(places_storage[place_id].normalized_name[0].forms, name_forms)


    @mock.patch('game.bills.prototypes.BillPrototype.time_before_end_step', lambda x: datetime.timedelta(seconds=0))
    def test_wrong_state(self):
        self.bill.state = BILL_STATE.ACCEPTED
        self.bill.save()
        self.assertRaises(BillException, self.bill.apply)

        places_storage.sync(force=True)

        self.check_place(self.place1.id, self.place1.name, self.place1.normalized_name[0].forms)

    @mock.patch('game.bills.prototypes.BillPrototype.time_before_end_step', lambda x: datetime.timedelta(seconds=0))
    def test_not_approved(self):
        self.bill.approved_by_moderator = False
        self.bill.save()

        self.assertRaises(BillException, self.bill.apply)

        places_storage.sync(force=True)

        self.check_place(self.place1.id, self.place1.name, self.place1.normalized_name[0].forms)

    def test_wrong_time(self):
        self.assertRaises(BillException, self.bill.apply)
        places_storage.sync(force=True)
        self.check_place(self.place1.id, self.place1.name, self.place1.normalized_name[0].forms)

    @mock.patch('game.bills.conf.bills_settings.MIN_VOTES_NUMBER', 2)
    @mock.patch('game.bills.prototypes.BillPrototype.time_before_end_step', datetime.timedelta(seconds=0))
    def test_not_enough_voices(self):

        self.assertEqual(Post.objects.all().count(), 1)

        self.assertFalse(self.bill.apply())
        self.assertTrue(self.bill.state.is_rejected)

        self.assertEqual(Post.objects.all().count(), 2)


        bill = BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state.is_rejected)

        places_storage.sync(force=True)

        self.check_place(self.place1.id, self.place1.name, self.place1.normalized_name[0].forms)


    @mock.patch('game.bills.conf.bills_settings.MIN_VOTES_NUMBER', 1)
    @mock.patch('game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.51)
    @mock.patch('game.bills.prototypes.BillPrototype.time_before_end_step', datetime.timedelta(seconds=0))
    def test_not_enough_voices_percents(self):
        VotePrototype.create(self.account2, self.bill, False)

        self.assertEqual(Post.objects.all().count(), 1)

        self.assertFalse(self.bill.apply())
        self.assertTrue(self.bill.state.is_rejected)

        self.assertEqual(Post.objects.all().count(), 2)

        bill = BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state.is_rejected)

        places_storage.sync(force=True)

        self.check_place(self.place1.id, self.place1.name, self.place1.normalized_name[0].forms)

    @mock.patch('game.bills.conf.bills_settings.MIN_VOTES_NUMBER', 2)
    @mock.patch('game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('game.bills.prototypes.BillPrototype.time_before_end_step', datetime.timedelta(seconds=0))
    def test_approved(self):
        VotePrototype.create(self.account2, self.bill, False)
        VotePrototype.create(self.account3, self.bill, True)

        ##################################
        # set name forms
        noun = Noun(normalized=self.bill.data.base_name.lower(),
                    forms=self.NAME_FORMS,
                    properties=(u'мр',))

        form = PlaceRenaming.ModeratorForm({'approved': True,
                                            'name_forms': s11n.to_json(noun.serialize()) })

        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)
        ##################################

        self.assertEqual(Post.objects.all().count(), 1)

        self.assertTrue(self.bill.apply())
        self.assertTrue(self.bill.state.is_accepted)

        self.assertEqual(Post.objects.all().count(), 2)

        bill = BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state.is_accepted)

        places_storage.sync(force=True)

        self.check_place(self.place1.id, 'new_name_1', self.NAME_FORMS)
