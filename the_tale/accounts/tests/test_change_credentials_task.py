# coding: utf-8
import mock

from dext.common.utils.urls import url

from django.contrib.auth import authenticate as django_authenticate

from the_tale.common.utils import testcase
from the_tale.common.postponed_tasks import POSTPONED_TASK_LOGIC_RESULT

from the_tale.accounts.prototypes import ChangeCredentialsTaskPrototype, AccountPrototype
from the_tale.accounts.postponed_tasks import ChangeCredentials, CHANGE_CREDENTIALS_STATE
from the_tale.accounts.logic import register_user

from the_tale.game.logic import create_test_map


class PostponedChangeCredentialsTaskTests(testcase.TestCase):

    def setUp(self):
        super(PostponedChangeCredentialsTaskTests, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)

        self.task = ChangeCredentialsTaskPrototype.create(self.account,
                                                          new_email='test_user@test.ru',
                                                          new_password='222222',
                                                          new_nick='test_nick',
                                                          relogin_required=True)

        self.postponed_task = ChangeCredentials(task_id=self.task.id)

    def test_create(self):
        self.assertEqual(self.postponed_task.processed_data, {'next_url': url('accounts:profile:edited')})
        self.assertEqual(self.postponed_task.task_id, self.task.id)
        self.assertTrue(self.postponed_task.state.is_UNPROCESSED)

    def test_serialization(self):
        self.assertEqual(self.postponed_task.serialize(), ChangeCredentials.deserialize(self.postponed_task.serialize()).serialize())

    def test_processed_view__simple(self):
        resource = mock.Mock()
        with mock.patch('the_tale.accounts.logic.force_login_user') as force_login_user:
            self.postponed_task.processed_view(resource)

        self.assertEqual(resource.account.id, self.account.id)
        self.assertEqual(force_login_user.call_count, 1)

    def test_processed_view__real(self):
        from the_tale.common.postponed_tasks import autodiscover
        autodiscover()

        self.assertEqual(self.task.process(logger=mock.Mock()), None) # sent mail
        postponed_taks = self.task.process(logger=mock.Mock()) # create task
        postponed_taks.process(logger=mock.Mock())
        self.check_ajax_ok(self.client.get(url('postponed-tasks:status', postponed_taks.id)))
        self.assertEqual(self.client.session['_auth_user_id'], self.account.id)

    def test_processed_view__real__without_relogin(self):
        from the_tale.common.postponed_tasks import autodiscover
        autodiscover()

        self.task._model.relogin_required = False
        self.task._model.save()

        self.assertEqual(self.task.process(logger=mock.Mock()), None) # sent mail
        postponed_taks = self.task.process(logger=mock.Mock()) # create task
        postponed_taks.process(logger=mock.Mock())
        self.check_ajax_ok(self.client.get(url('postponed-tasks:status', postponed_taks.id)))
        self.assertEqual(self.client.session.get('_auth_user_id'), None)

    def test_process__wrong_state(self):
        self.postponed_task.state = CHANGE_CREDENTIALS_STATE.PROCESSED
        self.assertEqual(self.postponed_task.process(main_task=mock.Mock()), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertTrue(self.postponed_task.state.is_WRONG_STATE)

    def test_process(self):
        self.assertEqual(self.postponed_task.process(main_task=mock.Mock()), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertTrue(self.postponed_task.state.is_PROCESSED)
        self.assertEqual(django_authenticate(nick='test_nick', password='222222').email, 'test_user@test.ru')
