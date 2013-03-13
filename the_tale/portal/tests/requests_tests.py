# coding: utf-8

from django.test import client
from django.core.urlresolvers import reverse

from common.utils.testcase import TestCase

from game.logic import create_test_map

class TestRequests(TestCase):

    def setUp(self):
        super(TestRequests, self).setUp()
        create_test_map()
        self.client = client.Client()

    def test_index(self):
        response = self.client.get(reverse('portal:'))
        self.assertEqual(response.status_code, 200)

    def test_preview(self):
        text = 'simple test text'
        self.check_html_ok(self.client.post(reverse('portal:preview'), {'text': text}), texts=[text])
