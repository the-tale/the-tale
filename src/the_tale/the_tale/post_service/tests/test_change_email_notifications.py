
import smart_imports

smart_imports.all()


class ChangeEmailNotificationTests(utils_testcase.TestCase):

    def setUp(self):
        super(ChangeEmailNotificationTests, self).setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

    def create_task_and_message(self, account, new_nick):
        task = accounts_prototypes.ChangeCredentialsTaskPrototype.create(account=account,
                                                                         new_email='%s@test.com' % new_nick,
                                                                         new_password='111111',
                                                                         new_nick=new_nick)
        task.request_email_confirmation()

        return task, prototypes.MessagePrototype.get_priority_message()

    def test_create_message(self):
        self.create_task_and_message(self.account, 'user_1_new')
        self.assertEqual(models.Message.objects.all().count(), 1)

    def test_mail_send(self):
        task, message = self.create_task_and_message(self.account, 'user_1_new')
        self.assertEqual(len(django_mail.outbox), 0)
        message.process()
        self.assertTrue(message.state.is_PROCESSED)
        self.assertEqual(len(django_mail.outbox), 1)
        self.assertEqual(django_mail.outbox[0].to, ['user_1_new@test.com'])

        self.assertTrue(task.uuid in django_mail.outbox[0].body)
        self.assertTrue(task.uuid in django_mail.outbox[0].alternatives[0][0])

    def test_mail_send__to_system_user(self):
        task, message = self.create_task_and_message(accounts_logic.get_system_user(), 'user_1_new')
        self.assertEqual(len(django_mail.outbox), 0)
        message.process()
        self.assertTrue(message.state.is_PROCESSED)
        self.assertEqual(len(django_mail.outbox), 0)

    def test_mail_send_for_fast_account(self):
        account_2 = self.accounts_factory.create_account()

        task, message = self.create_task_and_message(account_2, 'user_2_new')

        self.assertEqual(len(django_mail.outbox), 0)

        message = prototypes.MessagePrototype.get_priority_message()
        message.process()

        self.assertTrue(message.state.is_PROCESSED)
        self.assertEqual(len(django_mail.outbox), 1)
        self.assertEqual(django_mail.outbox[0].to, ['user_2_new@test.com'])

        self.assertTrue(task.uuid in django_mail.outbox[0].body)
        self.assertTrue(task.uuid in django_mail.outbox[0].alternatives[0][0])
