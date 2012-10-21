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

    def test_user_redirect(self):
        from django.contrib.auth import authenticate as django_authenticate
        from django.contrib.auth.models import User
        from accounts.prototypes import AccountPrototype
        from accounts.logic import register_user
        from game.logic import create_test_map

        # desinchronize account & user ids
        User.objects.create_user('fake-user')

        create_test_map()
        register_user('test_user', 'test_user@test.com', '111111')
        user = django_authenticate(username='test_user', password='111111')

        self.assertNotEqual(user.id, AccountPrototype(user.get_profile()).id)

        response = self.client.get(reverse('portal:users:show', args=[user.id]))
        self.assertRedirects(response, reverse('game:angels:show', args=[AccountPrototype(user.get_profile()).angel.id]), status_code=301, target_status_code=200)
