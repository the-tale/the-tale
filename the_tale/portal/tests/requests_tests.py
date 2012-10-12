# coding: utf-8
from django.test import client
from django.core.urlresolvers import reverse

from common.utils.testcase import TestCase


class TestRequests(TestCase):

    def setUp(self):
        self.client = client.Client()

    def test_index(self):
        response = self.client.get(reverse('portal:'))
        self.assertEqual(response.status_code, 200)

    def test_preview(self):
        text = 'simple test text'
        self.check_html_ok(self.client.post(reverse('portal:preview'), {'text': text}), texts=[text])
