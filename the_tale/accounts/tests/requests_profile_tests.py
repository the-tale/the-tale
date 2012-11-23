# coding: utf-8
from django.test import client
from django.core.urlresolvers import reverse
from django.core import mail
from django.contrib.auth import authenticate as django_authenticate

from common.utils.fake import FakeLogger
from common.utils.testcase import TestCase
from common.postponed_tasks import PostponedTask, PostponedTaskPrototype

from accounts.logic import register_user, login_url

from game.logic import create_test_map

from accounts.models import CHANGE_CREDENTIALS_TASK_STATE, ChangeCredentialsTask
from accounts.prototypes import AccountPrototype


class ProfileRequestsTests(TestCase):

    def setUp(self):
        create_test_map()
        self.client = client.Client()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)

    def test_profile_page_unlogined(self):
        self.check_redirect(reverse('accounts:profile:show'), login_url(reverse('accounts:profile:show')))

    def test_profile_page_logined(self):
        self.request_login('test_user@test.com')
        response = self.client.get(reverse('accounts:profile:show'))
        self.assertEqual(response.status_code, 200)

    def test_profile_edited(self):
        self.request_login('test_user@test.com')
        response = self.client.get(reverse('accounts:profile:edited'))
        self.assertEqual(response.status_code, 200)

    def test_profile_confirm_email_request(self):
        self.request_login('test_user@test.com')
        response = self.client.get(reverse('accounts:profile:confirm-email-request'))
        self.assertEqual(response.status_code, 200)

    def test_profile_update_password(self):
        self.request_login('test_user@test.com')
        response = self.client.post(reverse('accounts:profile:update'), {'email': 'test_user@test.com', 'password': '222222', 'nick': 'test_user'})
        self.assertEqual(response.status_code, 200)
        self.check_ajax_ok(response, data={'next_url': reverse('accounts:profile:edited')})
        self.assertEqual(ChangeCredentialsTask.objects.all().count(), 1)
        self.assertEqual(ChangeCredentialsTask.objects.all()[0].state, CHANGE_CREDENTIALS_TASK_STATE.PROCESSED)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(django_authenticate(username='test_user', password='222222').id, self.account.user.id)

    def test_profile_update_nick(self):
        self.request_login('test_user@test.com')
        response = self.client.post(reverse('accounts:profile:update'), {'email': 'test_user@test.com', 'nick': 'test_nick'})
        self.assertEqual(response.status_code, 200)
        self.check_ajax_ok(response, data={'next_url': reverse('accounts:profile:edited')})
        self.assertEqual(ChangeCredentialsTask.objects.all().count(), 1)
        self.assertEqual(ChangeCredentialsTask.objects.all()[0].state, CHANGE_CREDENTIALS_TASK_STATE.PROCESSED)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(django_authenticate(username='test_nick', password='111111').id, self.account.user.id)

    def test_profile_update_email(self):
        self.request_login('test_user@test.com')
        response = self.client.post(reverse('accounts:profile:update'), {'email': 'test_user@test.ru', 'nick': 'test_nick'})
        self.assertEqual(response.status_code, 200)
        self.check_ajax_ok(response, data={'next_url': reverse('accounts:profile:confirm-email-request')})
        self.assertEqual(ChangeCredentialsTask.objects.all().count(), 1)
        self.assertEqual(ChangeCredentialsTask.objects.all()[0].state, CHANGE_CREDENTIALS_TASK_STATE.EMAIL_SENT)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(django_authenticate(username='test_user', password='111111').id, self.account.user.id)
        self.assertEqual(django_authenticate(username='test_user', password='111111').email, 'test_user@test.com')

    def test_profile_update_duplicate_email(self):
        register_user('duplicated_user', 'duplicated@test.com', '111111')
        self.request_login('test_user@test.com')
        response = self.client.post(reverse('accounts:profile:update'), {'nick': 'duplicated_user_2', 'email': 'duplicated@test.com'})
        self.check_ajax_error(response, 'accounts.profile.update.used_email')
        self.assertEqual(ChangeCredentialsTask.objects.all().count(), 0)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(django_authenticate(username='test_user', password='111111').id, self.account.user.id)
        self.assertEqual(django_authenticate(username='test_user', password='111111').email, 'test_user@test.com')

    def test_profile_update_duplicate_nick(self):
        register_user('duplicated_user', 'duplicated@test.com', '111111')
        self.request_login('test_user@test.com')
        response = self.client.post(reverse('accounts:profile:update'), {'nick': 'duplicated_user', 'email': 'duplicated_@test.com'})
        self.check_ajax_error(response, 'accounts.profile.update.used_nick')
        self.assertEqual(ChangeCredentialsTask.objects.all().count(), 0)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(django_authenticate(username='test_user', password='111111').id, self.account.user.id)
        self.assertEqual(django_authenticate(username='test_user', password='111111').email, 'test_user@test.com')

    def test_profile_update_fast_errors(self):
        response = self.client.post(reverse('accounts:registration:fast'))
        PostponedTaskPrototype(PostponedTask.objects.all()[0]).process(FakeLogger())

        response = self.client.post(reverse('accounts:profile:update'), {'email': 'test_user@test.ru'})
        self.check_ajax_error(response, 'accounts.profile.update.form_errors')

        response = self.client.post(reverse('accounts:profile:update'), {'password': '111111'})
        self.check_ajax_error(response, 'accounts.profile.update.form_errors')

        response = self.client.post(reverse('accounts:profile:update'), {'nick': 'test_nick'})
        self.check_ajax_error(response, 'accounts.profile.update.form_errors')

        response = self.client.post(reverse('accounts:profile:update'), {'email': 'test_user@test.ru', 'nick': 'test_nick'})
        self.check_ajax_error(response, 'accounts.profile.update.empty_fields')

        response = self.client.post(reverse('accounts:profile:update'), {'email': 'test_user@test.ru', 'password': '111111'})
        self.check_ajax_error(response, 'accounts.profile.update.form_errors')

        response = self.client.post(reverse('accounts:profile:update'), {'password': '111111', 'nick': 'test_nick'})
        self.check_ajax_error(response, 'accounts.profile.update.form_errors')

        self.assertEqual(ChangeCredentialsTask.objects.all().count(), 0)
        self.assertEqual(len(mail.outbox), 0)


    def test_profile_confirm_email(self):
        self.request_login('test_user@test.com')
        response = self.client.post(reverse('accounts:profile:update'), {'email': 'test_user@test.ru', 'nick': 'test_nick'})

        uuid = ChangeCredentialsTask.objects.all()[0].uuid

        response = self.client.get(reverse('accounts:profile:confirm-email')+'?uuid='+uuid)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ChangeCredentialsTask.objects.all().count(), 1)
        self.assertEqual(ChangeCredentialsTask.objects.all()[0].state, CHANGE_CREDENTIALS_TASK_STATE.PROCESSED)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(django_authenticate(username='test_nick', password='111111').email, 'test_user@test.ru')

    def test_fast_profile_confirm_email(self):
        response = self.client.post(reverse('accounts:registration:fast'))
        PostponedTaskPrototype(PostponedTask.objects.all()[0]).process(FakeLogger())

        response = self.client.post(reverse('accounts:profile:update'), {'email': 'test_user@test.ru', 'nick': 'test_nick', 'password': '123456'})

        uuid = ChangeCredentialsTask.objects.all()[0].uuid

        response = self.client.get(reverse('accounts:profile:confirm-email')+'?uuid='+uuid)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ChangeCredentialsTask.objects.all().count(), 1)
        self.assertEqual(ChangeCredentialsTask.objects.all()[0].state, CHANGE_CREDENTIALS_TASK_STATE.PROCESSED)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(django_authenticate(username='test_nick', password='123456').email, 'test_user@test.ru')


    def test_profile_confirm_email_for_unlogined(self):
        self.request_login('test_user@test.com')
        self.client.post(reverse('accounts:profile:update'), {'email': 'test_user@test.ru', 'nick': 'test_nick'})
        self.client.get(reverse('accounts:auth:logout'))

        uuid = ChangeCredentialsTask.objects.all()[0].uuid

        self.client.get(reverse('accounts:profile:confirm-email')+'?uuid='+uuid)

        # check if we loggined - there will be redirect from login page
        self.check_redirect(reverse('accounts:auth:login'), '/')

    def test_update_last_news_reminder_time(self):

        self.request_login('test_user@test.com')

        self.check_ajax_ok(self.client.post(reverse('accounts:profile:update-last-news-reminder-time')))

        self.assertTrue(self.account.last_news_remind_time < AccountPrototype.get_by_id(self.account.id).last_news_remind_time)
