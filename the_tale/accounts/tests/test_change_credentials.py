# coding: utf-8

import datetime

import mock

from the_tale.common.utils import testcase
from django.contrib.auth import authenticate as django_authenticate

from the_tale.common.utils.fake import FakeLogger, FakeWorkerCommand

from the_tale.post_service.models import Message

from the_tale.accounts.prototypes import AccountPrototype, ChangeCredentialsTaskPrototype
from the_tale.accounts.models import CHANGE_CREDENTIALS_TASK_STATE
from the_tale.accounts.logic import register_user
from the_tale.accounts import exceptions

from the_tale.game.logic import create_test_map

def raise_exception(*argv, **kwargs): raise Exception('unknown error')

class TestChangeCredentialsTask(testcase.TestCase):

    def setUp(self):
        super(TestChangeCredentialsTask, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.test_account = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('fast_user')
        self.fast_account = AccountPrototype.get_by_id(account_id)

    def test_create(self):
        task = ChangeCredentialsTaskPrototype.create(self.test_account, new_email='test_user@test.ru', new_password='222222', new_nick='test_nick')

        self.assertTrue(task._model.new_password != '222222')
        self.assertTrue(task._model.new_nick == 'test_nick')
        self.assertEqual(task.state, CHANGE_CREDENTIALS_TASK_STATE.WAITING)
        self.assertEqual(task.account.id, self.test_account.id)
        self.assertTrue(not AccountPrototype.get_by_id(self.test_account.id).is_fast)

        task_duplicate = ChangeCredentialsTaskPrototype.get_by_uuid(task.uuid)

        self.assertEqual(task.id, task_duplicate.id)

    def test_create_exceptions(self):
        self.assertRaises(exceptions.MailNotSpecifiedForFastAccountError, ChangeCredentialsTaskPrototype.create, self.fast_account,  new_password='222222', new_nick='test_nick')
        self.assertRaises(exceptions.PasswordNotSpecifiedForFastAccountError, ChangeCredentialsTaskPrototype.create, self.fast_account, new_email='fast_user@test.com', new_nick='test_nick')
        self.assertRaises(exceptions.NickNotSpecifiedForFastAccountError, ChangeCredentialsTaskPrototype.create, self.fast_account, new_password='222222', new_email='fast_user@test.com')

    def test_email_changed(self):
        task = ChangeCredentialsTaskPrototype.create(self.test_account, new_email='test_user@test.ru')
        self.assertTrue(task.email_changed)

        task = ChangeCredentialsTaskPrototype.create(self.test_account, new_password='222222')
        self.assertTrue(not task.email_changed)

        task = ChangeCredentialsTaskPrototype.create(self.test_account, new_email='test_user@test.com')
        self.assertTrue(not task.email_changed)

    def test_change_credentials(self):
        task = ChangeCredentialsTaskPrototype.create(self.fast_account, new_email='fast_user@test.ru', new_password='222222', new_nick='test_nick')

        self.assertTrue(AccountPrototype.get_by_id(self.fast_account.id).is_fast)

        with mock.patch('the_tale.game.workers.environment.workers_environment.supervisor.cmd_update_hero_with_account_data') as fake_cmd:
            postponed_task = task.change_credentials()

        self.assertNotEqual(postponed_task, None)
        self.assertEqual(fake_cmd.call_count, 0)

    def test_change_credentials_password(self):
        task = ChangeCredentialsTaskPrototype.create(self.test_account, new_password='222222')
        postponed_task = task.change_credentials()

        self.assertNotEqual(postponed_task, None)
        self.assertEqual(Message.objects.all().count(), 0)

    def test_change_credentials_nick(self):
        task = ChangeCredentialsTaskPrototype.create(self.test_account, new_nick='test_nick')

        fake_cmd = FakeWorkerCommand()

        with mock.patch('the_tale.game.workers.environment.workers_environment.supervisor.cmd_update_hero_with_account_data') as fake_cmd:
            postponed_task = task.change_credentials()

        self.assertNotEqual(postponed_task, None)

        self.assertEqual(Message.objects.all().count(), 0)

        self.assertEqual(fake_cmd.call_count, 0)

        self.assertEqual(django_authenticate(nick='test_nick', password='111111'), None)

    def test_change_credentials_email(self):
        task = ChangeCredentialsTaskPrototype.create(self.test_account, new_email='test_user@test.ru')
        postponed_task = task.change_credentials()
        self.assertNotEqual(postponed_task, None)
        self.assertEqual(Message.objects.all().count(), 0)

    def test_request_email_confirmation_exceptions(self):
        task = ChangeCredentialsTaskPrototype.create(self.test_account, new_password='222222')
        self.assertRaises(exceptions.NewEmailNotSpecifiedError, task.request_email_confirmation)

    def test_request_email_confirmation(self):
        task = ChangeCredentialsTaskPrototype.create(self.test_account, new_email='test_user@test.ru')
        task.request_email_confirmation()
        self.assertEqual(Message.objects.all().count(), 1)

        task = ChangeCredentialsTaskPrototype.create(self.fast_account, new_email='fast_user@test.com', new_password='222222', new_nick='test_nick')
        task.request_email_confirmation()
        self.assertEqual(Message.objects.all().count(), 2)

    def test_process_completed_state(self):
        task = ChangeCredentialsTaskPrototype.create(self.test_account, new_email='test_user@test.ru')
        task._model.state = CHANGE_CREDENTIALS_TASK_STATE.PROCESSED
        task.process(FakeLogger())
        self.assertEqual(task._model.state, CHANGE_CREDENTIALS_TASK_STATE.PROCESSED)

        task._model.state = CHANGE_CREDENTIALS_TASK_STATE.UNPROCESSED
        task.process(FakeLogger())
        self.assertEqual(task._model.state, CHANGE_CREDENTIALS_TASK_STATE.UNPROCESSED)

        task._model.state = CHANGE_CREDENTIALS_TASK_STATE.ERROR
        task.process(FakeLogger())
        self.assertEqual(task._model.state, CHANGE_CREDENTIALS_TASK_STATE.ERROR)

    def test_process_duplicated_email(self):
        register_user('duplicated_user', 'duplicated@test.com', '111111')
        task = ChangeCredentialsTaskPrototype.create(self.test_account, new_email='duplicated@test.com')
        task._model.state = CHANGE_CREDENTIALS_TASK_STATE.EMAIL_SENT
        task.process(FakeLogger())
        self.assertEqual(task._model.state, CHANGE_CREDENTIALS_TASK_STATE.ERROR)


    def test_process_timeout(self):
        task = ChangeCredentialsTaskPrototype.create(self.test_account, new_email='test_user@test.ru')
        task._model.created_at = datetime.datetime.fromtimestamp(0)
        task.process(FakeLogger())
        self.assertEqual(task.state, CHANGE_CREDENTIALS_TASK_STATE.TIMEOUT)
        self.assertEqual(task._model.comment, 'timeout')
        self.assertEqual(django_authenticate(nick='test_user', password='111111').id, task.account.id)

    def test_process_waiting_and_email_confirmation(self):
        task = ChangeCredentialsTaskPrototype.create(self.test_account, new_email='test_user@test.ru')
        task.process(FakeLogger())
        self.assertEqual(task.state, CHANGE_CREDENTIALS_TASK_STATE.EMAIL_SENT)
        self.assertEqual(Message.objects.all().count(), 1)
        self.assertEqual(django_authenticate(nick='test_user', password='111111').id, task.account.id)

    def test_process_waiting_and_password_change(self):
        task = ChangeCredentialsTaskPrototype.create(self.test_account, new_password='222222')
        postponed_task = task.process(FakeLogger())
        self.assertEqual(task.state, CHANGE_CREDENTIALS_TASK_STATE.CHANGING)
        self.assertNotEqual(postponed_task, None)
        self.assertEqual(django_authenticate(nick='test_user', password='111111').id, task.account.id)

    def test_process_waiting_and_nick_change(self):
        task = ChangeCredentialsTaskPrototype.create(self.test_account, new_nick='test_nick')
        postponed_task = task.process(FakeLogger())
        self.assertEqual(task.state, CHANGE_CREDENTIALS_TASK_STATE.CHANGING)
        self.assertNotEqual(postponed_task, None)
        self.assertEqual(django_authenticate(nick='test_user', password='111111').id, task.account.id)

    def test_process_email_sent(self):
        task = ChangeCredentialsTaskPrototype.create(self.test_account, new_email='test_user@test.ru', new_password='222222')
        postponed_task = task.process(FakeLogger())
        self.assertEqual(postponed_task, None)
        self.assertEqual(task.state, CHANGE_CREDENTIALS_TASK_STATE.EMAIL_SENT)
        self.assertEqual(Message.objects.all().count(), 1)
        self.assertEqual(django_authenticate(nick='test_user', password='111111').id, task.account.id)
        self.assertEqual(django_authenticate(nick='test_user', password='222222'), None)

        postponed_task = task.process(FakeLogger())
        self.assertEqual(task.state, CHANGE_CREDENTIALS_TASK_STATE.CHANGING)
        self.assertNotEqual(postponed_task, None)

    @mock.patch('the_tale.post_service.message_handlers.ChangeEmailNotificationHandler', raise_exception)
    def test_process_error(self):
        task = ChangeCredentialsTaskPrototype.create(self.test_account, new_email='test_user@test.ru', new_password='222222')
        task.process(FakeLogger())
        self.assertEqual(task.state, CHANGE_CREDENTIALS_TASK_STATE.ERROR)
        self.assertEqual(Message.objects.all().count(), 0)
