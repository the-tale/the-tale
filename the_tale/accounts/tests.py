# coding: utf-8
from django.contrib.auth.models import User
from django.test import TestCase, client
from django.core.urlresolvers import reverse

from dext.utils import s11n

from accounts.logic import register_user, REGISTER_USER_RESULT

from game.angels.prototypes import get_angel_by_model
from game.heroes.bag import SLOTS
from game.logic import create_test_map


class TestRegistration(TestCase):

    def setUp(self):
        create_test_map()

    def test_successfull_result(self):
        result, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        # test result
        self.assertEqual(result, REGISTER_USER_RESULT.OK)
        self.assertTrue(bundle_id is not None)

        #test basic structure
        user = User.objects.get(username='test_user')

        self.assertEqual(user.username, 'test_user')
        self.assertEqual(user.email, 'test_user@test.com')

        account = user.get_profile()

        angel = get_angel_by_model(account.angel)
        self.assertEqual(len(angel.heroes()), 1)

        hero = angel.heroes()[0]

        # test hero equipment
        self.assertEqual(hero.equipment.get(SLOTS.PANTS).id, 'default_pants')
        self.assertEqual(hero.equipment.get(SLOTS.BOOTS).id, 'default_boots')
        self.assertEqual(hero.equipment.get(SLOTS.PLATE).id, 'default_plate')
        self.assertEqual(hero.equipment.get(SLOTS.GLOVES).id, 'default_gloves')
        self.assertEqual(hero.equipment.get(SLOTS.HAND_PRIMARY).id, 'default_weapon')

        self.assertTrue(hero.equipment.get(SLOTS.HAND_SECONDARY) is None)
        self.assertTrue(hero.equipment.get(SLOTS.HELMET) is None)
        self.assertTrue(hero.equipment.get(SLOTS.SHOULDERS) is None)
        self.assertTrue(hero.equipment.get(SLOTS.CLOAK) is None)
        self.assertTrue(hero.equipment.get(SLOTS.AMULET) is None)
        self.assertTrue(hero.equipment.get(SLOTS.RINGS) is None)

    def test_duplicate_username(self):
        result, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.assertEqual(result, REGISTER_USER_RESULT.OK)
        self.assertTrue(bundle_id is not None)
        result, bundle_id = register_user('test_user', 'test_user2@test.com', '111111')
        self.assertEqual(result, REGISTER_USER_RESULT.DUPLICATE_USERNAME)
        self.assertTrue(bundle_id is None)

    def test_duplicate_email(self):
        result, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.assertEqual(result, REGISTER_USER_RESULT.OK)
        self.assertTrue(bundle_id is not None)
        result, bundle_id = register_user('test_user2', 'test_user@test.com', '111111')
        self.assertEqual(result, REGISTER_USER_RESULT.DUPLICATE_EMAIL)
        self.assertTrue(bundle_id is None)



class TestRequests(TestCase):

    def setUp(self):
        create_test_map()
        register_user('test_user', 'test_user@test.com', '111111')
        register_user('test_user2', 'test_user2@test.com', '111111')
        self.client = client.Client()


    def login(self, email, password):
        response = self.client.post(reverse('accounts:login'), {'email': email, 'password': password})
        self.assertEqual(response.status_code, 200)

    def test_registration_page(self):
        response = self.client.get(reverse('accounts:registration'))
        self.assertEqual(response.status_code, 200)

    def test_registration_page_after_login(self):
        self.login('test_user@test.com', '111111')
        response = self.client.get(reverse('accounts:registration'))
        self.assertEqual(response.status_code, 302)

    def test_login_page(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_after_login(self):
        self.login('test_user@test.com', '111111')
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 302)

    def test_login_command(self):
        self.login('test_user@test.com', '111111')

    def test_login_after_login(self):
        self.login('test_user@test.com', '111111')

    def test_logout_command(self):
        response = self.client.post(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('application/json' in response['Content-Type'])
        self.assertEqual(s11n.from_json(response.content), {'status': 'ok'})

        response = self.client.get(reverse('accounts:logout'))
        self.assertTrue('text/html' in response['Content-Type'])
        self.assertEqual(response.status_code, 302)
