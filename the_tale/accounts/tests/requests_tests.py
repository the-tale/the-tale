# coding: utf-8
from django.test import TestCase, client
from django.core.urlresolvers import reverse

from dext.utils import s11n

from common.utils.fake import FakeLogger

from accounts.logic import register_user
from accounts.models import RegistrationTask, REGISTRATION_TASK_STATE
from accounts.prototypes import RegistrationTaskPrototype

from game.logic import create_test_map

class TestRequests(TestCase):

    def setUp(self):
        create_test_map()
        register_user('test_user', 'test_user@test.com', '111111')
        self.client = client.Client()

    def login(self, email, password):
        response = self.client.post(reverse('accounts:login'), {'email': email, 'password': password})
        self.assertEqual(response.status_code, 200)

    def test_introduction_page(self):
        response = self.client.get(reverse('accounts:introduction'))
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_after_login(self):
        self.login('test_user@test.com', '111111')
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 302)

    def test_login_command(self):
        self.login('test_user@test.com', '111111')

    def test_logout_command(self):
        response = self.client.post(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('application/json' in response['Content-Type'])
        self.assertEqual(s11n.from_json(response.content), {'status': 'ok'})

        response = self.client.get(reverse('accounts:logout'))
        self.assertTrue('text/html' in response['Content-Type'])
        self.assertEqual(response.status_code, 302)


class TestRegistrationRequests(TestCase):

    def setUp(self):
        create_test_map()
        register_user('test_user', 'test_user@test.com', '111111')
        self.client = client.Client()


    def test_fast_registration_processing(self):
        response = self.client.post(reverse('accounts:fast_registration'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content), {'status': 'processing',
                                                            'status_url': reverse('accounts:fast_registration_status')})
        self.assertEqual(RegistrationTask.objects.all().count(), 1)

    def test_fast_registration_for_logged_in_user(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.post(reverse('accounts:fast_registration'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content)['status'], 'error')

    def test_fast_registration_second_request(self):
        response = self.client.post(reverse('accounts:fast_registration'))
        response = self.client.post(reverse('accounts:fast_registration'))
        self.assertEqual(s11n.from_json(response.content)['status'], 'error')
        self.assertEqual(RegistrationTask.objects.all().count(), 1)

    def test_fast_registration_status_after_login(self):
        response = self.client.post(reverse('accounts:fast_registration'))
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.get(reverse('accounts:fast_registration_status'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content), {'status': 'ok'})

    def test_fast_registration_status_without_registration(self):
        response = self.client.get(reverse('accounts:fast_registration_status'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content)['status'], 'error')

    def test_fast_registration_status_waiting(self):
        response = self.client.post(reverse('accounts:fast_registration'))
        response = self.client.get(reverse('accounts:fast_registration_status'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content), {'status': 'processing',
                                                            'status_url': reverse('accounts:fast_registration_status')})

    def test_fast_registration_status_timeout(self):
        response = self.client.post(reverse('accounts:fast_registration'))

        task = RegistrationTask.objects.all()[0]
        task.state = REGISTRATION_TASK_STATE.UNPROCESSED
        task.save()

        response = self.client.get(reverse('accounts:fast_registration_status'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content)['status'], 'error')

    def test_fast_registration_status_error(self):
        response = self.client.post(reverse('accounts:fast_registration'))

        task = RegistrationTask.objects.all()[0]
        task.state = REGISTRATION_TASK_STATE.ERROR
        task.save()

        response = self.client.get(reverse('accounts:fast_registration_status'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content)['status'], 'error')


    def test_fast_registration_status_ok(self):
        response = self.client.post(reverse('accounts:fast_registration'))

        task_model = RegistrationTask.objects.all()[0]
        task = RegistrationTaskPrototype.get_by_id(task_model.id)
        task.process(FakeLogger())

        response = self.client.get(reverse('accounts:fast_registration_status'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content), {'status': 'ok'})


class TestProfileRequests(TestCase):

    def setUp(self):
        create_test_map()
        register_user('test_user', 'test_user@test.com', '111111')
        self.client = client.Client()

    def test_profile_page_unlogined(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)

    def test_profile_page_logined(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)

    # def test_profile_edited(self):
    #     response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
    #     response = self.client.get(reverse('accounts:profile_edited'))
    #     self.assertEqual(response.status_code, 200)
