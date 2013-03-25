# coding: utf-8

from django.test import client
from django.db import IntegrityError
from django.core.urlresolvers import reverse

from common.utils import testcase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.logic import create_test_map

from cms.models import Page
from cms.conf import cms_settings


class TestCMSRequests(testcase.TestCase):

    def setUp(self):
        super(TestCMSRequests, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.staff_account = AccountPrototype.get_by_id(account_id)

        self.client = client.Client()

        self.p1 = Page.objects.create(section='test', slug='slug1', caption='caption1', content='content1', order=0, active=False, author=self.staff_account._model)
        self.p1 = Page.objects.create(section='test', slug='slug2', caption='caption2', content='content2', order=1, active=True, author=self.staff_account._model)
        self.p1 = Page.objects.create(section='test', slug='slug3', caption='caption3', content='content3', order=2, active=True, author=self.staff_account._model)

    def test_sections_list(self):
        for section in cms_settings.SECTIONS:
            self.assertEqual(section.url[-1], '/')

    def test_duplicate_slug(self):
        self.assertRaises(IntegrityError, Page.objects.create, section='test', slug='slug1', caption='caption4', content='content4', order=4)

    def test_duplicate_order(self):
        self.assertRaises(IntegrityError, Page.objects.create, section='test', slug='slug4', caption='caption4', content='content4', order=0)


    def test_page_request(self):
        response = self.client.get(reverse('cms:test:page', args=['slug3']))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('caption3' in response.content)
        self.assertTrue('content3' in response.content)

    def test_unknown_page_request(self):
        response = self.client.get(reverse('cms:test:page', args=['wrong_slug3']))
        self.assertEqual(response.status_code, 404)

    def test_redirect_to_first_page(self):
        response = self.client.get(reverse('cms:test:'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], 'http://testserver%s' % reverse('cms:test:page', args=['slug2']))

    def test_index_page(self):
        Page.objects.create(section='test', slug='', caption='caption4', content='content4', order=4, active=True, author=self.staff_account._model)
        response = self.client.get(reverse('cms:test:'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('caption4' in response.content)
        self.assertTrue('content4' in response.content)

    def test_disabled_page(self):
        response = self.client.get(reverse('cms:test:page', args=['slug1']))
        self.assertEqual(response.status_code, 404)
