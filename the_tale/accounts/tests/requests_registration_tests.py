# coding: utf-8

from django.test import client
from django.core.urlresolvers import reverse

from common.utils.fake import FakeLogger
from common.utils.testcase import TestCase

from accounts.logic import register_user
from accounts.models import RegistrationTask, REGISTRATION_TASK_STATE
from accounts.prototypes import RegistrationTaskPrototype

from game.logic import create_test_map

class RequestsRegistrationTests(TestCase):

    def setUp(self):
        create_test_map()
        register_user('test_user', 'test_user@test.com', '111111')
        self.client = client.Client()

    def test_fast_registration_processing(self):
        response = self.client.post(reverse('accounts:registration:fast'))
        self.assertEqual(response.status_code, 200)
        self.check_ajax_processing(response, reverse('accounts:registration:fast-status'))
        self.assertEqual(RegistrationTask.objects.all().count(), 1)

    def test_fast_registration_for_logged_in_user(self):
        self.request_login('test_user@test.com')
        response = self.client.post(reverse('accounts:registration:fast'))
        self.check_ajax_error(response, 'accounts.registration.fast.already_registered')

    def test_fast_registration_second_request(self):
        response = self.client.post(reverse('accounts:registration:fast'))
        response = self.client.post(reverse('accounts:registration:fast'))
        self.check_ajax_error(response, 'accounts.registration.fast.is_processing')
        self.assertEqual(RegistrationTask.objects.all().count(), 1)

    def test_fast_registration_second_request_after_error(self):
        response = self.client.post(reverse('accounts:registration:fast'))

        task = RegistrationTask.objects.all().order_by('id')[0]
        task.state = REGISTRATION_TASK_STATE.UNPROCESSED
        task.save()
        response = self.client.post(reverse('accounts:registration:fast'))
        self.check_ajax_processing(response, reverse('accounts:registration:fast-status'))
        self.assertEqual(RegistrationTask.objects.all().count(), 2)

        task = RegistrationTask.objects.all().order_by('id')[1]
        task.state = REGISTRATION_TASK_STATE.ERROR
        task.save()
        response = self.client.post(reverse('accounts:registration:fast'))
        self.check_ajax_processing(response, reverse('accounts:registration:fast-status'))
        self.assertEqual(RegistrationTask.objects.all().count(), 3)

        task = RegistrationTask.objects.all().order_by('id')[2]
        task.delete()
        response = self.client.post(reverse('accounts:registration:fast'))
        self.check_ajax_processing(response, reverse('accounts:registration:fast-status'))
        self.assertEqual(RegistrationTask.objects.all().count(), 3)

    def test_fast_registration_status_after_login(self):
        response = self.client.post(reverse('accounts:registration:fast'))
        self.request_login('test_user@test.com')
        response = self.client.get(reverse('accounts:registration:fast-status'))
        self.check_ajax_ok(response)

    def test_fast_registration_status_without_registration(self):
        response = self.client.get(reverse('accounts:registration:fast-status'))
        self.check_ajax_error(response, 'accounts.registration.fast_status.wrong_request')

    def test_fast_registration_status_waiting(self):
        response = self.client.post(reverse('accounts:registration:fast'))
        response = self.client.get(reverse('accounts:registration:fast-status'))
        self.check_ajax_processing(response, reverse('accounts:registration:fast-status'))

    def test_fast_registration_status_timeout(self):
        response = self.client.post(reverse('accounts:registration:fast'))

        task = RegistrationTask.objects.all()[0]
        task.state = REGISTRATION_TASK_STATE.UNPROCESSED
        task.save()

        response = self.client.get(reverse('accounts:registration:fast-status'))
        self.check_ajax_error(response, 'accounts.registration.fast_status.timeout')

    def test_fast_registration_status_error(self):
        response = self.client.post(reverse('accounts:registration:fast'))

        task = RegistrationTask.objects.all()[0]
        task.state = REGISTRATION_TASK_STATE.ERROR
        task.save()

        response = self.client.get(reverse('accounts:registration:fast-status'))
        self.check_ajax_error(response, 'accounts.registration.fast_status.error')

    def test_fast_registration_status_ok(self):
        response = self.client.post(reverse('accounts:registration:fast'))

        task_model = RegistrationTask.objects.all()[0]
        task = RegistrationTaskPrototype.get_by_id(task_model.id)
        task.process(FakeLogger())

        response = self.client.get(reverse('accounts:registration:fast-status'))
        self.check_ajax_ok(response)
