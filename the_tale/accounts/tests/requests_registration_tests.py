# coding: utf-8

from django.test import client
from django.core.urlresolvers import reverse

from common.utils.testcase import TestCase
from common.postponed_tasks import PostponedTask, PostponedTaskPrototype, POSTPONED_TASK_STATE

from accounts.logic import register_user

from game.logic import create_test_map

class RequestsRegistrationTests(TestCase):

    def setUp(self):
        super(RequestsRegistrationTests, self).setUp()
        create_test_map()
        register_user('test_user', 'test_user@test.com', '111111')
        self.client = client.Client()

    def test_fast_registration_processing(self):
        response = self.client.post(reverse('accounts:registration:fast'))
        self.assertEqual(response.status_code, 200)
        task = PostponedTaskPrototype(model=PostponedTask.objects.all()[0])
        self.check_ajax_processing(response, task.status_url)
        self.assertEqual(PostponedTask.objects.all().count(), 1)
        self.assertEqual(task.internal_logic.referer, None)

    def test_fast_registration_processing__with_referer(self):
        referer = 'http://example.com/forum/post/1/'
        response = self.client.post(reverse('accounts:registration:fast'), HTTP_REFERER=referer)
        self.assertEqual(response.status_code, 200)
        task = PostponedTaskPrototype(model=PostponedTask.objects.all()[0])
        self.check_ajax_processing(response, task.status_url)
        self.assertEqual(PostponedTask.objects.all().count(), 1)
        self.assertEqual(task.internal_logic.referer, referer)

    def test_fast_registration_for_logged_in_user(self):
        self.request_login('test_user@test.com')
        response = self.client.post(reverse('accounts:registration:fast'))
        self.check_ajax_error(response, 'accounts.registration.fast.already_registered')

    def test_fast_registration_second_request(self):
        response = self.client.post(reverse('accounts:registration:fast'))
        task = PostponedTaskPrototype(model=PostponedTask.objects.all()[0])

        response = self.client.post(reverse('accounts:registration:fast'))

        self.check_ajax_processing(response, task.status_url)
        self.assertEqual(PostponedTask.objects.all().count(), 1)

    def test_fast_registration_second_request_after_error(self):
        response = self.client.post(reverse('accounts:registration:fast'))

        task = PostponedTaskPrototype(model=PostponedTask.objects.all()[0])
        task.state = POSTPONED_TASK_STATE.ERROR
        task.save()

        response = self.client.post(reverse('accounts:registration:fast'))

        task_2 = PostponedTaskPrototype(model=PostponedTask.objects.all()[1])

        self.check_ajax_processing(response, task_2.status_url)
        self.assertEqual(PostponedTask.objects.all().count(), 2)

        task_2.state = POSTPONED_TASK_STATE.ERROR
        task_2.save()

        response = self.client.post(reverse('accounts:registration:fast'))

        task_3 = PostponedTaskPrototype(model=PostponedTask.objects.all()[2])

        self.check_ajax_processing(response, task_3.status_url)
        self.assertEqual(PostponedTask.objects.all().count(), 3)

        task_3.remove()

        response = self.client.post(reverse('accounts:registration:fast'))

        task_4 = PostponedTaskPrototype(model=PostponedTask.objects.all()[2])

        self.check_ajax_processing(response, task_4.status_url)
        self.assertEqual(PostponedTask.objects.all().count(), 3)
