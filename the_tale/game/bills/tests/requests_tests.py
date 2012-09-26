# coding: utf-8

from django.test import client
from django.core.urlresolvers import reverse

from common.utils.testcase import TestCase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.logic import create_test_map

from game.bills.models import Bill
from game.bills.prototypes import BillPrototype
from game.bills.bills import PlaceRenaming
from game.bills.conf import bills_settings
from game.map.places.storage import places_storage


class BaseTestRequests(TestCase):

    def setUp(self):
        self.place1, self.place2, self.place3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user1', 'test_user1@test.com', '111111')
        self.account1 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user2', 'test_user2@test.com', '111111')
        self.account2 = AccountPrototype.get_by_id(account_id)

        self.client = client.Client()

        self.client.post(reverse('accounts:login'), {'email': 'test_user1@test.com', 'password': '111111'})

        from forum.models import Category, SubCategory

        forum_category = Category.objects.create(caption='category-1', slug='category-1')
        SubCategory.objects.create(caption=bills_settings.FORUM_PROPOSAL_CATEGORY_SLUG + '-caption',
                                   slug=bills_settings.FORUM_PROPOSAL_CATEGORY_SLUG,
                                   category=forum_category)

        SubCategory.objects.create(caption=bills_settings.FORUM_VOTING_CATEGORY_SLUG + '-caption',
                                   slug=bills_settings.FORUM_VOTING_CATEGORY_SLUG,
                                   category=forum_category)


    def logout(self):
        response = self.client.post(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 200)

    def create_bills(self, number, owner, caption_template, rationale_template, bill_data):
        for i in xrange(number):
            BillPrototype.create(owner.user, caption_template % i, rationale_template % i, bill_data)


class TestIndexRequests(BaseTestRequests):

    def test_unlogined(self):
        self.logout()
        self.check_html_ok(self.client.get(reverse('game:bills:')), texts=(('bills.unlogined', 1),))

    def test_is_fast(self):
        self.account1.is_fast = True
        self.account1.save()
        self.check_html_ok(self.client.get(reverse('game:bills:')), texts=(('bills.is_fast', 1),))

    def test_no_bills(self):
        # print self.client.get(reverse('game:bills:'))
        self.check_html_ok(self.client.get(reverse('game:bills:')), texts=(('pgf-no-bills-message', 1),))

    def test_one_page(self):
        bill_data = PlaceRenaming(place_id=self.place1.id, base_name='new_name_1')
        self.create_bills(2, self.account1, 'caption-a1-%d', 'rationale-a1-%d', bill_data)
        bill_data = PlaceRenaming(place_id=self.place2.id, base_name='new_name_2')
        self.create_bills(3, self.account2, 'caption-a2-%d', 'rationale-a2-%d', bill_data)

        texts = [('pgf-no-bills-message', 0),
                 ('caption-a1-0', 1), ('rationale-a1-0', 0),
                 ('caption-a1-1', 1), ('rationale-a1-1', 0),
                 ('caption-a2-0', 1), ('rationale-a2-0', 0),
                 ('caption-a2-1', 1), ('rationale-a2-1', 0),
                 ('caption-a2-2', 1), ('rationale-a2-2', 0),
                 ('test_user1', 2),
                 ('test_user2', 3)]

        self.check_html_ok(self.client.get(reverse('game:bills:')), texts=texts)

    def test_two_pages(self):
        bill_data = PlaceRenaming(place_id=self.place1.id, base_name='new_name_1')
        self.create_bills(bills_settings.BILLS_ON_PAGE, self.account1, 'caption-a1-%d', 'rationale-a1-%d', bill_data)
        bill_data = PlaceRenaming(place_id=self.place2.id, base_name='new_name_2')
        self.create_bills(3, self.account2, 'caption-a2-%d', 'rationale-a2-%d', bill_data)

        texts = [('pgf-no-bills-message', 0),
                 ('caption-a2-0', 1), ('rationale-a2-0', 0),
                 ('caption-a2-1', 1), ('rationale-a2-1', 0),
                 ('caption-a2-2', 1), ('rationale-a2-2', 0),
                 ('test_user2', 3)]

        self.check_html_ok(self.client.get(reverse('game:bills:')+'?page=2'), texts=texts)


