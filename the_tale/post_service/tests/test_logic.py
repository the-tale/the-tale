# coding: utf-8

import mock

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user, get_system_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.post_service import logic

from the_tale.game.logic import create_test_map


class SendMailTests(testcase.TestCase):

    SEND_ARGS = dict(subject=u'subject',
                     text_content='text_content',
                     html_content='html_content')

    def setUp(self):
        super(SendMailTests, self).setUp()

        create_test_map()

        register_user('user_1', 'user_1@test.com', '111111')
        self.account_1 = AccountPrototype.get_by_nick('user_1')

        register_user('user_2', 'user_2@test.com', '111111')
        self.account_2 = AccountPrototype.get_by_nick('user_2')

    def check_send_mail(self, accounts, result, call_count, send=None):
        if send is None:
            send = mock.Mock()

        with mock.patch('django.core.mail.EmailMultiAlternatives.send', send) as send_mock:
            self.assertEqual(logic.send_mail(accounts, **self.SEND_ARGS), result)

        self.assertEqual(send_mock.call_count, call_count)

    def test_no_fails(self):
        self.check_send_mail([self.account_1, self.account_2], result=True, call_count=2)

    def test_failed(self):
        self.check_send_mail([self.account_1, self.account_2], result=False, call_count=2, send=mock.Mock(side_effect=Exception('!')))

    def test_no_email(self):
        self.account_1.email = None
        self.check_send_mail([self.account_1, self.account_2], result=True, call_count=1)

    def test_system_user(self):
        self.check_send_mail([self.account_1, get_system_user(), self.account_2], result=True, call_count=2)

    def test_account(self):
        self.check_send_mail([self.account_1], result=True, call_count=1)

    def test_account_tuple__no_email(self):
        self.check_send_mail([(self.account_1, '')], result=True, call_count=0)

    def test_account_tuple(self):
        self.check_send_mail([(self.account_1, 'email@email.email')], result=True, call_count=1)
