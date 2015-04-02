# coding: utf-8
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate as django_authenticate

from dext.common.utils.urls import url

from the_tale.common.utils.fake import FakeLogger
from the_tale.common.utils.testcase import TestCase
from the_tale.common.postponed_tasks import PostponedTask, PostponedTaskPrototype

from the_tale.post_service.models import Message

from the_tale.accounts.logic import register_user, login_page_url

from the_tale.game.logic import create_test_map

from the_tale.accounts.models import ChangeCredentialsTask
from the_tale.accounts.prototypes import AccountPrototype, ChangeCredentialsTaskPrototype
from the_tale.accounts import relations

from the_tale.accounts.third_party.tests import helpers as third_party_helpers


class ProfileRequestsTests(TestCase, third_party_helpers.ThirdPartyTestsMixin):

    def setUp(self):
        super(ProfileRequestsTests, self).setUp()
        create_test_map()

        self.account = self.accounts_factory.create_account()
        self.account_nick = self.account.nick
        self.account_email = self.account.email

    def test_refuse_third_party__profile_page(self):
        self.request_third_party_token(account=self.account)
        self.check_html_ok(self.request_html(reverse('accounts:profile:show')), texts=['third_party.access_restricted'])

    def test_profile_page_unlogined(self):
        self.check_redirect(reverse('accounts:profile:show'), login_page_url(reverse('accounts:profile:show')))

    def test_profile_page__fast_account(self):
        self.request_login(self.account.email)

        self.account.is_fast = True
        self.account.save()

        texts = [('pgf-fast-account-help-block', 1),
                 ('pgf-fast-account-user-agreement-block', 1)]
        self.check_html_ok(self.request_html(reverse('accounts:profile:show')), texts=texts)

    def test_profile_page__normal_account(self):
        self.request_login(self.account.email)
        texts = [('pgf-fast-account-help-block', 0),
                 ('pgf-fast-account-user-agreement-block', 0)]
        self.check_html_ok(self.request_html(reverse('accounts:profile:show')), texts=texts)

    def test_profile_page_logined(self):
        self.request_login(self.account.email)
        response = self.client.get(reverse('accounts:profile:show'))
        self.assertEqual(response.status_code, 200)


    def test_refuse_third_party__profile_edited(self):
        self.request_third_party_token(account=self.account)
        self.check_html_ok(self.request_html(reverse('accounts:profile:edited')), texts=['third_party.access_restricted'])

    def test_profile_edited(self):
        self.request_login(self.account.email)
        response = self.client.get(reverse('accounts:profile:edited'))
        self.assertEqual(response.status_code, 200)

    def test_profile_confirm_email_request(self):
        self.request_login(self.account.email)
        response = self.client.get(reverse('accounts:profile:confirm-email-request'))
        self.assertEqual(response.status_code, 200)

    def test_refuse_third_party__confirm_email_request(self):
        self.request_third_party_token(account=self.account)
        self.check_html_ok(self.request_html(reverse('accounts:profile:confirm-email-request')), texts=['third_party.access_restricted'])

    def test_profile_update_password(self):
        self.request_login(self.account.email)
        response = self.client.post(reverse('accounts:profile:update'), {'email': self.account.email, 'password': '222222', 'nick': 'test_user'})
        self.assertEqual(response.status_code, 200)
        self.check_ajax_processing(response, PostponedTaskPrototype._db_get_object(0).status_url)
        self.assertEqual(ChangeCredentialsTask.objects.all().count(), 1)
        self.assertEqual(ChangeCredentialsTask.objects.all()[0].state, relations.CHANGE_CREDENTIALS_TASK_STATE.CHANGING)

    def test_refuse_third_party__update(self):
        self.request_third_party_token(account=self.account)
        self.check_ajax_error(self.client.post(reverse('accounts:profile:update'),
                                               {'email': self.account.email, 'password': '222222', 'nick': 'test_user'}), 'third_party.access_restricted')

    def test_profile_update_nick(self):
        self.request_login(self.account.email)
        response = self.client.post(reverse('accounts:profile:update'), {'email': self.account.email, 'nick': 'test_nick'})
        self.assertEqual(response.status_code, 200)
        self.check_ajax_processing(response, PostponedTaskPrototype._db_get_object(0).status_url)
        self.assertEqual(ChangeCredentialsTask.objects.all().count(), 1)
        self.assertEqual(ChangeCredentialsTask.objects.all()[0].state, relations.CHANGE_CREDENTIALS_TASK_STATE.CHANGING)

    def test_profile_update_nick__banned(self):
        self.request_login(self.account.email)
        self.account.ban_forum(1)

        with self.check_not_changed(ChangeCredentialsTask.objects.all().count):
            self.check_ajax_error(self.client.post(reverse('accounts:profile:update'),
                                                   {'email': self.account.email, 'nick': 'test_nick'}),
                                  'accounts.profile.update.banned')

    def test_profile_update_email(self):
        self.request_login(self.account.email)
        response = self.client.post(reverse('accounts:profile:update'), {'email': 'test_user@test.ru', 'nick': 'test_nick'})
        self.assertEqual(response.status_code, 200)
        self.check_ajax_ok(response, data={'next_url': reverse('accounts:profile:confirm-email-request')})
        self.assertEqual(ChangeCredentialsTask.objects.all().count(), 1)
        self.assertEqual(ChangeCredentialsTask.objects.all()[0].state, relations.CHANGE_CREDENTIALS_TASK_STATE.EMAIL_SENT)
        self.assertEqual(Message.objects.all().count(), 1)
        self.assertEqual(django_authenticate(nick=self.account_nick, password='111111').id, self.account.id)
        self.assertEqual(django_authenticate(nick=self.account_nick, password='111111').email, self.account_email)

    def test_profile_update_duplicate_email(self):
        register_user('duplicated_user', 'duplicated@test.com', '111111')
        self.request_login(self.account.email)
        response = self.client.post(reverse('accounts:profile:update'), {'nick': 'duplicated_user_2', 'email': 'duplicated@test.com'})
        self.check_ajax_error(response, 'accounts.profile.update.used_email')
        self.assertEqual(ChangeCredentialsTask.objects.all().count(), 0)
        self.assertEqual(Message.objects.all().count(), 0)
        self.assertEqual(django_authenticate(nick=self.account_nick, password='111111').id, self.account.id)
        self.assertEqual(django_authenticate(nick=self.account_nick, password='111111').email, self.account_email)

    def test_profile_update_duplicate_nick(self):
        register_user('duplicated_user', 'duplicated@test.com', '111111')
        self.request_login(self.account.email)
        response = self.client.post(reverse('accounts:profile:update'), {'nick': 'duplicated_user', 'email': 'duplicated_@test.com'})
        self.check_ajax_error(response, 'accounts.profile.update.used_nick')
        self.assertEqual(ChangeCredentialsTask.objects.all().count(), 0)
        self.assertEqual(Message.objects.all().count(), 0)
        self.assertEqual(django_authenticate(nick=self.account_nick, password='111111').id, self.account.id)
        self.assertEqual(django_authenticate(nick=self.account_nick, password='111111').email, self.account_email)

    def test_profile_update_fast_errors(self):
        response = self.client.post(reverse('accounts:registration:fast'))
        PostponedTaskPrototype(model=PostponedTask.objects.all()[0]).process(FakeLogger())

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
        self.assertEqual(Message.objects.all().count(), 0)


    def test_profile_confirm_email(self):
        self.request_login(self.account.email)
        self.client.post(reverse('accounts:profile:update'), {'email': 'test_user@test.ru', 'nick': 'test_nick'})
        self.assertEqual(PostponedTaskPrototype._model_class.objects.all().count(), 0)
        uuid = ChangeCredentialsTask.objects.all()[0].uuid

        response = self.client.get(reverse('accounts:profile:confirm-email')+'?uuid='+uuid)
        self.check_response_redirect(response, PostponedTaskPrototype._db_get_object(0).wait_url)

        self.assertEqual(ChangeCredentialsTask.objects.all().count(), 1)
        self.assertEqual(ChangeCredentialsTask.objects.all()[0].state, relations.CHANGE_CREDENTIALS_TASK_STATE.CHANGING)
        self.assertEqual(Message.objects.all().count(), 1)


    def test_refuse_third_party__confirm_email(self):
        self.request_login(self.account.email)
        self.client.post(reverse('accounts:profile:update'), {'email': 'test_user@test.ru', 'nick': 'test_nick'})
        self.assertEqual(PostponedTaskPrototype._model_class.objects.all().count(), 0)
        uuid = ChangeCredentialsTask.objects.all()[0].uuid

        self.request_third_party_token(account=self.account)
        self.check_ajax_error(self.client.get(reverse('accounts:profile:confirm-email')+'?uuid='+uuid), 'third_party.access_restricted')


    def test_fast_profile_confirm_email(self):
        self.client.post(reverse('accounts:registration:fast'))
        PostponedTaskPrototype(model=PostponedTask.objects.all()[0]).process(FakeLogger())

        self.client.post(reverse('accounts:profile:update'), {'email': 'test_user@test.ru', 'nick': 'test_nick', 'password': '123456'})
        self.assertEqual(Message.objects.all().count(), 1)

        uuid = ChangeCredentialsTask.objects.all()[0].uuid

        response = self.client.get(reverse('accounts:profile:confirm-email')+'?uuid='+uuid)
        self.check_response_redirect(response, PostponedTaskPrototype._db_get_object(1).wait_url)

        self.assertEqual(ChangeCredentialsTask.objects.all().count(), 1)
        self.assertEqual(ChangeCredentialsTask.objects.all()[0].state, relations.CHANGE_CREDENTIALS_TASK_STATE.CHANGING)

        self.assertEqual(django_authenticate(nick='test_nick', password='123456'), None)


    def test_profile_confirm_email_for_unlogined(self):
        self.request_login(self.account.email)
        self.client.post(reverse('accounts:profile:update'), {'email': 'test_user@test.ru', 'nick': 'test_nick'})
        self.request_logout()

        uuid = ChangeCredentialsTask.objects.all()[0].uuid

        response = self.client.get(reverse('accounts:profile:confirm-email')+'?uuid='+uuid)
        self.check_response_redirect(response, PostponedTaskPrototype._db_get_object(0).wait_url)

    def test_confirm_email__wrong_task(self):
        self.request_login(self.account.email)
        self.client.post(reverse('accounts:profile:update'), {'email': 'test_user@test.ru', 'nick': 'test_nick'})

        self.check_html_ok(self.client.get(url('accounts:profile:confirm-email', uuid='wronguuid'), texts=['pgf-change-credentials-wrong-link']))

    def test_confirm_email__already_processed(self):
        self.request_login(self.account.email)
        self.client.post(reverse('accounts:profile:update'), {'email': 'test_user@test.ru', 'nick': 'test_nick'})

        task = ChangeCredentialsTaskPrototype._db_get_object(0)
        task._model.state = relations.CHANGE_CREDENTIALS_TASK_STATE.PROCESSED
        task._model.save()

        self.check_html_ok(self.client.get(url('accounts:profile:confirm-email', uuid=task.uuid), texts=['pgf-change-credentials-already-processed']))

    def test_confirm_email__wrong_timeout(self):
        self.request_login(self.account.email)
        self.client.post(reverse('accounts:profile:update'), {'email': 'test_user@test.ru', 'nick': 'test_nick'})

        task = ChangeCredentialsTaskPrototype._db_get_object(0)
        task._model.state = relations.CHANGE_CREDENTIALS_TASK_STATE.TIMEOUT
        task._model.save()

        self.check_html_ok(self.client.get(url('accounts:profile:confirm-email', uuid=task.uuid), texts=['pgf-change-credentials-timeout']))

    def test_confirm_email__error_occured(self):
        self.request_login(self.account.email)
        self.client.post(reverse('accounts:profile:update'), {'email': 'test_user@test.ru', 'nick': 'test_nick'})

        task = ChangeCredentialsTaskPrototype._db_get_object(0)
        task._model.state = relations.CHANGE_CREDENTIALS_TASK_STATE.ERROR
        task._model.save()

        self.check_html_ok(self.client.get(url('accounts:profile:confirm-email', uuid=task.uuid), texts=['pgf-change-credentials-error']))


    def test_update_last_news_reminder_time_unlogined(self):
        self.check_ajax_error(self.client.post(reverse('accounts:profile:update-last-news-reminder-time')), 'common.login_required')


    def test_update_last_news_reminder_time(self):

        self.request_login(self.account.email)

        self.check_ajax_ok(self.client.post(reverse('accounts:profile:update-last-news-reminder-time')))

        self.assertTrue(self.account.last_news_remind_time < AccountPrototype.get_by_id(self.account.id).last_news_remind_time)


    def test_profile_update_settings__personal_messages(self):
        self.request_login(self.account.email)
        self.assertTrue(self.account.personal_messages_subscription)
        response = self.client.post(reverse('accounts:profile:update-settings'), {'personal_messages_subscription': False})
        self.assertFalse(AccountPrototype.get_by_id(self.account.id).personal_messages_subscription)
        self.check_ajax_ok(response, data={'next_url': reverse('accounts:profile:edited')})


    def test_profile_update_settings__bews(self):
        self.request_login(self.account.email)
        self.assertTrue(self.account.news_subscription)
        response = self.client.post(reverse('accounts:profile:update-settings'), {'news_subscription': False})
        self.assertFalse(AccountPrototype.get_by_id(self.account.id).news_subscription)
        self.check_ajax_ok(response, data={'next_url': reverse('accounts:profile:edited')})


    def test_profile_update_settings__description(self):
        self.request_login(self.account.email)
        self.assertEqual(self.account.description, u'')
        response = self.client.post(reverse('accounts:profile:update-settings'), {'description': 'new-description'})
        self.assertEqual(AccountPrototype.get_by_id(self.account.id).description, 'new-description')
        self.check_ajax_ok(response, data={'next_url': reverse('accounts:profile:edited')})
