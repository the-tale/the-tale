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


class CallCounter(object):

    def __init__(self, return_value=None):
        self.count = 0
        self.return_value = return_value

    def __call__(self, *argv, **kwargs):
        self.count += 1
        return self.return_value