class TestNewRequests(BaseTestRequests):

    def test_unlogined(self):
        self.logout()
        self.check_html_ok(self.client.get(reverse('game:bills:new') + ('?type=%s' % PlaceRenaming.type_str)), texts=(('bills.unlogined', 1),))

    def test_is_fast(self):
        self.account1.is_fast = True
        self.account1.save()
        self.check_html_ok(self.client.get(reverse('game:bills:new') + ('?type=%s' % PlaceRenaming.type_str)), texts=(('bills.is_fast', 1),))

    def test_wrong_type(self):
        self.check_html_ok(self.client.get(reverse('game:bills:new') + '?type=xxx'), texts=(('bills.new.wrong_type', 1),))

    def test_success(self):
        self.check_html_ok(self.client.get(reverse('game:bills:new') + ('?type=%s' % PlaceRenaming.type_str)))

    def test_new_place_renaming(self):
        texts = [('>'+place.name+'<', 1) for place in places_storage.all()]
        self.check_html_ok(self.client.get(reverse('game:bills:new') + ('?type=%s' % PlaceRenaming.type_str)), texts=texts)


class TestShowRequests(BaseTestRequests):

    def test_unlogined(self):
        bill_data = PlaceRenaming(place_id=self.place1.id, base_name='new_name_1')
        self.create_bills(1, self.account1, 'caption-a1-%d', 'rationale-a1-%d', bill_data)
        bill = Bill.objects.all()[0]

        self.logout()
        self.check_html_ok(self.client.get(reverse('game:bills:show', args=[bill.id])), texts=(('bills.unlogined', 1),))

    def test_is_fast(self):
        bill_data = PlaceRenaming(place_id=self.place1.id, base_name='new_name_1')
        self.create_bills(1, self.account1, 'caption-a1-%d', 'rationale-a1-%d', bill_data)
        bill = Bill.objects.all()[0]

        self.account1.is_fast = True
        self.account1.save()
        self.check_html_ok(self.client.get(reverse('game:bills:show', args=[bill.id])), texts=(('bills.is_fast', 1),))

    def test_unexsists(self):
        self.check_html_ok(self.client.get(reverse('game:bills:show', args=[0])), status_code=404)

    def test_success(self):
        bill_data = PlaceRenaming(place_id=self.place2.id, base_name='new_name_2')
        self.create_bills(1, self.account1, 'caption-a2-%d', 'rationale-a2-%d', bill_data)
        bill = Bill.objects.all()[0]

        texts = [('caption-a2-0', 2),
                 ('rationale-a2-0', 1),
                 (self.place2.name, 1)]

        self.check_html_ok(self.client.get(reverse('game:bills:show', args=[bill.id])), texts=texts)


class TestCreateRequests(BaseTestRequests):

    def get_post_data(self):
        return {'caption': 'bill-caption',
                'rationale': 'bill-rationale',
                'place': self.place1.id,
                'new_name': 'new-name'}

    def test_unlogined(self):
        self.logout()
        self.check_ajax_error(self.client.post(reverse('game:bills:create'), self.get_post_data()), 'bills.unlogined')

    def test_is_fast(self):
        self.account1.is_fast = True
        self.account1.save()
        self.check_ajax_error(self.client.post(reverse('game:bills:create'), self.get_post_data()), 'bills.is_fast')

    def test_type_not_exist(self):
        self.check_ajax_error(self.client.post(reverse('game:bills:create') + '?type=xxx', self.get_post_data()), 'bills.create.wrong_type')

    def test_success(self):
        response = self.client.post(reverse('game:bills:create') + ('?type=%s' % PlaceRenaming.type_str), self.get_post_data())
        bill = BillPrototype(Bill.objects.all()[0])
        self.assertEqual(bill.caption, 'bill-caption')
        self.assertEqual(bill.rationale, 'bill-rationale')
        self.assertEqual(bill.data.place.id, self.place1.id)
        self.assertEqual(bill.data.base_name, 'new-name')
        self.check_ajax_ok(response, data={'next_url': reverse('game:bills:show', args=[bill.id])})
