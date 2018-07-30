
import smart_imports

smart_imports.all()


class NewNewsTests(utils_testcase.TestCase):

    def setUp(self):
        super(NewNewsTests, self).setUp()
        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()
        self.account_3 = self.accounts_factory.create_account()

        self.news = news_logic.create_news(caption='news-caption', description='news-description', content='news-content')

        news_logic.send_mails(self.news)

        self.message = prototypes.MessagePrototype.get_priority_message()

        # enshure that system user exists
        accounts_logic.get_system_user()

    def test_register_message(self):
        self.assertEqual(models.Message.objects.all().count(), 1)

    def test_no_subscription(self):
        self.account_2.news_subscription = False
        self.account_2.save()

        with self.check_delta(django_mail.outbox.__len__, 2):
            self.message.process()

        self.assertTrue(self.message.state.is_PROCESSED)

        self.assertEqual(django_mail.outbox[0].to, [self.account_1.email])
        self.assertEqual(django_mail.outbox[1].to, [self.account_3.email])

        self.assertTrue(self.news.caption in django_mail.outbox[0].body)
        self.assertTrue(django_settings.SITE_URL in django_mail.outbox[0].body)

        self.assertTrue(self.news.caption in django_mail.outbox[0].alternatives[0][0])
        self.assertTrue(django_settings.SITE_URL in django_mail.outbox[0].alternatives[0][0])
