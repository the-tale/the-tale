# coding: utf-8
from django.test import TestCase, client
from django.core.urlresolvers import reverse


class TestRequests(TestCase):

    def setUp(self):
        self.client = client.Client()

    def test_index(self):
        response = self.client.get(reverse('portal:'))
        self.assertEqual(response.status_code, 200)
