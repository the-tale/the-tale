
import smart_imports

smart_imports.all()


class ResetPasswordTests(utils_testcase.TestCase):

    def setUp(self):
        super(ResetPasswordTests, self).setUp()

        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.reset_task = accounts_prototypes.ResetPasswordTaskPrototype.create(self.account_1)
        self.message = prototypes.MessagePrototype.get_priority_message()

    def test_register_message(self):
        self.assertEqual(models.Message.objects.all().count(), 1)

    def test_mail_send(self):
        self.assertEqual(len(django_mail.outbox), 0)
        self.message.process()
        self.assertTrue(self.message.state.is_PROCESSED)
        self.assertEqual(len(django_mail.outbox), 1)
        self.assertEqual(django_mail.outbox[0].to, [self.account_1.email])

        self.assertTrue(self.reset_task.uuid in django_mail.outbox[0].body)
        self.assertTrue(self.reset_task.uuid in django_mail.outbox[0].alternatives[0][0])

    def test_mail_send__to_system_user(self):
        models.Message.objects.all().delete()

        accounts_prototypes.ResetPasswordTaskPrototype.create(accounts_logic.get_system_user())
        message = prototypes.MessagePrototype.get_priority_message()

        self.assertEqual(len(django_mail.outbox), 0)
        message.process()
        self.assertTrue(message.state.is_PROCESSED)
        self.assertEqual(len(django_mail.outbox), 0)
