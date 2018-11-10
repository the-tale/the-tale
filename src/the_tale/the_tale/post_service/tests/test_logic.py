
import smart_imports

smart_imports.all()


class SendMailTests(utils_testcase.TestCase):

    SEND_ARGS = dict(subject='subject',
                     text_content='text_content',
                     html_content='html_content')

    def setUp(self):
        super(SendMailTests, self).setUp()

        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

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
        self.check_send_mail([self.account_1, accounts_logic.get_system_user(), self.account_2], result=True, call_count=2)

    def test_account(self):
        self.check_send_mail([self.account_1], result=True, call_count=1)

    def test_account_tuple__no_email(self):
        self.check_send_mail([(self.account_1, '')], result=True, call_count=0)

    def test_account_tuple(self):
        self.check_send_mail([(self.account_1, 'email@email.email')], result=True, call_count=1)
