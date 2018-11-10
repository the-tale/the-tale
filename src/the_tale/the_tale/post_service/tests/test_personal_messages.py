
import smart_imports

smart_imports.all()


class PersonalMessagesTests(utils_testcase.TestCase):

    def setUp(self):
        super(PersonalMessagesTests, self).setUp()

        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        personal_messages_logic.send_message(self.account_1.id, [self.account_2.id], 'test text')

        self.message = prototypes.MessagePrototype.get_priority_message()

    def test_register_message(self):
        self.assertEqual(models.Message.objects.all().count(), 1)

    def test_no_subscription(self):
        self.account_2.personal_messages_subscription = False
        self.account_2.save()

        self.assertEqual(len(django_mail.outbox), 0)
        self.message.process()
        self.assertTrue(self.message.state.is_PROCESSED)
        self.assertEqual(len(django_mail.outbox), 0)

    def test_subscription(self):
        self.assertEqual(len(django_mail.outbox), 0)
        self.message.process()
        self.assertTrue(self.message.state.is_PROCESSED)
        self.assertEqual(len(django_mail.outbox), 1)
        self.assertEqual(django_mail.outbox[0].to, [self.account_2.email])

        self.assertTrue(self.account_1.nick in django_mail.outbox[0].body)
        self.assertFalse(self.account_2.nick in django_mail.outbox[0].body)
        self.assertTrue('test text' in django_mail.outbox[0].body)
        self.assertTrue(django_settings.SITE_URL in django_mail.outbox[0].body)

        self.assertTrue(self.account_1.nick in django_mail.outbox[0].alternatives[0][0])
        self.assertFalse(self.account_2.nick in django_mail.outbox[0].alternatives[0][0])
        self.assertTrue('test text' in django_mail.outbox[0].alternatives[0][0])
        self.assertTrue(django_settings.SITE_URL in django_mail.outbox[0].alternatives[0][0])

    def test_mail_send__to_system_user(self):
        models.Message.objects.all().delete()

        personal_messages_logic.send_message(self.account_1.id, [accounts_logic.get_system_user().id], 'test text')

        message = prototypes.MessagePrototype.get_priority_message()

        self.assertEqual(len(django_mail.outbox), 0)
        message.process()
        self.assertTrue(message.state.is_PROCESSED)
        self.assertEqual(len(django_mail.outbox), 0)
