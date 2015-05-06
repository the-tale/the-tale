# coding: utf-8
import mock

from dext.common.utils.urls import url

from the_tale.common.utils import testcase

from the_tale.common import postponed_tasks

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.middleware import RegistrationMiddleware, FirstTimeVisitMiddleware
from the_tale.accounts.conf import accounts_settings
from the_tale.accounts.postponed_tasks import RegistrationTask

from the_tale.game.logic import create_test_map


class RegistrationMiddlewareTests(testcase.TestCase):

    def setUp(self):
        super(RegistrationMiddlewareTests, self).setUp()
        create_test_map()
        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)

        self.middleware = RegistrationMiddleware()

        self.referral_link = '/?%s=%d' % (accounts_settings.REFERRAL_URL_ARGUMENT, self.account.id)
        self.action_link = '/?%s=action' % accounts_settings.ACTION_URL_ARGUMENT

    def test_handle_registration__not_anonymous(self):
        with mock.patch('the_tale.accounts.middleware.login_user') as login_user:
            result = self.middleware.handle_registration(self.make_request_html('/',
                                                                                session={accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY: 666},
                                                                                user=self.account._model))

        self.assertTrue(result.is_NOT_ANONYMOUS)
        self.assertEqual(login_user.call_count, 0)

    def test_handle_registration__no_data_in_session(self):
        with mock.patch('the_tale.accounts.middleware.login_user') as login_user:
            result = self.middleware.handle_registration(self.make_request_html('/'))

        self.assertTrue(result.is_NO_TASK_ID)
        self.assertEqual(login_user.call_count, 0)

    def test_handle_registration__no_task(self):
        with mock.patch('the_tale.accounts.middleware.login_user') as login_user:
            result = self.middleware.handle_registration(self.make_request_html('/', session={accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY: 666}))

        self.assertTrue(result.is_TASK_NOT_FOUND)
        self.assertEqual(login_user.call_count, 0)

    def test_handle_registration__task_not_processed(self):
        registration_task = RegistrationTask(account_id=None, referer=None, referral_of_id=None, action_id=None)
        task = postponed_tasks.PostponedTaskPrototype.create(registration_task)

        with mock.patch('the_tale.accounts.middleware.login_user') as login_user:
            result = self.middleware.handle_registration(self.make_request_html('/', session={accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY: task.id}))

        self.assertTrue(result.is_TASK_NOT_PROCESSED)
        self.assertEqual(login_user.call_count, 0)

    def test_handle_registration__task_processed(self):
        # self.request_login('test_user@test.com')

        registration_task = RegistrationTask(account_id=None, referer=None, referral_of_id=None, action_id=None)
        task = postponed_tasks.PostponedTaskPrototype.create(registration_task)
        task.process(logger=mock.Mock)

        with mock.patch('the_tale.accounts.middleware.login_user') as login_user:
            result = self.middleware.handle_registration(self.make_request_html('/', session={accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY: task.id}))

        self.assertTrue(result.is_USER_LOGINED)
        self.assertEqual(login_user.call_count, 1)


    def test_handle_referer__not_anonymous(self):
        result = self.middleware.handle_referer(self.make_request_html('/', user=self.account._model, meta={'HTTP_REFERER': 'example.com'}))
        self.assertTrue(result.is_NOT_ANONYMOUS)

    def test_handle_referer__no_referer(self):
        result = self.middleware.handle_referer(self.make_request_html('/'))
        self.assertTrue(result.is_NO_REFERER)

    def test_handle_referer__already_saved(self):
        result = self.middleware.handle_referer(self.make_request_html('/',
                                                                       session={accounts_settings.SESSION_REGISTRATION_REFERER_KEY: 'example.com'},
                                                                       meta={'HTTP_REFERER': 'example.com'}))
        self.assertTrue(result.is_ALREADY_SAVED)

    def test_handle_referer__saved(self):
        result = self.middleware.handle_referer(self.make_request_html('/', meta={'HTTP_REFERER': 'example.com'}))
        self.assertTrue(result.is_SAVED)


    def test_handle_referral__not_anonymous(self):
        result = self.middleware.handle_referral(self.make_request_html(self.referral_link, user=self.account._model))
        self.assertTrue(result.is_NOT_ANONYMOUS)

    def test_handle_referral__no_referral(self):
        result = self.middleware.handle_referral(self.make_request_html('/'))
        self.assertTrue(result.is_NO_REFERRAL)

    def test_handle_referral__referral_already_in_session(self):
        result = self.middleware.handle_referral(self.make_request_html(self.referral_link,
                                                                       session={accounts_settings.SESSION_REGISTRATION_REFERRAL_KEY: 666}))
        self.assertTrue(result.is_ALREADY_SAVED)

    def test_handle_referral__referral_not_in_session(self):
        result = self.middleware.handle_referral(self.make_request_html(self.referral_link))
        self.assertTrue(result.is_SAVED)


    def test_handle_action__not_anonymous(self):
        result = self.middleware.handle_action(self.make_request_html(self.action_link, user=self.account._model))
        self.assertTrue(result.is_NOT_ANONYMOUS)

    def test_handle_action__no_action(self):
        result = self.middleware.handle_action(self.make_request_html('/'))
        self.assertTrue(result.is_NO_ACTION)

    def test_handle_action__action_already_in_session(self):
        result = self.middleware.handle_action(self.make_request_html(self.action_link,
                                                                      session={accounts_settings.SESSION_REGISTRATION_ACTION_KEY: 'action2'}))
        self.assertTrue(result.is_ALREADY_SAVED)

    def test_handle_action__action_not_in_session(self):
        result = self.middleware.handle_action(self.make_request_html(self.action_link))
        self.assertTrue(result.is_SAVED)



class FirstTimeVisitMiddlewareTests(testcase.TestCase):

    def setUp(self):
        super(FirstTimeVisitMiddlewareTests, self).setUp()

        create_test_map()

        self.account = self.accounts_factory.create_account()

        self.middleware = FirstTimeVisitMiddleware()

        self.requested_url = url('accounts:show', self.account.id)


    def test_visit_chain(self):
        response = self.client.get(self.requested_url)

        self.assertEqual(response.client.session.get(accounts_settings.SESSION_FIRST_TIME_VISIT_VISITED_KEY), True)
        self.assertEqual(response.client.session.get(accounts_settings.SESSION_FIRST_TIME_VISIT_KEY), True)

        response = self.client.get(self.requested_url)

        self.assertEqual(response.client.session.get(accounts_settings.SESSION_FIRST_TIME_VISIT_VISITED_KEY), True)
        self.assertEqual(response.client.session.get(accounts_settings.SESSION_FIRST_TIME_VISIT_KEY), False)

        response = self.client.get(self.requested_url)

        self.assertEqual(response.client.session.get(accounts_settings.SESSION_FIRST_TIME_VISIT_VISITED_KEY), True)
        self.assertEqual(response.client.session.get(accounts_settings.SESSION_FIRST_TIME_VISIT_KEY), False)
