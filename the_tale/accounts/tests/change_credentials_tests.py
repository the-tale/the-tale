# coding: utf-8
# coding: utf-8
import datetime

import mock

from django.test import TestCase
from django.contrib.auth import authenticate as django_authenticate
from django.core import mail

from common.utils.fake import FakeLogger

from accounts.prototypes import AccountPrototype, ChangeCredentialsTaskPrototype
from accounts.models import CHANGE_CREDENTIALS_TASK_STATE
from accounts.logic import register_user
from accounts.exceptions import AccountsException

from game.logic import create_test_map

def raise_exception(*argv, **kwargs): raise Exception('unknown error')

class TestChangeCredentialsTask(TestCase):

    def setUp(self):
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.test_account = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('fast_user')
        self.fast_account = AccountPrototype.get_by_id(account_id)

    def test_create(self):
        task = ChangeCredentialsTaskPrototype.create(self.test_account, new_email='test_user@test.ru', new_password='222222')

        self.assertTrue(task.model.new_password != '222222')
        self.assertEqual(task.state, CHANGE_CREDENTIALS_TASK_STATE.WAITING)
        self.assertEqual(task.account.id, self.test_account.id)

        task_duplicate = ChangeCredentialsTaskPrototype.get_by_uuid(task.uuid)

        self.assertEqual(task.id, task_duplicate.id)

    def test_create_exceptions(self):
        self.assertRaises(AccountsException, ChangeCredentialsTaskPrototype.create, self.fast_account,  new_password='222222')
        self.assertRaises(AccountsException, ChangeCredentialsTaskPrototype.create, self.fast_account,  new_email='fast_user@test.com')

    def test_email_changed(self):
        task = ChangeCredentialsTaskPrototype.create(self.test_account, new_email='test_user@test.ru')
        self.assertTrue(task.email_changed)

        task = ChangeCredentialsTaskPrototype.create(self.test_account, new_password='222222')
        self.assertTrue(not task.email_changed)

        task = ChangeCredentialsTaskPrototype.create(self.test_account, new_email='test_user@test.com')
        self.assertTrue(not task.email_changed)

    def test_change_credentials(self):
        task = ChangeCredentialsTaskPrototype.create(self.fast_account, new_email='fast_user@test.ru', new_password='222222')
        task.change_credentials()

        self.assertEqual(task.account.user.email, 'fast_user@test.ru')
        user = django_authenticate(username='fast_user', password='222222')
        self.assertEqual(user.id, task.account.user.id)

    def test_change_credentials_password(self):
        task = ChangeCredentialsTaskPrototype.create(self.test_account, new_password='222222')
        task.change_credentials()

        self.assertEqual(task.account.user.email, 'test_user@test.com')
        user = django_authenticate(username='test_user', password='222222')

        self.assertEqual(user.id, task.account.user.id)

    def test_change_credentials_email(self):
        task = ChangeCredentialsTaskPrototype.create(self.test_account, new_email='test_user@test.ru')
        task.change_credentials()

        self.assertEqual(task.account.user.email, 'test_user@test.ru')
        self.assertEqual(django_authenticate(username='test_user', password='111111').id, task.account.user.id)

    def test_request_email_confirmation_exceptions(self):
        task = ChangeCredentialsTaskPrototype.create(self.test_account, new_password='222222')
        self.assertRaises(AccountsException, task.request_email_confirmation)

    def test_request_email_confirmation(self):
        task = ChangeCredentialsTaskPrototype.create(self.test_account, new_email='test_user@test.ru')
        task.request_email_confirmation()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[-1].to, ['test_user@test.ru'])

        task = ChangeCredentialsTaskPrototype.create(self.fast_account, new_email='fast_user@test.com', new_password='222222')
        task.request_email_confirmation()
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[-1].to, ['fast_user@test.com'])

    def test_process_completed_state(self):
        task = ChangeCredentialsTaskPrototype.create(self.test_account, new_email='test_user@test.ru')
        task.model.state = CHANGE_CREDENTIALS_TASK_STATE.PROCESSED
        task.process(FakeLogger())
        self.assertEqual(task.model.state, CHANGE_CREDENTIALS_TASK_STATE.PROCESSED)

        task.model.state = CHANGE_CREDENTIALS_TASK_STATE.UNPROCESSED
        task.process(FakeLogger())
        self.assertEqual(task.model.state, CHANGE_CREDENTIALS_TASK_STATE.UNPROCESSED)

        task.model.state = CHANGE_CREDENTIALS_TASK_STATE.ERROR
        task.process(FakeLogger())
        self.assertEqual(task.model.state, CHANGE_CREDENTIALS_TASK_STATE.ERROR)

    def test_process_timeout(self):
        task = ChangeCredentialsTaskPrototype.create(self.test_account, new_email='test_user@test.ru')
        task.model.created_at = datetime.datetime.fromtimestamp(0)
        task.process(FakeLogger())
        self.assertEqual(task.state, CHANGE_CREDENTIALS_TASK_STATE.UNPROCESSED)
        self.assertEqual(task.model.comment, 'timeout')
        self.assertEqual(django_authenticate(username='test_user', password='111111').id, task.account.user.id)

    def test_process_waiting_and_email_confirmation(self):
        task = ChangeCredentialsTaskPrototype.create(self.test_account, new_email='test_user@test.ru')
        task.process(FakeLogger())
        self.assertEqual(task.state, CHANGE_CREDENTIALS_TASK_STATE.EMAIL_SENT)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(django_authenticate(username='test_user', password='111111').id, task.account.user.id)


    def test_process_waiting_and_password_change(self):
        task = ChangeCredentialsTaskPrototype.create(self.test_account, new_password='222222')
        task.process(FakeLogger())
        self.assertEqual(task.state, CHANGE_CREDENTIALS_TASK_STATE.PROCESSED)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(django_authenticate(username='test_user', password='222222').id, task.account.user.id)


    def test_process_email_sent(self):
        task = ChangeCredentialsTaskPrototype.create(self.test_account, new_email='test_user@test.ru', new_password='222222')
        task.process(FakeLogger())
        self.assertEqual(task.state, CHANGE_CREDENTIALS_TASK_STATE.EMAIL_SENT)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(django_authenticate(username='test_user', password='111111').id, task.account.user.id)
        self.assertEqual(django_authenticate(username='test_user', password='222222'), None)

        task.process(FakeLogger())
        self.assertEqual(task.state, CHANGE_CREDENTIALS_TASK_STATE.PROCESSED)
        user = django_authenticate(username='test_user', password='222222')
        self.assertEqual(user.id, task.account.user.id)
        self.assertEqual(user.email, 'test_user@test.ru')
        self.assertEqual(len(mail.outbox), 1)

    @mock.patch('accounts.prototypes.ChangeEmailNotification', raise_exception)
    def test_process_error(self):
        task = ChangeCredentialsTaskPrototype.create(self.test_account, new_email='test_user@test.ru', new_password='222222')
        task.process(FakeLogger())
        self.assertEqual(task.state, CHANGE_CREDENTIALS_TASK_STATE.ERROR)
        self.assertEqual(len(mail.outbox), 0)
