# coding: utf-8

from django.core.urlresolvers import reverse

from dext.utils.testcase import TestCase as DextTestCase

class TestCase(DextTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def request_login(self, email, password='111111'):
        response = self.client.post(reverse('accounts:auth:login'), {'email': email, 'password': password})
        self.check_ajax_ok(response)

    def request_logout(self):
        response = self.client.post(reverse('accounts:auth:logout'))
        self.check_ajax_ok(response)
